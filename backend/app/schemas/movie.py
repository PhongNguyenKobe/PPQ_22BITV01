from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GenreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class MovieRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    original_title: str | None = None
    description: str | None = None
    duration_min: int
    release_date: date | None = None
    age_rating: str | None = None
    language: str | None = None
    trailer_url: str | None = None
    poster_url: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    genres: list[GenreRead] = Field(default_factory=list)


class ShowtimeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    movie_id: UUID
    auditorium_id: UUID
    starts_at: datetime
    ends_at: datetime
    status: str
    base_price: Decimal
    branch_name: str
    screen_name: str


class SeatRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    seat_row: str
    seat_number: int
    seat_type: str
    is_active: bool
    status: str
