from __future__ import annotations

from typing import Literal
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.user import UserRead

class AdminUserRead(UserRead):
    branch_id: UUID | None = None


class BranchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    city: str


class BranchDetailRead(BranchRead):
    address_line: str
    district: str | None = None
    phone: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    movies: list[dict] = Field(default_factory=list)
    showtimes: list[dict] = Field(default_factory=list)


class UserRoleUpdate(BaseModel):
    role_code: Literal["CUSTOMER", "BRANCH_ADMIN", "STAFF", "SUPER_ADMIN"]
    branch_id: UUID | None = None


class RevenueDataPoint(BaseModel):
    label: str
    value: int


class AdminBreakdownItem(BaseModel):
    label: str
    revenue: int
    tickets: int = 0
    poster_url: str | None = None


class AdminStatsResponse(BaseModel):
    totalBranches: int
    totalMovies: int
    totalUsers: int
    totalRevenue: int
    todayRevenue: int = 0
    monthRevenue: int = 0
    ticketsSold: int = 0
    successfulBookings: int = 0
    cancelledBookings: int = 0
    pendingBookings: int = 0
    revenueChartData: list[RevenueDataPoint] = []
    branchPerformance: list[AdminBreakdownItem] = []
    topMovies: list[AdminBreakdownItem] = []


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
    director: str | None = Field(default=None, max_length=255)
    cast_names: list[str] = Field(default_factory=list)


class AdminUserCreate(BaseModel):
    email: str
    full_name: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=10)
    role_code: Literal["CUSTOMER", "BRANCH_ADMIN", "STAFF", "SUPER_ADMIN"] = "CUSTOMER"
    branch_id: UUID | None = None


class AdminUserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=10)
    is_active: bool | None = None


class BranchManageRead(BaseModel):
    id: UUID
    vendor_id: UUID
    code: str
    name: str
    address_line: str
    city: str
    district: str | None = None
    phone: str | None = None
    is_active: bool
    auditoriums_count: int = 0


class BranchManageCreate(BaseModel):
    vendor_id: UUID | None = None
    code: str = Field(min_length=3, max_length=20, pattern=r"^[A-Z0-9_-]+$")
    name: str = Field(min_length=5, max_length=200)
    address_line: str = Field(min_length=8, max_length=300)
    city: str = Field(min_length=3, max_length=100)
    district: str | None = Field(default=None, min_length=3, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    is_active: bool = True

    @field_validator("code", "name", "address_line", "city", "district", "phone", mode="before")
    @classmethod
    def trim_branch_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("phone")
    @classmethod
    def validate_branch_phone(cls, value: str | None) -> str | None:
        if value and not __import__("re").fullmatch(r"0\d{9}", value):
            raise ValueError("Số điện thoại chi nhánh phải gồm 10 chữ số và bắt đầu bằng 0")
        return value


class BranchManageUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=3, max_length=20, pattern=r"^[A-Z0-9_-]+$")
    name: str | None = Field(default=None, min_length=5, max_length=200)
    address_line: str | None = Field(default=None, min_length=8, max_length=300)
    city: str | None = Field(default=None, min_length=3, max_length=100)
    district: str | None = Field(default=None, min_length=3, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    is_active: bool | None = None

    @field_validator("code", "name", "address_line", "city", "district", "phone", mode="before")
    @classmethod
    def trim_branch_update_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("phone")
    @classmethod
    def validate_branch_update_phone(cls, value: str | None) -> str | None:
        if value and not __import__("re").fullmatch(r"0\d{9}", value):
            raise ValueError("Số điện thoại chi nhánh phải gồm 10 chữ số và bắt đầu bằng 0")
        return value


class AuditoriumRead(BaseModel):
    id: UUID
    branch_id: UUID
    branch_name: str
    code: str
    name: str
    total_seats: int
    screen_type: str | None = None
    is_active: bool


class AuditoriumCreate(BaseModel):
    branch_id: UUID
    code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=100)
    total_seats: int = Field(gt=0)
    screen_type: str | None = Field(default=None, max_length=30)
    is_active: bool = True


class AuditoriumUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=30)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    total_seats: int | None = Field(default=None, gt=0)
    screen_type: str | None = Field(default=None, max_length=30)
    is_active: bool | None = None


class SeatTypeRead(BaseModel):
    id: int
    code: str
    name: str


class SeatAdminRead(BaseModel):
    id: UUID
    auditorium_id: UUID
    auditorium_name: str
    branch_name: str
    seat_row: str
    seat_number: int
    seat_type_id: int
    seat_type_code: str
    is_active: bool


class SeatAdminCreate(BaseModel):
    auditorium_id: UUID
    seat_row: str = Field(min_length=1, max_length=5)
    seat_number: int = Field(gt=0)
    seat_type_id: int
    is_active: bool = True


class SeatAdminUpdate(BaseModel):
    seat_row: str | None = Field(default=None, min_length=1, max_length=5)
    seat_number: int | None = Field(default=None, gt=0)
    seat_type_id: int | None = None
    is_active: bool | None = None


class SeatLayoutCell(BaseModel):
    seat_row: str = Field(min_length=1, max_length=5)
    seat_number: int = Field(gt=0, le=100)
    seat_type_id: int
    is_active: bool = True


class SeatLayoutUpdate(BaseModel):
    seats: list[SeatLayoutCell] = Field(min_length=1, max_length=1000)


class SeatLayoutRead(BaseModel):
    auditorium_id: UUID
    active_seats: int
    seats: list[SeatAdminRead]


class ShowtimeAdminRead(BaseModel):
    id: UUID
    movie_id: UUID
    movie_title: str
    auditorium_id: UUID
    auditorium_name: str
    branch_name: str
    starts_at: datetime
    ends_at: datetime
    status: str
    stored_status: str = "OPEN"
    booking_closes_at: datetime | None = None
    cancellation_reason: str | None = None
    base_price: float
    booking_count: int = 0
    sold_seats: int = 0
    revenue: float = 0


class ShowtimeAdminCreate(BaseModel):
    movie_id: UUID
    auditorium_id: UUID
    starts_at: datetime
    ends_at: datetime
    status: str = Field(default="DRAFT", pattern="^(DRAFT|OPEN|CANCELLED)$")
    booking_closes_at: datetime | None = None
    base_price: float = Field(gt=0)


class ShowtimeAdminUpdate(BaseModel):
    auditorium_id: UUID | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    status: str | None = Field(default=None, pattern="^(DRAFT|OPEN|CANCELLED)$")
    booking_closes_at: datetime | None = None
    cancellation_reason: str | None = Field(default=None, max_length=1000)
    base_price: float | None = Field(default=None, gt=0)


class ShowtimeBulkCreate(BaseModel):
    showtimes: list[ShowtimeAdminCreate] = Field(min_length=1, max_length=500)


class ShowtimeBulkPublish(BaseModel):
    showtime_ids: list[UUID] = Field(min_length=1, max_length=500)


class TmdbMovieImportPayload(BaseModel):
    tmdb_id: int
    title: str = Field(min_length=1, max_length=255)
    overview: str | None = None
    poster_path: str | None = None
    release_date: date | None = None
    original_title: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default="vi-VN", max_length=50)
    duration_min: int = Field(default=120, gt=0)
    trailer_url: str | None = None
    genres: list[str] = Field(default_factory=list)
    director: str | None = Field(default=None, max_length=255)
    cast_names: list[str] = Field(default_factory=list)
    status: str = Field(default="UPCOMING", pattern="^(UPCOMING|NOW_SHOWING)$")


class TmdbMovieImportResponse(BaseModel):
    id: UUID
    title: str
    imported: bool


class BranchAdminSalesPoint(BaseModel):
    label: str
    tickets: int


class BranchAdminPromoRead(BaseModel):
    code: str
    discount: int
    desc: str
    active: bool


class BranchAdminShowtimeRead(BaseModel):
    id: UUID
    movie_id: UUID
    movie_title: str
    auditorium_id: UUID
    auditorium_name: str
    branch_name: str
    starts_at: datetime
    ends_at: datetime
    status: str
    base_price: float


class BranchAdminStatsResponse(BaseModel):
    branch_id: UUID
    branch_name: str
    ticketsSold: int
    activeShowtimes: int
    activePromos: int
    branchRevenue: int
    orders: int = 0
    seatsSold: int = 0
    occupancyRate: float = 0
    movieCount: int = 0
    showtimeCount: int = 0
    salesChartData: list[BranchAdminSalesPoint] = Field(default_factory=list)
    showtimesList: list[BranchAdminShowtimeRead] = Field(default_factory=list)
    promotionsList: list[BranchAdminPromoRead] = Field(default_factory=list)


class MovieRequestPayload(BaseModel):
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
    genres: list[str] = Field(default_factory=list)


class MovieRequestCreate(BaseModel):
    request_type: Literal["CREATE", "UPDATE", "DELETE"]
    target_movie_id: UUID | None = None
    payload: MovieRequestPayload


class MovieRequestRead(BaseModel):
    id: UUID
    requested_by_id: UUID
    target_movie_id: UUID | None = None
    request_type: Literal["CREATE", "UPDATE", "DELETE"]
    status: str
    payload: MovieRequestPayload
    review_note: str | None = None
    created_at: datetime
