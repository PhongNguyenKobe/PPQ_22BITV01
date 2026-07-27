from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.payment import generate_confirmation_number, generate_qr_code_data, validate_payment_amount
from app.db.session import get_db
from app.models.commerce import Booking, Payment
from app.models.user import User
from app.schemas.payment import CheckoutResponse, PaymentCheckoutRequest, PaymentCreate, PaymentRead

router = APIRouter()


async def _owned_pending_booking(db: AsyncSession, booking_id: UUID, user_id: UUID) -> Booking:
    booking = await db.get(Booking, booking_id)
    if booking is None or booking.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking is not payable")
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
    return PaymentRead.model_validate(payment)


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    payload: PaymentCheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckoutResponse:
    booking = await _owned_pending_booking(db, payload.booking_id, current_user.id)
    valid, message = await validate_payment_amount(payload.amount, booking.total_price)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    payment = Payment(
        booking_id=booking.id,
        user_id=current_user.id,
        amount=payload.amount,
        payment_method=payload.payment_method,
        status="SUCCESS",
        paid_at=datetime.now(timezone.utc),
    )
    booking.status = "CONFIRMED"
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
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
