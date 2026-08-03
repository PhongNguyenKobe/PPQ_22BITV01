from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ComboWrite(BaseModel):
    branch_id: UUID
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(gt=0)
    image_url: str | None = None
    stock_quantity: int | None = Field(default=None, ge=0)
    is_active: bool = True


class ComboRead(ComboWrite):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
