from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.payment import (
    validate_payment_amount,
    generate_confirmation_number,
    generate_qr_code_data,
)
from app.db.session import get_db
from app.schemas.payment import (
    PaymentCreate,
    PaymentRead,
    PaymentCheckoutRequest,
    CheckoutResponse,
)
from app.models.user import User

router = APIRouter()


@router.post("/process", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def process_payment(
    payload: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaymentRead:
    """
    Process payment for a booking.
    
    - **booking_id**: UUID of the booking to pay for
    - **amount**: Payment amount (must match booking total)
    - **payment_method**: Payment method (CREDIT_CARD, DEBIT_CARD, MOMO, VNPAY, WALLET)
    - **transaction_id**: Optional external transaction ID from payment gateway
    - Returns: Payment confirmation
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Validate payment amount
    # TODO: Fetch booking total from database
    booking_total = payload.amount  # Placeholder
    is_valid, message = await validate_payment_amount(payload.amount, booking_total)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # TODO: Call payment gateway (Stripe, VNPAY, Momo, etc.)
    # TODO: Store payment record in database
    
    return PaymentRead(
        id=UUID('00000000-0000-0000-0000-000000000003'),
        booking_id=payload.booking_id,
        user_id=current_user.id,
        amount=payload.amount,
        payment_method=payload.payment_method,
        status="SUCCESS",
        transaction_id=payload.transaction_id,
        paid_at=None,
        created_at=None,
        updated_at=None,
    )


@router.post("/checkout", response_model=CheckoutResponse, status_code=status.HTTP_200_OK)
async def checkout(
    payload: PaymentCheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckoutResponse:
    """
    Finalize checkout - create order with payment and generate e-ticket.
    
    This endpoint:
    1. Process payment
    2. Confirm booking
    3. Generate QR code for e-ticket
    4. Send confirmation email
    
    - **booking_id**: UUID of the booking
    - **amount**: Total amount to charge
    - **payment_method**: Payment method
    - **combo_ids**: Optional combo items (snacks, drinks, etc.)
    - Returns: Order confirmation with QR code
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # TODO: Process payment
    # TODO: Update booking status to CONFIRMED
    # TODO: Generate e-ticket
    # TODO: Send confirmation email
    
    confirmation_number = await generate_confirmation_number()
    qr_code_data = await generate_qr_code_data(payload.booking_id, confirmation_number)
    
    return CheckoutResponse(
        order_id=payload.booking_id,
        booking_id=payload.booking_id,
        payment_id=UUID('00000000-0000-0000-0000-000000000004'),
        status="SUCCESS",
        total_amount=payload.amount,
        qr_code=qr_code_data,
        confirmation_number=confirmation_number,
        message=f"Đặt vé thành công! Mã xác nhận: {confirmation_number}"
    )


@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaymentRead:
    """
    Get payment details.
    
    - **payment_id**: UUID of the payment
    - Returns: Payment information
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # TODO: Fetch payment from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Payment not found"
    )
