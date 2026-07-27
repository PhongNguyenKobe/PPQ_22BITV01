from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
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

router = APIRouter()


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
