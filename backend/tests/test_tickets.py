from datetime import datetime, timedelta, timezone
from unittest import TestCase
from app.core.tickets import (
    compact_ticket_qr_payload,
    parse_compact_ticket_qr,
    build_ticket_code,
    parse_ticket_qr_payload,
    ticket_checkin_state,
    ticket_qr_payload,
    signed_ticket_qr_payload,
    parse_signed_ticket_qr,
    new_ticket_scan_code,
    parse_ticket_scan_code,
    verify_compact_ticket_qr,
)
from uuid import uuid4


class TicketCodeTests(TestCase):
    def test_short_code_contains_branch_and_show_date(self):
        code = build_ticket_code(
            "Q1-HCM",
            datetime(2026, 8, 3, tzinfo=timezone.utc),
            12,
        )
        self.assertEqual(code, "Q1HCM260803012")
        self.assertEqual(parse_ticket_qr_payload(ticket_qr_payload(code)), code)

    def test_short_per_seat_code_is_accepted(self):
        code = "H260808002-01"
        self.assertEqual(parse_ticket_qr_payload(ticket_qr_payload(code)), code)

    def test_compact_per_seat_qr_is_short_and_signed(self):
        payload = compact_ticket_qr_payload("H260808002-01", "nonce-value")
        code, signature = parse_compact_ticket_qr(payload)
        self.assertEqual(code, "H260808002-01")
        self.assertLessEqual(len(payload), 32)
        self.assertTrue(verify_compact_ticket_qr(code, "nonce-value", signature))
        self.assertFalse(verify_compact_ticket_qr(code, "wrong-nonce", signature))

    def test_opaque_scan_code_is_twelve_characters(self):
        code = new_ticket_scan_code()
        self.assertEqual(len(code), 12)
        self.assertEqual(parse_ticket_scan_code(code), code)

    def test_rejects_unknown_qr_format(self):
        with self.assertRaises(ValueError):
            parse_ticket_qr_payload("https://example.com/not-a-ticket")

    def test_signed_per_seat_qr_rejects_tampering(self):
        ticket_id = uuid4()
        payload = signed_ticket_qr_payload(ticket_id, "nonce-value")
        self.assertEqual(parse_signed_ticket_qr(payload), ticket_id)
        with self.assertRaises(ValueError):
            parse_signed_ticket_qr(payload[:-1] + ("A" if payload[-1] != "A" else "B"))

    def test_checkin_states(self):
        now = datetime.now(timezone.utc)
        self.assertEqual(ticket_checkin_state("CONFIRMED", now + timedelta(hours=1), None, now), "VALID")
        self.assertEqual(ticket_checkin_state("CONFIRMED", now - timedelta(seconds=1), None, now), "EXPIRED")
        self.assertEqual(ticket_checkin_state("CONFIRMED", now + timedelta(hours=1), now, now), "ALREADY_USED")
        self.assertEqual(ticket_checkin_state("CANCELLED", now + timedelta(hours=1), None, now), "CANCELLED")
        self.assertEqual(
            ticket_checkin_state(
                "CONFIRMED", now + timedelta(hours=4), None, now, now + timedelta(hours=3)
            ),
            "TOO_EARLY",
        )
