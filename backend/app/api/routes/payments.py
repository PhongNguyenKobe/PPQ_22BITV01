from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.api.routes.promotions import ensure_usable, promotion_discount
from app.core.config import settings
from app.core.seat_events import seat_events
from app.crud.booking import cleanup_expired_reservations
from app.crud.payment import generate_confirmation_number, generate_qr_code_data, validate_payment_amount
from app.crud.showtime import is_showtime_bookable
from app.db.session import get_db
from app.models.commerce import Booking, Payment, PaymentStatusHistory, Promotion
from app.models.user import User
from app.schemas.payment import CheckoutResponse, PaymentCheckoutRequest, PaymentCreate, PaymentRead
from app.services.vnpay import build_payment_url, verify_signature

router = APIRouter()


def _is_vnpay(method: str) -> bool:
    return "VNPAY" in method.upper().replace(" ", "")


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    return forwarded.split(",", 1)[0].strip() if forwarded else (request.client.host if request.client else "127.0.0.1")


def _provider_paid_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y%m%d%H%M%S").replace(
            tzinfo=timezone(timedelta(hours=7))
        ).astimezone(timezone.utc)
    except ValueError:
        return None


async def _owned_pending_booking(db: AsyncSession, booking_id: UUID, user_id: UUID) -> Booking:
    await cleanup_expired_reservations(db)
    booking = await db.get(Booking, booking_id)
    if booking is None or booking.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking is not payable")
    if booking.expires_at and booking.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking payment time has expired")
    if not is_showtime_bookable(booking.showtime):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket sales are closed for this showtime")
    return booking


async def _history(
    db: AsyncSession,
    payment: Payment,
    old_status: str | None,
    source: str,
    payload: dict,
    signature_valid: bool | None,
    note: str | None = None,
) -> None:
    db.add(PaymentStatusHistory(
        payment_id=payment.id,
        old_status=old_status,
        new_status=payment.status,
        source=source,
        response_code=payment.response_code,
        provider_status=payment.provider_status,
        signature_valid=signature_valid,
        note=note,
        raw_payload={str(key): str(value) for key, value in payload.items()},
    ))


async def _apply_vnpay_result(
    db: AsyncSession,
    payload: dict,
    source: str,
) -> tuple[Payment | None, str, str]:
    signature_valid = verify_signature(payload)
    result = await db.execute(
        select(Payment)
        .options(selectinload(Payment.booking))
        .where(Payment.provider_ref == str(payload.get("vnp_TxnRef", "")))
        .with_for_update()
    )
    payment = result.scalar_one_or_none()
    if payment is None:
        return None, "01", "Order not found"

    old_status = payment.status
    if old_status == "CANCELLED":
        await _history(db, payment, old_status, source, payload, signature_valid, "Payment request was cancelled by customer")
        await db.commit()
        return payment, "02", "Order already cancelled"

    try:
        amount_matches = Decimal(str(payload.get("vnp_Amount", "0"))) / Decimal("100") == payment.amount
    except Exception:
        amount_matches = False

    if not signature_valid:
        await _history(db, payment, old_status, source, payload, False, "Invalid VNPAY signature")
        await db.commit()
        return payment, "97", "Invalid signature"
    if not amount_matches:
        await _history(db, payment, old_status, source, payload, True, "Amount mismatch")
        await db.commit()
        return payment, "04", "Invalid amount"

    payment.signature_valid = True
    payment.response_code = str(payload.get("vnp_ResponseCode", "")) or None
    payment.provider_status = str(payload.get("vnp_TransactionStatus", "")) or None
    payment.provider_transaction_no = str(payload.get("vnp_TransactionNo", "")) or None
    payment.transaction_id = payment.provider_transaction_no or payment.transaction_id
    payment.bank_transaction_no = str(payload.get("vnp_BankTranNo", "")) or None
    payment.bank_code = str(payload.get("vnp_BankCode", "")) or None
    payment.card_type = str(payload.get("vnp_CardType", "")) or None
    payment.provider_paid_at = _provider_paid_at(payload.get("vnp_PayDate"))

    success = payment.response_code == "00" and payment.provider_status == "00"
    if success and old_status not in {"SUCCESS", "REFUNDED"}:
        payment.status = "SUCCESS"
        payment.paid_at = datetime.now(timezone.utc)
        payment.booking.status = "CONFIRMED"
        if payment.booking.promotion_id:
            promotion = await db.get(Promotion, payment.booking.promotion_id, with_for_update=True)
            if promotion:
                promotion.used_count += 1
    elif not success and old_status == "PENDING":
        payment.status = "FAILED"
        payment.booking.status = "CANCELLED"

    await _history(db, payment, old_status, source, payload, True)
    await db.commit()
    if success:
        await seat_events.broadcast(payment.booking.showtime_id, "SEATS_UPDATED")
    return payment, "00", "Confirm Success"


@router.post("/process", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def process_payment(
    payload: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaymentRead:
    """Legacy/demo payment endpoint. VNPAY must use /checkout and its signed callback."""
    if _is_vnpay(payload.payment_method):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="VNPAY must be initiated through checkout")
    booking = await _owned_pending_booking(db, payload.booking_id, current_user.id)
    valid, message = await validate_payment_amount(payload.amount, booking.total_price)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    payment = Payment(
        booking_id=booking.id, user_id=current_user.id, amount=payload.amount,
        payment_method=payload.payment_method, transaction_id=payload.transaction_id,
        status="SUCCESS", paid_at=datetime.now(timezone.utc),
    )
    booking.status = "CONFIRMED"
    db.add(payment)
    await db.flush()
    await _history(db, payment, None, "CREATE", {"payment_method": payload.payment_method}, None)
    await db.commit()
    await db.refresh(payment)
    await seat_events.broadcast(booking.showtime_id, "SEATS_UPDATED")
    return PaymentRead.model_validate(payment)


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    payload: PaymentCheckoutRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckoutResponse:
    booking = await _owned_pending_booking(db, payload.booking_id, current_user.id)
    subtotal = booking.subtotal_price or booking.total_price
    discount = Decimal("0")
    promotion = None
    if payload.promotion_code:
        promotion_result = await db.execute(
            select(Promotion).where(Promotion.code == payload.promotion_code.strip().upper()).with_for_update()
        )
        promotion = ensure_usable(promotion_result.scalar_one_or_none(), subtotal)
        discount = promotion_discount(promotion, subtotal)
    final_total = subtotal - discount
    valid, message = await validate_payment_amount(payload.amount, final_total)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    if (await db.execute(select(Payment).where(
        Payment.booking_id == booking.id,
        Payment.status.in_(["PENDING", "SUCCESS"]),
    ))).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking already has an active payment")

    vnpay = _is_vnpay(payload.payment_method)
    if vnpay and not settings.vnpay_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="VNPAY Sandbox is not configured")

    booking.subtotal_price = subtotal
    booking.discount_amount = discount
    booking.total_price = final_total
    booking.promotion_id = promotion.id if promotion else None
    payment_id = uuid4()
    payment = Payment(
        id=payment_id, booking_id=booking.id, user_id=current_user.id, amount=final_total,
        payment_method="VNPAY" if vnpay else payload.payment_method,
        status="PENDING" if vnpay else "SUCCESS",
        paid_at=None if vnpay else datetime.now(timezone.utc),
        provider_ref=payment_id.hex if vnpay else None,
    )
    if not vnpay:
        booking.status = "CONFIRMED"
        if promotion:
            promotion.used_count += 1
    db.add(payment)
    await db.flush()
    await _history(db, payment, None, "CREATE", {"amount": str(final_total), "method": payment.payment_method}, None)
    await db.commit()
    await db.refresh(payment)

    confirmation = booking.ticket_code or await generate_confirmation_number()
    payment_url = None
    if vnpay:
        payment_url = build_payment_url(
            txn_ref=payment.provider_ref,
            amount=int(payment.amount),
            order_info=f"Thanh toan ve CineAI {booking.id}",
            ip_address=_client_ip(request),
            expires_at=booking.expires_at or datetime.now(timezone.utc) + timedelta(minutes=15),
        )
    else:
        await seat_events.broadcast(booking.showtime_id, "SEATS_UPDATED")
    return CheckoutResponse(
        order_id=booking.id, booking_id=booking.id, payment_id=payment.id,
        status=payment.status, total_amount=payment.amount,
        qr_code=None if payment_url else await generate_qr_code_data(booking.id, confirmation),
        confirmation_number=confirmation,
        message=f"Đã tạo yêu cầu thanh toán. Mã xác nhận: {confirmation}",
        payment_url=payment_url,
    )


@router.get("/vnpay/return", include_in_schema=False)
async def vnpay_return(request: Request, db: AsyncSession = Depends(get_db)):
    payment, _, _ = await _apply_vnpay_result(db, dict(request.query_params), "RETURN")
    result = "success" if payment and payment.status == "SUCCESS" else "failed"
    payment_id = str(payment.id) if payment else ""
    return RedirectResponse(
        f"{settings.frontend_url.rstrip('/')}/payment/vnpay-return?result={result}&payment_id={payment_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/vnpay/ipn")
async def vnpay_ipn(request: Request, db: AsyncSession = Depends(get_db)):
    _, response_code, message = await _apply_vnpay_result(db, dict(request.query_params), "IPN")
    return {"RspCode": response_code, "Message": message}


@router.get("/vnpay/callback")
async def vnpay_callback(request: Request, db: AsyncSession = Depends(get_db)):
    payment, response_code, message = await _apply_vnpay_result(db, dict(request.query_params), "CALLBACK")
    success = payment is not None and payment.status == "SUCCESS"
    return {
        "success": success,
        "message": "Payment verified" if success else f"Payment verification failed: {message}",
        "payment_id": str(payment.id) if payment else None,
        "transaction_ref": str(payment.provider_ref) if payment else None,
        "payment_status": payment.status if payment else None,
    }



@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaymentRead:
    result = await db.execute(select(Payment).where(Payment.id == payment_id, Payment.user_id == current_user.id))
    payment = result.scalar_one_or_none()
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return PaymentRead.model_validate(payment)


@router.post("/{payment_id}/cancel", response_model=PaymentRead)
async def cancel_pending_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaymentRead:
    result = await db.execute(
        select(Payment)
        .options(selectinload(Payment.booking))
        .where(Payment.id == payment_id, Payment.user_id == current_user.id)
        .with_for_update()
    )
    payment = result.scalar_one_or_none()
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    if payment.status != "PENDING" or payment.booking.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only a pending payment request can be cancelled",
        )

    old_status = payment.status
    payment.status = "CANCELLED"
    payment.booking.status = "CANCELLED"
    payment.booking.cancellation_reason = "Customer cancelled pending VNPAY payment"
    payment.booking.cancelled_at = datetime.now(timezone.utc)
    payment.booking.cancelled_by = current_user.id
    await _history(
        db,
        payment,
        old_status,
        "CUSTOMER_CANCEL",
        {},
        None,
        "Pending VNPAY payment cancelled before completion",
    )
    await db.commit()
    await db.refresh(payment)
    await seat_events.broadcast(payment.booking.showtime_id, "SEATS_UPDATED")
    return PaymentRead.model_validate(payment)
