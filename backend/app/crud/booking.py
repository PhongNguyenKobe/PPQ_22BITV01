from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.catalog import Seat, Showtime


async def list_showtime_available_seats(db: AsyncSession, showtime_id: UUID) -> list[dict]:
    """
    Get all seats for a showtime with their booking status.
    Returns: List of seat info with is_booked flag
    """
    result = await db.execute(
        select(Seat)
        .options(selectinload(Seat.seat_type), selectinload(Seat.auditorium))
        .join(Showtime, Showtime.auditorium_id == Seat.auditorium_id)
        .where(
            and_(
                Showtime.id == showtime_id,
                Seat.is_active == True
            )
        )
        .order_by(Seat.seat_row.asc(), Seat.seat_number.asc())
    )
    seats = result.scalars().all()
    
    return [
        {
            "id": str(seat.id),
            "seat_row": seat.seat_row,
            "seat_number": seat.seat_number,
            "seat_type": seat.seat_type.name if seat.seat_type else "STANDARD",
            "is_active": seat.is_active,
            "is_booked": False,  # Would check against bookings table in real implementation
            "status": "AVAILABLE"
        }
        for seat in seats
    ]


async def validate_showtime_exists(db: AsyncSession, showtime_id: UUID) -> bool:
    """
    Validate if showtime exists and is open for booking.
    """
    result = await db.execute(
        select(Showtime).where(
            and_(
                Showtime.id == showtime_id,
                Showtime.status == "OPEN"
            )
        )
    )
    return result.scalar_one_or_none() is not None


async def validate_seats_available(db: AsyncSession, showtime_id: UUID, seat_ids: list[UUID]) -> tuple[bool, str]:
    """
    Validate if all selected seats are available for the showtime.
    Returns: (is_valid, message)
    """
    if not seat_ids:
        return False, "No seats selected"
    
    if len(seat_ids) > 10:
        return False, "Maximum 10 seats per booking"
    
    # In a real implementation, check against Booking table
    # For now, just validate seats exist
    result = await db.execute(
        select(func.count(Seat.id)).where(
            and_(
                Seat.id.in_(seat_ids),
                Seat.is_active == True
            )
        )
    )
    count = result.scalar()
    
    if count != len(seat_ids):
        return False, "One or more seats are invalid or inactive"
    
    return True, "Seats are available"
