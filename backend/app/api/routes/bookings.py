from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.crud.booking import (
    list_showtime_available_seats,
    booking_to_dict,
    create_user_booking,
    get_user_booking,
    list_user_booking_rows,
    validate_showtime_exists,
    validate_seats_available,
)
from app.db.session import get_db
from app.schemas.booking import (
    SeatBookRequest,
    SeatBookResponse,
    BookingCreate,
    BookingRead,
    BookingListResponse,
)
from app.models.user import User
from app.models.commerce import Booking, Ticket
from app.models.catalog import Auditorium, Branch, Movie, Showtime

router = APIRouter()


@router.get("/tickets/verify/{scan_code}")
async def verify_public_ticket(scan_code: str, db: AsyncSession = Depends(get_db)):
    """Read-only phone view; intentionally excludes customer personal data."""
    from app.core.tickets import parse_ticket_scan_code, ticket_checkin_state

    try:
        normalized = parse_ticket_scan_code(scan_code)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found") from None
    row = (await db.execute(
        select(Ticket, Booking, Showtime, Movie, Auditorium, Branch)
        .join(Booking, Booking.id == Ticket.booking_id)
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .join(Movie, Movie.id == Showtime.movie_id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .join(Branch, Branch.id == Auditorium.branch_id)
        .where(Ticket.scan_code == normalized)
    )).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket, booking, showtime, movie, auditorium, branch = row
    booking_tickets = list((await db.execute(
        select(Ticket).where(Ticket.booking_id == booking.id).order_by(Ticket.ticket_code)
    )).scalars().all())
    state = ticket_checkin_state(booking.status, showtime.ends_at, None, datetime.now(timezone.utc), showtime.starts_at)
    if any(item.status == "CANCELLED" for item in booking_tickets): state = "CANCELLED"
    elif booking_tickets and all(item.status == "USED" for item in booking_tickets): state = "ALREADY_USED"
    return {"ticket_code": booking.ticket_code, "state": state, "movie_title": movie.title,
            "poster_url": movie.poster_url, "branch_name": branch.name,
            "auditorium_name": auditorium.name,
            "seats": [f"{item.seat_row}{item.seat_number}" for item in booking_tickets],
            "starts_at": showtime.starts_at, "ends_at": showtime.ends_at}


@router.put("/{booking_id}/cancel-request")
async def request_booking_cancellation(
    booking_id: UUID,
    reason: str = Query(min_length=5, max_length=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    booking = await get_user_booking(db, booking_id, current_user.id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking.status == "CANCEL_REQUESTED":
        return {"id": booking.id, "status": booking.status, "reason": booking.cancellation_reason}
    if booking.status != "CONFIRMED":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only a confirmed booking can request cancellation")
    
    payment_time = booking.created_at
    successful_payment = next(
        (payment for payment in booking.payments if payment.status == "SUCCESS"),
        None,
    )
    if successful_payment:
        payment_time = successful_payment.created_at

    if payment_time.tzinfo is None:
        payment_time = payment_time.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > payment_time + timedelta(hours=24):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cancellation can only be requested within 24 hours of payment",
        )

    starts_at = booking.showtime.starts_at
    if starts_at.tzinfo is None:
        starts_at = starts_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) >= starts_at:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot request cancellation for a showtime that has already started",
        )
    booking.status = "CANCEL_REQUESTED"
    booking.cancellation_reason = reason.strip()
    booking.cancellation_requested_at = datetime.now(timezone.utc)
    booking.cancellation_review_note = None
    booking.cancellation_reviewed_at = None
    booking.cancellation_reviewed_by = None
    await db.commit()
    return {"id": booking.id, "status": booking.status, "reason": booking.cancellation_reason}


@router.post("/seats", response_model=list[SeatBookResponse])
async def get_showtime_seats(
    payload: SeatBookRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SeatBookResponse]:
    """
    Get available seats for a specific showtime.
    
    - **showtime_id**: UUID of the showtime
    - Returns: List of seats with booking status
    """
    # Validate showtime exists
    if not await validate_showtime_exists(db, payload.showtime_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Showtime not found or not open for booking"
        )
    
    # Get available seats
    seats = await list_showtime_available_seats(db, payload.showtime_id, current_user.id)
    return [SeatBookResponse(**seat) for seat in seats]


@router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingRead:
    """
    Create a new booking (reserve seats for a showtime).
    
    - **showtime_id**: UUID of the showtime
    - **seat_ids**: List of seat UUIDs to book
    - **quantity**: Number of tickets (1-10)
    - **total_price**: Total booking price
    - Returns: Booking confirmation
    """
    if idempotency_key:
        idempotency_key = idempotency_key.strip()
        if not idempotency_key or len(idempotency_key) > 100:
            raise HTTPException(status_code=422, detail="Invalid Idempotency-Key")
        existing_id = await db.scalar(select(Booking.id).where(
            Booking.user_id == current_user.id,
            Booking.idempotency_key == idempotency_key,
        ))
        if existing_id:
            existing = await get_user_booking(db, existing_id, current_user.id)
            return BookingRead(**booking_to_dict(existing))

    # Validate showtime
    if not await validate_showtime_exists(db, payload.showtime_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Showtime not found or not open for booking"
        )
    
    # Validate seats
    is_valid, message = await validate_seats_available(db, payload.showtime_id, payload.seat_ids, current_user.id)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    if payload.quantity != len(payload.seat_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="quantity must match seat_ids")
    combo_items = {item.combo_id: item.quantity for item in payload.combo_items}
    if len(combo_items) != len(payload.combo_items):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate combos are not allowed")
    try:
        booking = await create_user_booking(
            db, current_user.id, payload.showtime_id, payload.seat_ids, combo_items, idempotency_key
        )
    except ValueError as exc:
        if str(exc) == "SHOWTIME_UNAVAILABLE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Showtime has started, ended, or is no longer open for booking",
            ) from None
        if str(exc) == "SEAT_HOLD_REQUIRED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Your seat hold expired. Please select the seats again.",
            ) from None
        if str(exc) == "COMBO_UNAVAILABLE":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Combo is unavailable at this branch") from None
        if str(exc).startswith("COMBO_OUT_OF_STOCK:"):
            combo_name = str(exc).split(":", 1)[1]
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Combo {combo_name} is out of stock") from None
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="One or more seats are already booked") from None
    return BookingRead(**booking_to_dict(booking))


@router.get("", response_model=BookingListResponse)
async def list_user_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingListResponse:
    """
    Get all bookings for current user with pagination.
    
    - **skip**: Number of bookings to skip
    - **limit**: Maximum number of bookings to return (1-100)
    - Returns: Paginated list of user's bookings
    """
    total, rows = await list_user_booking_rows(db, current_user.id, skip, limit)
    return BookingListResponse(
        total=total,
        page=(skip // limit) + 1,
        limit=limit,
        bookings=[BookingRead(**booking_to_dict(item)) for item in rows],
    )


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingRead:
    """
    Get detailed information about a specific booking.
    
    - **booking_id**: UUID of the booking
    - Returns: Booking details
    """
    booking = await get_user_booking(db, booking_id, current_user.id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return BookingRead(**booking_to_dict(booking))
