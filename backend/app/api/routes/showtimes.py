from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.booking import (
    HOLD_MINUTES,
    hold_showtime_seats,
    list_showtime_available_seats,
    release_showtime_holds,
    validate_showtime_exists,
)
from app.db.session import get_db
from app.core.seat_events import seat_events
from app.models.catalog import Seat
from app.models.user import User
from app.schemas.booking import SeatHoldRequest, SeatHoldResponse
from app.schemas.movie import SeatRead

router = APIRouter()


@router.websocket("/{showtime_id}/ws")
async def seat_updates(websocket: WebSocket, showtime_id: UUID) -> None:
    await seat_events.connect(showtime_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        seat_events.disconnect(showtime_id, websocket)


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
async def read_showtime_seats(
    showtime_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SeatRead]:
    if not await validate_showtime_exists(db, showtime_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Showtime has started, ended, or is no longer open for booking",
        )
    seats = await list_showtime_available_seats(db, showtime_id, current_user.id)
    return [
        SeatRead(
            id=seat["id"],
            seat_row=seat["seat_row"],
            seat_number=seat["seat_number"],
            seat_type=seat["seat_type"],
            is_active=seat["is_active"],
            status=seat["status"],
        )
        for seat in seats
    ]


@router.post("/{showtime_id}/holds", response_model=SeatHoldResponse)
async def hold_seats(
    showtime_id: UUID,
    payload: SeatHoldRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SeatHoldResponse:
    try:
        expires_at = await hold_showtime_seats(db, showtime_id, current_user.id, payload.seat_ids)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from None
    await seat_events.broadcast(showtime_id, "SEATS_UPDATED")
    return SeatHoldResponse(
        showtime_id=showtime_id,
        seat_ids=payload.seat_ids,
        expires_at=expires_at,
        hold_seconds=HOLD_MINUTES * 60,
    )


@router.delete("/{showtime_id}/holds", status_code=status.HTTP_204_NO_CONTENT)
async def release_holds(
    showtime_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await release_showtime_holds(db, showtime_id, current_user.id)
    await seat_events.broadcast(showtime_id, "SEATS_UPDATED")
