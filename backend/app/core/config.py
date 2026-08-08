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
    gemini_api_key: str = Field("", validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-3.5-flash-lite", validation_alias="GEMINI_MODEL")
    frontend_url: str = Field("http://localhost:3000", validation_alias="FRONTEND_URL")
    from_email: str = Field("phongnguyenfe@gmail.com", validation_alias="FROM_EMAIL")
    smtp_password: str = Field("dqlv galp qreu sbdx", validation_alias="PASSWORD")
    smtp_host: str = Field("smtp.gmail.com", validation_alias="SMTP_HOST")
    smtp_port: int = Field(587, validation_alias="SMTP_PORT")
    cancellation_cutoff_minutes: int = Field(120, validation_alias="CANCELLATION_CUTOFF_MINUTES")
    vnpay_tmn_code: str = Field("", validation_alias="VNPAY_TMN_CODE")
    vnpay_hash_secret: str = Field("", validation_alias="VNPAY_HASH_SECRET")
    vnpay_payment_url: str = Field(
        "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
        validation_alias="VNPAY_PAYMENT_URL",
    )
    vnpay_api_url: str = Field(
        "https://sandbox.vnpayment.vn/merchant_webapi/api/transaction",
        validation_alias="VNPAY_API_URL",
    )
    vnpay_return_url: str = Field(
        "http://localhost:8000/api/v1/payments/vnpay/return",
        validation_alias="VNPAY_RETURN_URL",
    )
    paypal_client_id: str = Field("", validation_alias="PAYPAL_CLIENT_ID")
    paypal_client_secret: str = Field("", validation_alias="PAYPAL_CLIENT_SECRET")
    paypal_mode: str = Field("sandbox", validation_alias="PAYPAL_MODE")
    facebook_page_id: str = Field("", validation_alias="NUXT_PUBLIC_FACEBOOK_PAGE_ID")
    facebook_app_id: str = Field("", validation_alias="NUXT_PUBLIC_FACEBOOK_APP_ID")
    facebook_app_secret: str = Field("", validation_alias="FACEBOOK_APP_SECRET")
    backend_cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5173",
        ],
        validation_alias="BACKEND_CORS_ORIGINS",
    )
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_backend_cors_origins(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if not v:
            return v
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @property
    def vnpay_enabled(self) -> bool:
        return bool(self.vnpay_tmn_code and self.vnpay_hash_secret)

    @property
    def paypal_enabled(self) -> bool:
        return bool(self.paypal_client_id and self.paypal_client_secret)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
