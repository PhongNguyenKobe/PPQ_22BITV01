from datetime import datetime, timezone

from app.models.catalog import Showtime


def effective_showtime_status(showtime: Showtime, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    if showtime.status in {"DRAFT", "CANCELLED"}:
        return showtime.status
    if now >= showtime.ends_at:
        return "FINISHED"
    if now >= showtime.starts_at:
        return "IN_PROGRESS"
    if now >= showtime.booking_closes_at:
        return "SALES_CLOSED"
    return "OPEN"


def is_showtime_bookable(showtime: Showtime, now: datetime | None = None) -> bool:
    return effective_showtime_status(showtime, now) == "OPEN"
