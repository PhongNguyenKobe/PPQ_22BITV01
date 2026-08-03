from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class MovieReviewWrite(BaseModel):
    rating: int = Field(ge=1, le=5)
    content: str = Field(min_length=1, max_length=1000)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Vui lòng nhập cảm nhận của bạn")
        return value


class MovieReviewRead(BaseModel):
    id: UUID
    user_id: UUID
    user_name: str
    rating: int
    content: str
    verified_purchase: bool
    created_at: datetime
    updated_at: datetime


class MovieReviewSummary(BaseModel):
    total: int
    average: float
    distribution: dict[int, int]


class MovieReviewsResponse(BaseModel):
    summary: MovieReviewSummary
    reviews: list[MovieReviewRead]
