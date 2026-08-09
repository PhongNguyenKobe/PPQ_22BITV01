from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commerce import NotificationOutbox


def enqueue_notification(
    db: AsyncSession,
    user_id: UUID,
    event_type: str,
    payload: dict,
) -> None:
    db.add(NotificationOutbox(
        user_id=user_id,
        event_type=event_type,
        channel="EMAIL",
        payload=payload,
        status="PENDING",
        available_at=datetime.now(timezone.utc),
    ))
