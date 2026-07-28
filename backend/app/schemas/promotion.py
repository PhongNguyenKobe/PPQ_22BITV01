from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PromotionBase(BaseModel):
    code: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=2, max_length=200)
    discount_type: str
    discount_value: Decimal = Field(gt=0)
    max_discount: Decimal | None = Field(default=None, gt=0)
    min_order_amount: Decimal = Field(default=Decimal("0"), ge=0)
    starts_at: datetime
    ends_at: datetime
    usage_limit: int | None = Field(default=None, ge=0)
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("discount_type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        value = value.upper()
        if value not in {"PERCENT", "FIXED"}:
            raise ValueError("discount_type must be PERCENT or FIXED")
        return value

    @model_validator(mode="after")
    def validate_values(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        if self.discount_type == "PERCENT" and self.discount_value > 100:
            raise ValueError("percentage cannot exceed 100")
        return self


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    name: str | None = None
    discount_type: str | None = None
    discount_value: Decimal | None = Field(default=None, gt=0)
    max_discount: Decimal | None = Field(default=None, gt=0)
    min_order_amount: Decimal | None = Field(default=None, ge=0)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    usage_limit: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class PromotionRead(PromotionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    used_count: int
    created_at: datetime
    updated_at: datetime


class PromotionValidation(BaseModel):
    code: str
    subtotal: Decimal = Field(gt=0)


class PromotionQuote(BaseModel):
    promotion_id: UUID
    code: str
    subtotal: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    message: str
