from __future__ import annotations

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import RoleRead, UserRead


class AdminUserRead(UserRead):
    branch_id: UUID | None = None


class BranchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    city: str


class UserRoleUpdate(BaseModel):
    role_code: Literal["CUSTOMER", "BRANCH_ADMIN", "STAFF", "SUPER_ADMIN"]
    branch_id: UUID | None = None


class MovieDraftPayload(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    original_title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    duration_min: int = Field(gt=0)
    release_date: date | None = None
    age_rating: str | None = Field(default=None, max_length=10)
    language: str | None = Field(default=None, max_length=50)
    trailer_url: str | None = None
    poster_url: str | None = None
    status: str = Field(default="UPCOMING", pattern="^(UPCOMING|NOW_SHOWING|ENDED)$")
    genres: list[str] = Field(default_factory=list)


class MovieRequestCreate(BaseModel):
    request_type: Literal["CREATE", "UPDATE", "DELETE"]
    target_movie_id: UUID | None = None
    payload: MovieDraftPayload


class MovieRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    requested_by_id: UUID
    target_movie_id: UUID | None = None
    request_type: str
    status: str
    payload: dict
    review_note: str | None = None
    reviewed_by_id: UUID | None = None
    reviewed_at: datetime | None = None
    created_at: datetime
    requested_by: UserRead | None = None


class MovieRequestReview(BaseModel):
    review_note: str | None = None
