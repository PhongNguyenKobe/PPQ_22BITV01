from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.catalog import Seat, Showtime
from app.models.commerce import Booking, BookingSeat, SeatHold

HOLD_MINUTES = 10


async def cleanup_expired_reservations(db: AsyncSession) -> None:
    now = datetime.now(timezone.utc)
    await db.execute(delete(SeatHold).where(SeatHold.expires_at <= now))
    expired_result = await db.execute(
        select(Booking).where(
            Booking.status == "PENDING",
            Booking.expires_at.is_not(None),
            Booking.expires_at <= now,
        )
    )
    expired = list(expired_result.scalars().all())
    if expired:
        ids = [item.id for item in expired]
        await db.execute(delete(BookingSeat).where(BookingSeat.booking_id.in_(ids)))
        for booking in expired:
            booking.status = "CANCELLED"
    await db.flush()


async def list_showtime_available_seats(db: AsyncSession, showtime_id: UUID, user_id: UUID | None = None) -> list[dict]:
    await cleanup_expired_reservations(db)
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
    holds_result = await db.execute(
        select(SeatHold.seat_id, SeatHold.user_id).where(
            SeatHold.showtime_id == showtime_id,
            SeatHold.expires_at > datetime.now(timezone.utc),
        )
    )
    holds = {row.seat_id: row.user_id for row in holds_result.all()}
    return [
        {
            "id": seat.id,
            "seat_row": seat.seat_row,
            "seat_number": seat.seat_number,
            "seat_type": seat.seat_type.code if seat.seat_type else "STANDARD",
            "is_active": seat.is_active,
            "is_booked": seat.id in booked_ids,
            "status": (
                "BOOKED"
                if seat.id in booked_ids
                else "HELD_BY_ME"
                if holds.get(seat.id) == user_id
                else "HOLD"
                if seat.id in holds
                else "AVAILABLE"
            ),
        }
        for seat in seats
    ]


async def validate_showtime_exists(db: AsyncSession, showtime_id: UUID) -> bool:
    result = await db.execute(
        select(Showtime.id).where(
            Showtime.id == showtime_id,
            Showtime.status == "OPEN",
            Showtime.booking_closes_at > func.now(),
        )
    )
    return result.scalar_one_or_none() is not None


async def validate_seats_available(db: AsyncSession, showtime_id: UUID, seat_ids: list[UUID], user_id: UUID | None = None) -> tuple[bool, str]:
    await cleanup_expired_reservations(db)
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
    held = await db.execute(
        select(func.count(SeatHold.id)).where(
            SeatHold.showtime_id == showtime_id,
            SeatHold.seat_id.in_(unique_ids),
            SeatHold.expires_at > datetime.now(timezone.utc),
            SeatHold.user_id != user_id if user_id else SeatHold.user_id.is_not(None),
        )
    )
    if (held.scalar() or 0) > 0:
        return False, "One or more seats are temporarily held by another customer"
    return True, "Seats are available"


async def hold_showtime_seats(
    db: AsyncSession,
    showtime_id: UUID,
    user_id: UUID,
    seat_ids: list[UUID],
) -> datetime:
    if not await validate_showtime_exists(db, showtime_id):
        raise ValueError("SHOWTIME_UNAVAILABLE")
    valid, message = await validate_seats_available(db, showtime_id, seat_ids, user_id)
    if not valid:
        raise ValueError(message)
    await db.execute(
        delete(SeatHold).where(
            SeatHold.showtime_id == showtime_id,
            SeatHold.user_id == user_id,
        )
    )
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=HOLD_MINUTES)
    db.add_all(
        [
            SeatHold(showtime_id=showtime_id, seat_id=seat_id, user_id=user_id, expires_at=expires_at)
            for seat_id in seat_ids
        ]
    )
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("One or more seats were just held by another customer") from None
    return expires_at


async def release_showtime_holds(db: AsyncSession, showtime_id: UUID, user_id: UUID) -> None:
    await db.execute(
        delete(SeatHold).where(SeatHold.showtime_id == showtime_id, SeatHold.user_id == user_id)
    )
    await db.commit()


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
    await cleanup_expired_reservations(db)
    showtime_result = await db.execute(
        select(Showtime).where(
            Showtime.id == showtime_id,
            Showtime.status == "OPEN",
            Showtime.booking_closes_at > func.now(),
        )
    )
    showtime = showtime_result.scalar_one_or_none()
    if showtime is None:
        raise ValueError("SHOWTIME_UNAVAILABLE")
    holds_result = await db.execute(
        select(SeatHold.seat_id).where(
            SeatHold.showtime_id == showtime_id,
            SeatHold.user_id == user_id,
            SeatHold.seat_id.in_(seat_ids),
            SeatHold.expires_at > datetime.now(timezone.utc),
        )
    )
    if set(holds_result.scalars().all()) != set(seat_ids):
        raise ValueError("SEAT_HOLD_REQUIRED")
    booking = Booking(
        user_id=user_id,
        showtime_id=showtime_id,
        total_price=Decimal(str(showtime.base_price)) * len(seat_ids),
        status="PENDING",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=HOLD_MINUTES),
        seats=[BookingSeat(showtime_id=showtime_id, seat_id=seat_id) for seat_id in seat_ids],
    )
    db.add(booking)
    await db.execute(
        delete(SeatHold).where(
            SeatHold.showtime_id == showtime_id,
            SeatHold.user_id == user_id,
            SeatHold.seat_id.in_(seat_ids),
        )
    )
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
