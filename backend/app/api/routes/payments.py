from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.api.routes.promotions import ensure_context_usable, ensure_usable, promotion_discount
from app.core.config import settings
from app.core.seat_events import seat_events
from app.crud.booking import (
    cleanup_expired_reservations,
    confirm_booking_combo_inventory,
    issue_booking_ticket,
    release_booking_combo_inventory,
)
from app.crud.payment import generate_qr_code_data, validate_payment_amount
from app.crud.showtime import is_showtime_bookable
from app.db.session import get_db
from app.models.commerce import Booking, Payment, PaymentStatusHistory, Promotion, PromotionRedemption
from app.models.catalog import Showtime
from app.models.user import User
from app.schemas.payment import CheckoutResponse, PaymentCheckoutRequest, PaymentCreate, PaymentRead
from app.services.vnpay import build_payment_url, verify_signature
from app.services.notifications import enqueue_notification

router = APIRouter()


async def _confirm_promotion_redemption(db: AsyncSession, payment: Payment) -> None:
    redemption = (await db.execute(
        select(PromotionRedemption)
        .where(PromotionRedemption.payment_id == payment.id)
        .with_for_update()
    )).scalar_one_or_none()
    if redemption is None or redemption.status != "RESERVED":
        return
    promotion = await db.get(Promotion, redemption.promotion_id, with_for_update=True)
    redemption.status = "USED"
    if promotion:
        promotion.used_count += 1
        promotion.used_amount += redemption.discount_amount


async def _release_promotion_redemption(db: AsyncSession, payment: Payment) -> None:
    redemption = (await db.execute(
        select(PromotionRedemption)
        .where(PromotionRedemption.payment_id == payment.id)
        .with_for_update()
    )).scalar_one_or_none()
    if redemption is not None and redemption.status == "RESERVED":
        redemption.status = "RELEASED"


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
    # Expire stale reservations before interpreting a late provider callback.
    await cleanup_expired_reservations(db)
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
    if success and old_status not in {"SUCCESS", "REFUNDED", "RECONCILIATION_REQUIRED"}:
        payment.paid_at = datetime.now(timezone.utc)
        if old_status != "PENDING" or payment.booking.status != "PENDING":
            payment.status = "RECONCILIATION_REQUIRED"
            payment.refund_error = "Provider captured payment after the booking was cancelled or expired"
            enqueue_notification(db, payment.user_id, "PAYMENT_RECONCILIATION_REQUIRED", {
                "booking_id": str(payment.booking_id), "payment_id": str(payment.id),
            })
        else:
            payment.status = "SUCCESS"
            payment.booking.status = "CONFIRMED"
            await confirm_booking_combo_inventory(db, payment.booking.id)
            await issue_booking_ticket(db, payment.booking)
            await _confirm_promotion_redemption(db, payment)
            enqueue_notification(db, payment.user_id, "TICKET_ISSUED", {
                "booking_id": str(payment.booking_id), "ticket_code": payment.booking.ticket_code,
            })
    elif not success and old_status == "PENDING":
        payment.status = "FAILED"
        payment.booking.status = "CANCELLED"
        await release_booking_combo_inventory(db, [payment.booking.id])
        await _release_promotion_redemption(db, payment)

    await _history(db, payment, old_status, source, payload, True)
    await db.commit()
    if payment.status == "SUCCESS":
        await seat_events.broadcast(payment.booking.showtime_id, "SEATS_UPDATED")
    if payment.status == "RECONCILIATION_REQUIRED":
        return payment, "02", "Payment captured after reservation expiry; reconciliation required"
    return payment, "00", "Confirm Success"


@router.post("/process", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def process_payment(
    payload: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaymentRead:
    """Legacy/demo payment endpoint. VNPAY must use /checkout and its signed callback."""
    if settings.environment.strip().lower() not in {"development", "test"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
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
    await confirm_booking_combo_inventory(db, booking.id)
    await issue_booking_ticket(db, booking)
    await _confirm_promotion_redemption(db, payment)
    db.add(payment)
    await db.flush()
    enqueue_notification(db, payment.user_id, "TICKET_ISSUED", {
        "booking_id": str(booking.id), "ticket_code": booking.ticket_code,
    })
    await _history(db, payment, None, "CREATE", {"payment_method": payload.payment_method}, None)
    await db.commit()
    await db.refresh(payment)
    await seat_events.broadcast(booking.showtime_id, "SEATS_UPDATED")
    return PaymentRead.model_validate(payment)


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    payload: PaymentCheckoutRequest,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckoutResponse:
    if idempotency_key:
        idempotency_key = idempotency_key.strip()
        if not idempotency_key or len(idempotency_key) > 100:
            raise HTTPException(status_code=422, detail="Invalid Idempotency-Key")
        existing = (await db.execute(select(Payment).where(
            Payment.user_id == current_user.id,
            Payment.idempotency_key == idempotency_key,
        ))).scalar_one_or_none()
        if existing:
            booking = await db.get(Booking, payload.booking_id)
            if booking is None or booking.user_id != current_user.id or existing.booking_id != booking.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Idempotency-Key was used for another order")
            confirmation = booking.ticket_code or booking.id.hex[:12].upper()
            return CheckoutResponse(
                order_id=booking.id, booking_id=booking.id, payment_id=existing.id,
                status=existing.status, total_amount=existing.amount,
                qr_code=(await generate_qr_code_data(booking.id, confirmation)) if existing.status == "SUCCESS" else None,
                confirmation_number=confirmation,
                message="Existing idempotent payment request returned",
                payment_url=existing.checkout_url,
            )
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
        showtime = await db.get(Showtime, booking.showtime_id)
        method = "VNPAY" if _is_vnpay(payload.payment_method) else payload.payment_method.upper()
        await ensure_context_usable(
            db, promotion, user_id=current_user.id, showtime=showtime,
            payment_method=method, discount=discount,
        )
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
    paypal = payload.payment_method.upper() == "PAYPAL"
    if vnpay and not settings.vnpay_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="VNPAY Sandbox is not configured")
    if paypal and not settings.paypal_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="PayPal Sandbox is not configured")

    booking.subtotal_price = subtotal
    booking.discount_amount = discount
    booking.total_price = final_total
    booking.promotion_id = promotion.id if promotion else None
    payment_id = uuid4()
    
    is_async_payment = vnpay or paypal
    
    payment = Payment(
        id=payment_id, booking_id=booking.id, user_id=current_user.id, amount=final_total,
        idempotency_key=idempotency_key,
        payment_method="VNPAY" if vnpay else ("PAYPAL" if paypal else payload.payment_method),
        status="PENDING" if is_async_payment else "SUCCESS",
        paid_at=None if is_async_payment else datetime.now(timezone.utc),
        provider_ref=payment_id.hex if vnpay else None,
    )
    if not is_async_payment:
        booking.status = "CONFIRMED"
        await confirm_booking_combo_inventory(db, booking.id)
        await issue_booking_ticket(db, booking)
        enqueue_notification(db, current_user.id, "TICKET_ISSUED", {
            "booking_id": str(booking.id), "ticket_code": booking.ticket_code,
        })
    db.add(payment)
    await db.flush()
    if promotion:
        db.add(PromotionRedemption(
            promotion_id=promotion.id,
            user_id=current_user.id,
            booking_id=booking.id,
            payment_id=payment.id,
            discount_amount=discount,
            status="RESERVED" if is_async_payment else "USED",
        ))
        if not is_async_payment:
            promotion.used_count += 1
            promotion.used_amount += discount
    await _history(db, payment, None, "CREATE", {"amount": str(final_total), "method": payment.payment_method}, None)

    confirmation = booking.ticket_code or booking.id.hex[:12].upper()
    payment_url = None
    if vnpay:
        payment_url = build_payment_url(
            txn_ref=payment.provider_ref,
            amount=int(payment.amount),
            order_info=f"Thanh toan ve CineAI {booking.id}",
            ip_address=_client_ip(request),
            expires_at=booking.expires_at or datetime.now(timezone.utc) + timedelta(minutes=15),
        )
    elif paypal:
        from app.services.paypal import create_paypal_order
        base_api_url = f"{str(request.base_url).rstrip('/')}{settings.api_v1_prefix}"
        try:
            paypal_order = await create_paypal_order(
                amount=payment.amount,
                payment_id=payment.id,
                base_api_url=base_api_url,
            )
            payment.provider_ref = paypal_order["id"]
            for link in paypal_order["links"]:
                if link["rel"] == "approve":
                    payment_url = link["href"]
                    break
            if not payment_url:
                raise ValueError("No approval link in PayPal response")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"PayPal initialization failed: {str(e)}"
            )
    else:
        await seat_events.broadcast(booking.showtime_id, "SEATS_UPDATED")

    payment.checkout_url = payment_url

    await db.commit()
    await db.refresh(payment)
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



@router.get("/paypal/return", include_in_schema=False)
async def paypal_return(
    payment_id: UUID,
    token: str,
    PayerID: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    await cleanup_expired_reservations(db)
    result = await db.execute(
        select(Payment)
        .options(selectinload(Payment.booking))
        .where(Payment.id == payment_id)
        .with_for_update()
    )
    payment = result.scalar_one_or_none()
    if payment is None:
        return RedirectResponse(
            f"{settings.frontend_url.rstrip('/')}/checkout/paypal-return?result=failed&message=Payment not found",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    if token != payment.provider_ref:
        return RedirectResponse(
            f"{settings.frontend_url.rstrip('/')}/checkout/paypal-return?result=failed&payment_id={payment_id}&message=Invalid PayPal order",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    old_status = payment.status
    if old_status in {"SUCCESS", "REFUNDED"}:
        return RedirectResponse(
            f"{settings.frontend_url.rstrip('/')}/checkout/paypal-return?result=success&payment_id={payment_id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    try:
        from app.services.paypal import capture_paypal_order
        capture_res = await capture_paypal_order(token)
        capture_status = capture_res.get("status")
        
        capture_id = None
        try:
            purchase_units = capture_res.get("purchase_units", [])
            if purchase_units:
                payments_obj = purchase_units[0].get("payments", {})
                captures = payments_obj.get("captures", [])
                if captures:
                    capture_id = captures[0].get("id")
        except Exception:
            pass

        if capture_status == "COMPLETED":
            payment.paid_at = datetime.now(timezone.utc)
            payment.response_code = "COMPLETED"
            payment.provider_status = "COMPLETED"
            payment.provider_transaction_no = capture_id
            payment.transaction_id = capture_id or token
            payment.signature_valid = True
            captured_amount = None
            captured_currency = None
            try:
                captured_money = capture_res["purchase_units"][0]["payments"]["captures"][0]["amount"]
                captured_amount = Decimal(str(captured_money["value"]))
                captured_currency = str(captured_money["currency_code"]).upper()
            except (KeyError, IndexError, TypeError, ValueError):
                pass
            expected_paypal_amount = (payment.amount / Decimal("25000")).quantize(Decimal("0.01"))
            if captured_currency != "USD" or captured_amount != expected_paypal_amount:
                payment.status = "RECONCILIATION_REQUIRED"
                payment.refund_error = "PayPal captured an unexpected amount"
            elif old_status != "PENDING" or payment.booking.status != "PENDING":
                payment.status = "RECONCILIATION_REQUIRED"
                payment.refund_error = "PayPal captured payment after the booking was cancelled or expired"
            else:
                payment.status = "SUCCESS"
                payment.booking.status = "CONFIRMED"
                await confirm_booking_combo_inventory(db, payment.booking.id)
                await issue_booking_ticket(db, payment.booking)
                await _confirm_promotion_redemption(db, payment)
                enqueue_notification(db, payment.user_id, "TICKET_ISSUED", {
                    "booking_id": str(payment.booking_id), "ticket_code": payment.booking.ticket_code,
                })
            if payment.status == "RECONCILIATION_REQUIRED":
                enqueue_notification(db, payment.user_id, "PAYMENT_RECONCILIATION_REQUIRED", {
                    "booking_id": str(payment.booking_id), "payment_id": str(payment.id),
                })
                    
            await _history(db, payment, old_status, "PAYPAL_RETURN", capture_res, True)
            await db.commit()
            if payment.status == "SUCCESS":
                await seat_events.broadcast(payment.booking.showtime_id, "SEATS_UPDATED")
            
            return RedirectResponse(
                f"{settings.frontend_url.rstrip('/')}/checkout/paypal-return?result={'success' if payment.status == 'SUCCESS' else 'pending'}&payment_id={payment_id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        else:
            payment.status = "FAILED"
            payment.booking.status = "CANCELLED"
            await release_booking_combo_inventory(db, [payment.booking.id])
            await _release_promotion_redemption(db, payment)
            await _history(db, payment, old_status, "PAYPAL_RETURN", capture_res, False, f"PayPal status: {capture_status}")
            await db.commit()
            return RedirectResponse(
                f"{settings.frontend_url.rstrip('/')}/checkout/paypal-return?result=failed&payment_id={payment_id}&message=PayPal capture status: {capture_status}",
                status_code=status.HTTP_303_SEE_OTHER,
            )
    except Exception as e:
        payment.status = "FAILED"
        payment.booking.status = "CANCELLED"
        await release_booking_combo_inventory(db, [payment.booking.id])
        await _release_promotion_redemption(db, payment)
        await _history(db, payment, old_status, "PAYPAL_RETURN", {"error": str(e)}, False, "PayPal capture exception")
        await db.commit()
        return RedirectResponse(
            f"{settings.frontend_url.rstrip('/')}/checkout/paypal-return?result=failed&payment_id={payment_id}&message={str(e)}",
            status_code=status.HTTP_303_SEE_OTHER,
        )


@router.get("/paypal/cancel", include_in_schema=False)
async def paypal_cancel(
    payment_id: UUID,
    token: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Payment)
        .options(selectinload(Payment.booking))
        .where(Payment.id == payment_id)
        .with_for_update()
    )
    payment = result.scalar_one_or_none()
    if payment:
        old_status = payment.status
        if old_status == "PENDING":
            payment.status = "CANCELLED"
            payment.booking.status = "CANCELLED"
            await release_booking_combo_inventory(db, [payment.booking.id])
            await _release_promotion_redemption(db, payment)
            await _history(db, payment, old_status, "PAYPAL_CANCEL", {"token": token}, None, "User cancelled PayPal checkout")
            await db.commit()
    return RedirectResponse(
        f"{settings.frontend_url.rstrip('/')}/checkout/paypal-return?result=cancelled&payment_id={payment_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )



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
    await release_booking_combo_inventory(db, [payment.booking.id])
    await _release_promotion_redemption(db, payment)
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
