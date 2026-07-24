from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.movie import list_showtime_seats
from app.db.session import get_db
from app.models.catalog import Seat
from app.schemas.movie import SeatRead

router = APIRouter()


def _seat_to_read(seat: Seat) -> SeatRead:
    return SeatRead(
        id=seat.id,
        seat_row=seat.seat_row,
        seat_number=seat.seat_number,
        seat_type=seat.seat_type.code if seat.seat_type else "STANDARD",
        is_active=seat.is_active,
        status="available",
    )


@router.get("/{showtime_id}/seats", response_model=list[SeatRead])
async def read_showtime_seats(showtime_id: UUID, db: AsyncSession = Depends(get_db)) -> list[SeatRead]:
    seats = await list_showtime_seats(db, showtime_id)
    return [_seat_to_read(seat) for seat in seats]
