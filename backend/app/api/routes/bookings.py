from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.booking import (
    list_showtime_available_seats,
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
    seats = await list_showtime_available_seats(db, payload.showtime_id)
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
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to create booking"
        )
    
    # Validate showtime
    if not await validate_showtime_exists(db, payload.showtime_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Showtime not found or not open for booking"
        )
    
    # Validate seats
    is_valid, message = await validate_seats_available(db, payload.showtime_id, payload.seat_ids)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # TODO: Create booking in database
    # This is a placeholder response
    return BookingRead(
        id=UUID('00000000-0000-0000-0000-000000000001'),
        user_id=current_user.id,
        showtime_id=payload.showtime_id,
        movie_id=UUID('00000000-0000-0000-0000-000000000002'),
        booking_date=None,
        seats=[
            {"row": "A", "number": 1},
            {"row": "A", "number": 2},
        ],
        quantity=payload.quantity,
        total_price=payload.total_price,
        status="PENDING",
        created_at=None,
    )


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
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # TODO: Fetch bookings from database
    return BookingListResponse(
        total=0,
        page=skip // limit,
        limit=limit,
        bookings=[]
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
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # TODO: Fetch booking from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Booking not found"
    )
