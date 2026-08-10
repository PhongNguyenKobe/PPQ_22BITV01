"""Process the durable notification outbox.

Run periodically with: python scripts/process_notifications.py
"""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.commerce import NotificationOutbox
from app.models.user import User
from app.services.email import send_transactional_email, render_notification_email


async def main() -> None:
    async with AsyncSessionLocal() as db:
        rows = await db.execute(
            select(NotificationOutbox)
            .where(NotificationOutbox.status == "PENDING", NotificationOutbox.available_at <= datetime.now(timezone.utc))
            .order_by(NotificationOutbox.created_at)
            .limit(100)
            .with_for_update(skip_locked=True)
        )
        for item in rows.scalars().all():
            user = await db.get(User, item.user_id)
            subject, body = await render_notification_email(db, item.event_type, item.payload)
            sent = bool(user) and await asyncio.to_thread(send_transactional_email, user.email, subject, body)
            item.attempts += 1
            if sent:
                item.status = "SENT"
                item.sent_at = datetime.now(timezone.utc)
                item.last_error = None
            elif item.attempts >= 5:
                item.status = "FAILED"
                item.last_error = "Delivery failed after five attempts"
            else:
                item.available_at = datetime.now(timezone.utc) + timedelta(minutes=2 ** item.attempts)
                item.last_error = "Delivery failed; retry scheduled"
        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
