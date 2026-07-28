from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.payment import generate_confirmation_number, generate_qr_code_data, validate_payment_amount
from app.crud.booking import cleanup_expired_reservations
from app.crud.showtime import is_showtime_bookable
from app.db.session import get_db
from app.core.seat_events import seat_events
from app.models.commerce import Booking, Payment, Promotion
from app.api.routes.promotions import ensure_usable, promotion_discount
from app.models.user import User
from app.schemas.payment import CheckoutResponse, PaymentCheckoutRequest, PaymentCreate, PaymentRead

router = APIRouter()


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
