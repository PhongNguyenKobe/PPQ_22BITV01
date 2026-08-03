from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID


def ticket_code_prefix(branch_code: str, starts_at: datetime) -> str:
    branch = re.sub(r"[^A-Z0-9]", "", branch_code.upper())[:5] or "RAP"
    return f"{branch}{starts_at:%y%m%d}"


def build_ticket_code(branch_code: str, starts_at: datetime, daily_sequence: int) -> str:
    if not 1 <= daily_sequence <= 999:
        raise ValueError("DAILY_TICKET_CAPACITY_EXCEEDED")
    return f"{ticket_code_prefix(branch_code, starts_at)}{daily_sequence:03d}"


def ticket_qr_payload(ticket_code: str) -> str:
    return ticket_code.upper()


def parse_ticket_qr_payload(value: str) -> str:
    token = value.strip().upper()
    if token.startswith("CINEAI:T:"):
        token = token.removeprefix("CINEAI:T:")
    if not re.fullmatch(r"[A-Z0-9]{1,5}\d{9}", token):
        raise ValueError("INVALID_TICKET_CODE")
    return token


def ticket_checkin_state(
    booking_status: str,
    ends_at: datetime,
    checked_in_at: datetime | None,
    now: datetime,
) -> str:
    if booking_status in {"CANCELLED", "CANCEL_REQUESTED", "EXPIRED"}:
        return booking_status
    if booking_status != "CONFIRMED":
        return "NOT_CONFIRMED"
    if checked_in_at is not None:
        return "ALREADY_USED"
    if now > ends_at:
        return "EXPIRED"
    return "VALID"
