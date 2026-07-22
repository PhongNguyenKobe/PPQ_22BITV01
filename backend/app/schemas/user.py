from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class UserBase(BaseModel):
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    full_name: str = Field(min_length=1, max_length=150)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=10)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    phone: str | None = Field(default=None, max_length=20)
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=10)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    branch_id: UUID | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: list[RoleRead] = Field(default_factory=list)
