from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    """Create payment request"""
    booking_id: UUID
    amount: Decimal = Field(gt=0)
    payment_method: str  # 'CREDIT_CARD', 'DEBIT_CARD', 'MOMO', 'VNPAY', 'WALLET'
    transaction_id: str | None = None


class PaymentRead(BaseModel):
    """Payment information response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    booking_id: UUID
    user_id: UUID
    amount: Decimal
    payment_method: str
    status: str  # 'PENDING', 'SUCCESS', 'FAILED', 'REFUNDED'
    transaction_id: str | None = None
    provider_ref: str | None = None
    provider_transaction_no: str | None = None
    bank_transaction_no: str | None = None
    bank_code: str | None = None
    card_type: str | None = None
    response_code: str | None = None
    provider_status: str | None = None
    signature_valid: bool | None = None
    provider_paid_at: datetime | None = None
    last_verified_at: datetime | None = None
    refund_transaction_no: str | None = None
    refund_response_code: str | None = None
    refund_provider_status: str | None = None
    refund_error: str | None = None
    refund_attempts: int = 0
    refund_requested_at: datetime | None = None
    refunded_at: datetime | None = None
    paid_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class PaymentCheckoutRequest(BaseModel):
    """Checkout request - finalize order"""
    booking_id: UUID
    amount: Decimal
    payment_method: str
    promotion_code: str | None = Field(default=None, max_length=50)
    combo_ids: list[UUID] | None = None  # Optional combo items


class CheckoutResponse(BaseModel):
    """Checkout response with order confirmation"""
    order_id: UUID
    booking_id: UUID
    payment_id: UUID
    status: str
    total_amount: Decimal
    qr_code: str | None = None
    confirmation_number: str
    message: str
    payment_url: str | None = None
