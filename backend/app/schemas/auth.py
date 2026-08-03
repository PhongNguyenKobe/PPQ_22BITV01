from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class TokenData(BaseModel):
    sub: str | None = None
    roles: list[str] = Field(default_factory=list)


class AuthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str = "bearer"
    user: UserRead


class CheckIdentifierRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=255)


class VerifyOtpRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=255)
    code: str = Field(min_length=6, max_length=6)


class ResendOtpRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=255)


class RegisterResponse(BaseModel):
    message: str
    email: str


class ForgotPasswordRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=255)


class ResetPasswordRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=255)
    code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=16)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        from app.schemas.user import validate_password_strength_value
        return validate_password_strength_value(value)
