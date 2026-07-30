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


class VnpayCreateRequest(BaseModel):
    booking_id: UUID
    amount: Decimal = Field(gt=0)
    promotion_code: str | None = Field(default=None, max_length=50)


class VnpayCreateResponse(BaseModel):
    payment_url: str
    transaction_ref: str
    expires_at: datetime | None = None


class VnpayCallbackResponse(BaseModel):
    success: bool
    message: str
    transaction_ref: str | None = None
    payment_status: str | None = None
