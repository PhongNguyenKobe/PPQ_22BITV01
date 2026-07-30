from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "PPQ API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = Field(
        "postgresql+asyncpg://user:password@localhost:5432/dbname",
        validation_alias="DATABASE_URL",
    )
    jwt_secret_key: str = Field("change-this-secret", validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(10080, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    backend_cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5173",
        ],
        validation_alias="BACKEND_CORS_ORIGINS",
    )
    vnpay_tmn_code: str | None = Field(default=None, validation_alias="VNPAY_TMN_CODE")
    vnpay_hash_secret: str | None = Field(default=None, validation_alias="VNPAY_HASH_SECRET")
    vnpay_payment_url: str = Field(
        "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
        validation_alias="VNPAY_PAYMENT_URL",
    )
    vnpay_return_url: str | None = Field(default=None, validation_alias="VNPAY_RETURN_URL")

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_backend_cors_origins(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
