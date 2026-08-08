from __future__ import annotations

import re
import base64
import hashlib
import hmac
import secrets
import string
from datetime import datetime, timedelta
from uuid import UUID
from urllib.parse import urlparse

from app.core.config import settings


def ticket_code_prefix(branch_code: str, starts_at: datetime) -> str:
    branch = re.sub(r"[^A-Z0-9]", "", branch_code.upper())[:5] or "RAP"
    return f"{branch}{starts_at:%y%m%d}"


def build_ticket_code(branch_code: str, starts_at: datetime, daily_sequence: int) -> str:
    if not 1 <= daily_sequence <= 999:
        raise ValueError("DAILY_TICKET_CAPACITY_EXCEEDED")
    return f"{ticket_code_prefix(branch_code, starts_at)}{daily_sequence:03d}"


def ticket_qr_payload(ticket_code: str) -> str:
    return ticket_code.upper()


def new_ticket_scan_code() -> str:
    """Opaque 12-character lookup token (~57 bits) for a compact QR."""
    alphabet = string.ascii_uppercase + string.digits
    return "Q" + "".join(secrets.choice(alphabet) for _ in range(11))


def parse_ticket_scan_code(value: str) -> str:
    raw = value.strip()
    if "://" in raw:
        raw = urlparse(raw).path.rstrip("/").rsplit("/", 1)[-1]
    token = raw.upper()
    if not re.fullmatch(r"Q[A-Z0-9]{11}", token):
        raise ValueError("INVALID_TICKET_SCAN_CODE")
    return token


def parse_ticket_qr_payload(value: str) -> str:
    token = value.strip().upper()
    if token.startswith("CINEAI:T:"):
        token = token.removeprefix("CINEAI:T:")
    if not re.fullmatch(r"[A-Z0-9]{1,5}\d{9}(?:-\d{2})?", token):
        raise ValueError("INVALID_TICKET_CODE")
    return token


def compact_ticket_qr_payload(ticket_code: str, nonce: str) -> str:
    code = ticket_code.upper()
    digest = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        f"{code}.{nonce}".encode("utf-8"),
        hashlib.sha256,
    ).digest()[:10]
    signature = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"S1.{code}.{signature}"


def parse_compact_ticket_qr(value: str) -> tuple[str, str]:
    parts = value.strip().split(".")
    if len(parts) != 3 or parts[0].upper() != "S1":
        raise ValueError("INVALID_TICKET_QR")
    code = parse_ticket_qr_payload(parts[1])
    if not re.fullmatch(r"[A-Za-z0-9_-]{14}", parts[2]):
        raise ValueError("INVALID_TICKET_QR")
    return code, parts[2]


def verify_compact_ticket_qr(ticket_code: str, nonce: str, signature: str) -> bool:
    expected = compact_ticket_qr_payload(ticket_code, nonce).rsplit(".", 1)[1]
    return hmac.compare_digest(expected, signature)


def signed_ticket_qr_payload(ticket_id: UUID, nonce: str) -> str:
    body = f"T1.{ticket_id.hex}.{nonce}"
    digest = hmac.new(
        settings.jwt_secret_key.encode("utf-8"), body.encode("utf-8"), hashlib.sha256
    ).digest()[:16]
    signature = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"{body}.{signature}"


def parse_signed_ticket_qr(value: str) -> UUID:
    parts = value.strip().split(".")
    if len(parts) != 4 or parts[0] != "T1" or not re.fullmatch(r"[a-fA-F0-9]{32}", parts[1]):
        raise ValueError("INVALID_TICKET_QR")
    body = ".".join(parts[:3])
    expected = hmac.new(
        settings.jwt_secret_key.encode("utf-8"), body.encode("utf-8"), hashlib.sha256
    ).digest()[:16]
    expected_signature = base64.urlsafe_b64encode(expected).decode("ascii").rstrip("=")
    if not hmac.compare_digest(expected_signature, parts[3]):
        raise ValueError("INVALID_TICKET_QR")
    return UUID(hex=parts[1])


def ticket_checkin_state(
    booking_status: str,
    ends_at: datetime,
    checked_in_at: datetime | None,
    now: datetime,
    starts_at: datetime | None = None,
) -> str:
    if booking_status in {"CANCELLED", "CANCEL_REQUESTED", "EXPIRED"}:
        return booking_status
    if booking_status != "CONFIRMED":
        return "NOT_CONFIRMED"
    if checked_in_at is not None:
        return "ALREADY_USED"
    if starts_at is not None and now < starts_at - timedelta(minutes=60):
        return "TOO_EARLY"
    if now > ends_at:
        return "EXPIRED"
    return "VALID"
