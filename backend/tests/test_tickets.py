from datetime import datetime, timedelta, timezone
from unittest import TestCase
from app.core.tickets import (
    build_ticket_code,
    parse_ticket_qr_payload,
    ticket_checkin_state,
    ticket_qr_payload,
)


class TicketCodeTests(TestCase):
    def test_short_code_contains_branch_and_show_date(self):
        code = build_ticket_code(
            "Q1-HCM",
            datetime(2026, 8, 3, tzinfo=timezone.utc),
            12,
        )
        self.assertEqual(code, "Q1HCM260803012")
        self.assertEqual(parse_ticket_qr_payload(ticket_qr_payload(code)), code)

    def test_rejects_unknown_qr_format(self):
        with self.assertRaises(ValueError):
            parse_ticket_qr_payload("https://example.com/not-a-ticket")

    def test_checkin_states(self):
        now = datetime.now(timezone.utc)
        self.assertEqual(ticket_checkin_state("CONFIRMED", now + timedelta(hours=1), None, now), "VALID")
        self.assertEqual(ticket_checkin_state("CONFIRMED", now - timedelta(seconds=1), None, now), "EXPIRED")
        self.assertEqual(ticket_checkin_state("CONFIRMED", now + timedelta(hours=1), now, now), "ALREADY_USED")
        self.assertEqual(ticket_checkin_state("CANCELLED", now + timedelta(hours=1), None, now), "CANCELLED")
