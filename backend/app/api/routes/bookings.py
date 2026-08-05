from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
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
from app.models.commerce import BookingCombo, Combo
from app.models.catalog import Auditorium, Showtime
from sqlalchemy import select
from decimal import Decimal

router = APIRouter()


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
    try:
        booking = await create_user_booking(db, current_user.id, payload.showtime_id, payload.seat_ids)
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
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="One or more seats are already booked") from None
    if payload.combo_items:
        branch_id = await db.scalar(
            select(Auditorium.branch_id).join(Showtime, Showtime.auditorium_id == Auditorium.id).where(Showtime.id == payload.showtime_id)
        )
        requested = {item.combo_id: item.quantity for item in payload.combo_items}
        combos = list((await db.execute(
            select(Combo).where(Combo.id.in_(requested), Combo.branch_id == branch_id, Combo.is_active.is_(True))
        )).scalars().all())
        if len(combos) != len(requested):
            raise HTTPException(status_code=400, detail="Một combo không còn bán tại chi nhánh này")
        combo_total = Decimal("0")
        for combo in combos:
            quantity = requested[combo.id]
            if combo.stock_quantity is not None and combo.stock_quantity < quantity:
                raise HTTPException(status_code=409, detail=f"Combo {combo.name} không đủ số lượng")
            line_total = combo.price * quantity
            combo_total += line_total
            db.add(BookingCombo(booking_id=booking.id, combo_id=combo.id, combo_name=combo.name, unit_price=combo.price, quantity=quantity, line_total=line_total))
        booking.subtotal_price += combo_total
        booking.total_price += combo_total
        await db.commit()
        booking = await get_user_booking(db, booking.id, current_user.id)
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
