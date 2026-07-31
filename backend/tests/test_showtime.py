from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest import TestCase

from app.crud.showtime import effective_showtime_status, is_showtime_bookable


class ShowtimeAvailabilityTests(TestCase):
    def test_past_showtime_is_never_bookable_even_with_bad_close_time(self):
        now = datetime.now(timezone.utc)
        showtime = SimpleNamespace(
            status="OPEN",
            starts_at=now - timedelta(hours=2),
            ends_at=now - timedelta(minutes=10),
            booking_closes_at=now + timedelta(days=1),
        )

        self.assertEqual(effective_showtime_status(showtime, now), "FINISHED")
        self.assertFalse(is_showtime_bookable(showtime, now))

    def test_started_showtime_is_not_bookable(self):
        now = datetime.now(timezone.utc)
        showtime = SimpleNamespace(
            status="OPEN",
            starts_at=now - timedelta(minutes=1),
            ends_at=now + timedelta(hours=2),
            booking_closes_at=now + timedelta(hours=1),
        )

        self.assertEqual(effective_showtime_status(showtime, now), "IN_PROGRESS")
        self.assertFalse(is_showtime_bookable(showtime, now))

    def test_future_open_showtime_is_bookable(self):
        now = datetime.now(timezone.utc)
        showtime = SimpleNamespace(
            status="OPEN",
            starts_at=now + timedelta(hours=2),
            ends_at=now + timedelta(hours=4),
            booking_closes_at=now + timedelta(hours=1, minutes=45),
        )

        self.assertEqual(effective_showtime_status(showtime, now), "OPEN")
        self.assertTrue(is_showtime_bookable(showtime, now))
