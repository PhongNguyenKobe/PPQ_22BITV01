from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.catalog import Seat, Showtime
from app.models.commerce import Booking, BookingSeat


async def list_showtime_available_seats(db: AsyncSession, showtime_id: UUID) -> list[dict]:
    result = await db.execute(
        select(Seat)
        .options(selectinload(Seat.seat_type))
        .join(Showtime, Showtime.auditorium_id == Seat.auditorium_id)
        .where(Showtime.id == showtime_id, Seat.is_active.is_(True))
        .order_by(Seat.seat_row, Seat.seat_number)
    )
    seats = list(result.scalars().all())
    booked_result = await db.execute(
        select(BookingSeat.seat_id)
        .join(Booking, Booking.id == BookingSeat.booking_id)
        .where(BookingSeat.showtime_id == showtime_id, Booking.status.in_(["PENDING", "CONFIRMED"]))
    )
    booked_ids = set(booked_result.scalars().all())
    return [
        {
            "id": seat.id,
            "seat_row": seat.seat_row,
            "seat_number": seat.seat_number,
            "seat_type": seat.seat_type.name if seat.seat_type else "STANDARD",
            "is_active": seat.is_active,
            "is_booked": seat.id in booked_ids,
            "status": "BOOKED" if seat.id in booked_ids else "AVAILABLE",
        }
        for seat in seats
    ]


async def validate_showtime_exists(db: AsyncSession, showtime_id: UUID) -> bool:
    result = await db.execute(select(Showtime.id).where(Showtime.id == showtime_id, Showtime.status == "OPEN"))
    return result.scalar_one_or_none() is not None


async def validate_seats_available(db: AsyncSession, showtime_id: UUID, seat_ids: list[UUID]) -> tuple[bool, str]:
    unique_ids = set(seat_ids)
    if not unique_ids:
        return False, "No seats selected"
    if len(unique_ids) != len(seat_ids):
        return False, "Duplicate seats are not allowed"
    if len(unique_ids) > 10:
        return False, "Maximum 10 seats per booking"

    showtime = await db.get(Showtime, showtime_id)
    if showtime is None:
        return False, "Showtime not found"
    result = await db.execute(
        select(Seat).where(
            Seat.id.in_(unique_ids),
            Seat.auditorium_id == showtime.auditorium_id,
            Seat.is_active.is_(True),
        )
    )
    if len(result.scalars().all()) != len(unique_ids):
        return False, "One or more seats are invalid for this showtime"
    booked = await db.execute(
        select(func.count(BookingSeat.id))
        .join(Booking, Booking.id == BookingSeat.booking_id)
        .where(
            BookingSeat.showtime_id == showtime_id,
            BookingSeat.seat_id.in_(unique_ids),
            Booking.status.in_(["PENDING", "CONFIRMED"]),
        )
    )
    if (booked.scalar() or 0) > 0:
        return False, "One or more seats are already booked"
    return True, "Seats are available"


def booking_to_dict(booking: Booking) -> dict:
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "showtime_id": booking.showtime_id,
        "movie_id": booking.showtime.movie_id,
        "booking_date": booking.created_at,
        "seats": [{"row": item.seat.seat_row, "number": item.seat.seat_number} for item in booking.seats],
        "quantity": len(booking.seats),
        "total_price": booking.total_price,
        "status": booking.status,
        "created_at": booking.created_at,
    }


async def get_user_booking(db: AsyncSession, booking_id: UUID, user_id: UUID) -> Booking | None:
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.showtime), selectinload(Booking.seats).selectinload(BookingSeat.seat))
        .where(Booking.id == booking_id, Booking.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user_booking(db: AsyncSession, user_id: UUID, showtime_id: UUID, seat_ids: list[UUID]) -> Booking:
    showtime = await db.get(Showtime, showtime_id)
    booking = Booking(
        user_id=user_id,
        showtime_id=showtime_id,
        total_price=Decimal(str(showtime.base_price)) * len(seat_ids),
        status="PENDING",
        seats=[BookingSeat(showtime_id=showtime_id, seat_id=seat_id) for seat_id in seat_ids],
    )
    db.add(booking)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("SEAT_ALREADY_BOOKED") from None
    return await get_user_booking(db, booking.id, user_id)


async def list_user_booking_rows(db: AsyncSession, user_id: UUID, skip: int, limit: int) -> tuple[int, list[Booking]]:
    total_result = await db.execute(select(func.count(Booking.id)).where(Booking.user_id == user_id))
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.showtime), selectinload(Booking.seats).selectinload(BookingSeat.seat))
        .where(Booking.user_id == user_id)
        .order_by(Booking.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return total_result.scalar() or 0, list(result.scalars().all())
