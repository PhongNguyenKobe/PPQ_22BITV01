from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SeatBookRequest(BaseModel):
    """Request to get available seats for a showtime"""
    showtime_id: UUID


class SeatBookResponse(BaseModel):
    """Response with seat information"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    seat_row: str
    seat_number: int
    seat_type: str
    is_active: bool
    is_booked: bool = False
    status: str  # 'AVAILABLE', 'BOOKED', 'HOLD'


class BookingCreate(BaseModel):
    """Create a new booking"""
    showtime_id: UUID
    seat_ids: list[UUID]
    quantity: int = Field(gt=0, le=10)
    total_price: Decimal


class BookingRead(BaseModel):
    """Booking information response"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    showtime_id: UUID
    movie_id: UUID
    booking_date: datetime
    seats: list[dict] = Field(default_factory=list)  # [{'row': 'A', 'number': 1}, ...]
    quantity: int
    total_price: Decimal
    status: str  # 'PENDING', 'CONFIRMED', 'CANCELLED'
    created_at: datetime


class BookingUpdate(BaseModel):
    """Update booking status"""
    status: str  # 'CONFIRMED', 'CANCELLED'


class BookingListResponse(BaseModel):
    """List all bookings with pagination"""
    total: int
    page: int
    limit: int
    bookings: list[BookingRead]
