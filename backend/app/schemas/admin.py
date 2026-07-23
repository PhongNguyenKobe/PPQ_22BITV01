from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserRead


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

