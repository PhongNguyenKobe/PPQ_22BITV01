from datetime import date, datetime
import re
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


VIETNAM_PHONE_PATTERN = re.compile(r"^0(?:3|5|7|8|9)\d{8}$")
PASSWORD_SPECIAL_PATTERN = re.compile(r"[^A-Za-z0-9]")


def validate_password_strength_value(value: str) -> str:
    if any(character.isspace() for character in value):
        raise ValueError("Mật khẩu không được chứa khoảng trắng")
    if not any(character.islower() for character in value):
        raise ValueError("Mật khẩu phải có ít nhất một chữ thường")
    if not any(character.isupper() for character in value):
        raise ValueError("Mật khẩu phải có ít nhất một chữ in hoa")
    if not any(character.isdigit() for character in value):
        raise ValueError("Mật khẩu phải có ít nhất một chữ số")
    if not PASSWORD_SPECIAL_PATTERN.search(value):
        raise ValueError("Mật khẩu phải có ít nhất một ký tự đặc biệt")
    return value


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
    address: str | None = Field(default=None, max_length=255)
    receive_marketing_emails: bool = True


class UserCreate(UserBase):
    phone: str = Field(min_length=10, max_length=10)
    password: str = Field(min_length=8, max_length=16)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        normalized = value.strip()
        if not VIETNAM_PHONE_PATTERN.fullmatch(normalized):
            raise ValueError("Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 03, 05, 07, 08 hoặc 09")
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        return validate_password_strength_value(value)


class UserUpdate(BaseModel):
    phone: str | None = Field(default=None, max_length=20)
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=10)
    address: str | None = Field(default=None, max_length=255)
    receive_marketing_emails: bool | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not VIETNAM_PHONE_PATTERN.fullmatch(normalized):
            raise ValueError("Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 03, 05, 07, 08 hoặc 09")
        return normalized


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=16)

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, value: str) -> str:
        return validate_password_strength_value(value)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    branch_id: UUID | None = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    roles: list[RoleRead] = Field(default_factory=list)
