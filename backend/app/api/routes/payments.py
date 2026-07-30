from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import hmac
import secrets
from urllib.parse import urlencode
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.payment import generate_confirmation_number, generate_qr_code_data, validate_payment_amount
from app.crud.booking import cleanup_expired_reservations
from app.crud.showtime import is_showtime_bookable
from app.db.session import get_db
from app.core.config import settings
from app.core.seat_events import seat_events
from app.models.commerce import Booking, Payment, Promotion
from app.api.routes.promotions import ensure_usable, promotion_discount
from app.models.user import User
from app.schemas.payment import (
    CheckoutResponse,
    PaymentCheckoutRequest,
    PaymentCreate,
    PaymentRead,
    VnpayCallbackResponse,
    VnpayCreateRequest,
    VnpayCreateResponse,
)

router = APIRouter()


def _vnpay_signature(params: dict[str, str]) -> str:
    if not settings.vnpay_hash_secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="VNPay is not configured")
    data = urlencode(sorted(params.items()))
    return hmac.new(settings.vnpay_hash_secret.encode(), data.encode(), hashlib.sha512).hexdigest()


def _vnpay_is_success(params: dict[str, str]) -> bool:
    return params.get("vnp_ResponseCode") == "00" and params.get("vnp_TransactionStatus") == "00"


async def _finalize_vnpay(db: AsyncSession, params: dict[str, str]) -> tuple[bool, str, Payment | None]:
    signature = params.pop("vnp_SecureHash", "")
    params.pop("vnp_SecureHashType", None)
    if not signature or not hmac.compare_digest(signature.lower(), _vnpay_signature(params).lower()):
        return False, "Invalid VNPay signature", None
    transaction_ref = params.get("vnp_TxnRef")
    if not transaction_ref:
        return False, "Missing VNPay transaction reference", None
    result = await db.execute(select(Payment).where(Payment.transaction_id == transaction_ref).with_for_update())
    payment = result.scalar_one_or_none()
    if payment is None:
        return False, "Payment not found", None
    expected_amount = int(Decimal(payment.amount) * 100)
    if params.get("vnp_TmnCode") != settings.vnpay_tmn_code or params.get("vnp_Amount") != str(expected_amount):
        return False, "VNPay transaction data does not match", payment
    if payment.status == "SUCCESS":
        return True, "Payment already confirmed", payment
    if not _vnpay_is_success(params):
        payment.status = "FAILED"
        await db.commit()
        return False, "VNPay payment was declined", payment
    booking = await db.get(Booking, payment.booking_id, with_for_update=True)
    if booking is None or booking.status != "PENDING":
        return False, "Booking is no longer payable", payment
    payment.status = "SUCCESS"
    payment.paid_at = datetime.now(timezone.utc)
    booking.status = "CONFIRMED"
    if booking.promotion_id:
        promotion = await db.get(Promotion, booking.promotion_id, with_for_update=True)
        if promotion:
            promotion.used_count += 1
    await db.commit()
    await seat_events.broadcast(booking.showtime_id, "SEATS_UPDATED")
    return True, "Payment confirmed", payment


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


@router.post("/process", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def process_payment(
    payload: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaymentRead:
    booking = await _owned_pending_booking(db, payload.booking_id, current_user.id)
    valid, message = await validate_payment_amount(payload.amount, booking.total_price)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    payment = Payment(
        booking_id=booking.id,
        user_id=current_user.id,
        amount=payload.amount,
        payment_method=payload.payment_method,
        transaction_id=payload.transaction_id,
        status="SUCCESS",
        paid_at=datetime.now(timezone.utc),
    )
    booking.status = "CONFIRMED"
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    await seat_events.broadcast(booking.showtime_id, "SEATS_UPDATED")
    return PaymentRead.model_validate(payment)


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    payload: PaymentCheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckoutResponse:
    booking = await _owned_pending_booking(db, payload.booking_id, current_user.id)
    subtotal = booking.subtotal_price or booking.total_price
    discount = 0
    promotion = None
    if payload.promotion_code:
        promotion_result = await db.execute(
            select(Promotion)
            .where(Promotion.code == payload.promotion_code.strip().upper())
            .with_for_update()
        )
        promotion = ensure_usable(promotion_result.scalar_one_or_none(), subtotal)
        discount = promotion_discount(promotion, subtotal)
    final_total = subtotal - discount
    valid, message = await validate_payment_amount(payload.amount, final_total)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    previous = await db.execute(
        select(Payment).where(Payment.booking_id == booking.id, Payment.status == "SUCCESS")
    )
    if previous.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking has already been paid")
    booking.subtotal_price = subtotal
    booking.discount_amount = discount
    booking.total_price = final_total
    booking.promotion_id = promotion.id if promotion else None
    if promotion:
        promotion.used_count += 1
    payment = Payment(
        booking_id=booking.id,
        user_id=current_user.id,
        amount=final_total,
        payment_method=payload.payment_method,
        status="SUCCESS",
        paid_at=datetime.now(timezone.utc),
    )
    booking.status = "CONFIRMED"
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    await seat_events.broadcast(booking.showtime_id, "SEATS_UPDATED")
    confirmation = await generate_confirmation_number()
    return CheckoutResponse(
        order_id=booking.id,
        booking_id=booking.id,
        payment_id=payment.id,
        status=payment.status,
        total_amount=payment.amount,
        qr_code=await generate_qr_code_data(booking.id, confirmation),
        confirmation_number=confirmation,
        message=f"Đã tạo yêu cầu thanh toán. Mã xác nhận: {confirmation}",
    )


@router.post("/vnpay/create", response_model=VnpayCreateResponse)
async def create_vnpay_payment(
    payload: VnpayCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VnpayCreateResponse:
    if not settings.vnpay_tmn_code or not settings.vnpay_hash_secret or not settings.vnpay_return_url:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="VNPay Sandbox is not configured")
    booking = await _owned_pending_booking(db, payload.booking_id, current_user.id)
    subtotal = booking.subtotal_price or booking.total_price
    discount = Decimal("0")
    promotion = None
    if payload.promotion_code:
        promotion_result = await db.execute(select(Promotion).where(Promotion.code == payload.promotion_code.strip().upper()))
        promotion = ensure_usable(promotion_result.scalar_one_or_none(), subtotal)
        discount = promotion_discount(promotion, subtotal)
    final_total = subtotal - discount
    valid, message = await validate_payment_amount(payload.amount, final_total)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    booking.subtotal_price = subtotal
    booking.discount_amount = discount
    booking.total_price = final_total
    booking.promotion_id = promotion.id if promotion else None
    transaction_ref = f"CINE{datetime.now().strftime('%Y%m%d%H%M%S')}{secrets.token_hex(4).upper()}"
    payment = Payment(
        booking_id=booking.id,
        user_id=current_user.id,
        amount=final_total,
        payment_method="VNPAY",
        transaction_id=transaction_ref,
        status="PENDING",
    )
    db.add(payment)
    await db.commit()
    create_date = datetime.now().astimezone().strftime("%Y%m%d%H%M%S")
    params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": settings.vnpay_tmn_code,
        "vnp_Amount": str(int(Decimal(final_total) * 100)),
        "vnp_CreateDate": create_date,
        "vnp_CurrCode": "VND",
        "vnp_IpAddr": request.client.host if request.client else "127.0.0.1",
        "vnp_Locale": "vn",
        "vnp_OrderInfo": f"Thanh toan ve phim {transaction_ref}",
        "vnp_OrderType": "other",
        "vnp_ReturnUrl": settings.vnpay_return_url,
        "vnp_TxnRef": transaction_ref,
    }
    return VnpayCreateResponse(
        payment_url=f"{settings.vnpay_payment_url}?{urlencode(params)}&vnp_SecureHash={_vnpay_signature(params)}",
        transaction_ref=transaction_ref,
        expires_at=booking.expires_at,
    )


@router.get("/vnpay/callback", response_model=VnpayCallbackResponse)
async def vnpay_callback(request: Request, db: AsyncSession = Depends(get_db)) -> VnpayCallbackResponse:
    success, message, payment = await _finalize_vnpay(db, dict(request.query_params))
    return VnpayCallbackResponse(
        success=success,
        message=message,
        transaction_ref=payment.transaction_id if payment else None,
        payment_status=payment.status if payment else None,
    )


@router.get("/vnpay/ipn")
async def vnpay_ipn(request: Request, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    success, message, payment = await _finalize_vnpay(db, dict(request.query_params))
    if payment is None:
        return {"RspCode": "01", "Message": message}
    return {"RspCode": "00" if success else "02", "Message": message}


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
