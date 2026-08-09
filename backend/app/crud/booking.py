from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import secrets
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.tickets import build_ticket_code, new_ticket_scan_code, ticket_code_prefix, ticket_qr_payload
from app.core.config import settings
from app.models.catalog import Auditorium, Branch, Seat, Showtime
from app.models.commerce import Booking, BookingCombo, BookingSeat, Combo, Payment, PricingRule, SeatHold, Ticket

HOLD_MINUTES = 5
SINGLE_SEAT_GAP_MESSAGE = (
    "Không thể để lại một ghế trống riêng lẻ. Vui lòng chọn ghế liền nhau."
)


def _single_available_seats(
    seats: list[tuple[UUID, str, int]],
    unavailable_ids: set[UUID],
) -> set[UUID]:
    """Return available seats that form a one-seat run within a physical row segment."""
    single_seats: set[UUID] = set()
    rows: dict[str, list[tuple[UUID, int]]] = {}
    for seat_id, seat_row, seat_number in seats:
        rows.setdefault(seat_row, []).append((seat_id, seat_number))

    for row_seats in rows.values():
        ordered = sorted(row_seats, key=lambda item: item[1])
        segment: list[tuple[UUID, int]] = []
        for seat in ordered:
            if segment and seat[1] != segment[-1][1] + 1:
                _collect_single_available_seat(segment, unavailable_ids, single_seats)
                segment = []
            segment.append(seat)
        _collect_single_available_seat(segment, unavailable_ids, single_seats)
    return single_seats


def _collect_single_available_seat(
    segment: list[tuple[UUID, int]],
    unavailable_ids: set[UUID],
    result: set[UUID],
) -> None:
    available_run: list[UUID] = []
    for seat_id, _ in segment:
        if seat_id in unavailable_ids:
            if len(available_run) == 1:
                result.add(available_run[0])
            available_run = []
        else:
            available_run.append(seat_id)
    if len(available_run) == 1:
        result.add(available_run[0])


def leaves_new_single_seat_gap(
    seats: list[tuple[UUID, str, int]],
    unavailable_ids: set[UUID],
    selected_ids: set[UUID],
) -> bool:
    """Only reject a singleton created by this selection, not one already present."""
    before = _single_available_seats(seats, unavailable_ids)
    after = _single_available_seats(seats, unavailable_ids | selected_ids)
    return bool(after - before)


async def cleanup_expired_reservations(db: AsyncSession) -> None:
    now = datetime.now(timezone.utc)
    await db.execute(delete(SeatHold).where(SeatHold.expires_at <= now))
    expired_result = await db.execute(
        select(Booking).where(
            Booking.status == "PENDING",
            Booking.expires_at.is_not(None),
            Booking.expires_at <= now,
        )
    )
    expired = list(expired_result.scalars().all())
    if expired:
        ids = [item.id for item in expired]
        await release_booking_combo_inventory(db, ids)
        seat_rows = await db.execute(
            select(BookingSeat)
            .options(selectinload(BookingSeat.seat))
            .where(BookingSeat.booking_id.in_(ids))
        )
        seats_by_booking: dict[UUID, list[dict]] = {}
        for item in seat_rows.scalars().all():
            seats_by_booking.setdefault(item.booking_id, []).append({
                "id": str(item.seat_id),
                "row": item.seat.seat_row,
                "number": item.seat.seat_number,
            })
        await db.execute(delete(BookingSeat).where(BookingSeat.booking_id.in_(ids)))
        for booking in expired:
            if not booking.seat_snapshot:
                booking.seat_snapshot = seats_by_booking.get(booking.id, [])
            booking.status = "EXPIRED"
        pending_payments = await db.execute(
            select(Payment).where(Payment.booking_id.in_(ids), Payment.status == "PENDING")
        )
        for payment in pending_payments.scalars().all():
            payment.status = "EXPIRED"
    await db.flush()


async def release_booking_combo_inventory(
    db: AsyncSession,
    booking_ids: list[UUID],
    *,
    include_sold: bool = False,
) -> None:
    if not booking_ids:
        return
    statuses = ["RESERVED", "SOLD"] if include_sold else ["RESERVED"]
    rows = await db.execute(
        select(BookingCombo)
        .where(BookingCombo.booking_id.in_(booking_ids), BookingCombo.inventory_status.in_(statuses))
        .order_by(BookingCombo.combo_id)
        .with_for_update()
    )
    for item in rows.scalars().all():
        combo = await db.get(Combo, item.combo_id, with_for_update=True)
        if combo is not None and combo.stock_quantity is not None:
            combo.stock_quantity += item.quantity
        item.inventory_status = "RELEASED"
    await db.flush()


async def confirm_booking_combo_inventory(db: AsyncSession, booking_id: UUID) -> None:
    rows = await db.execute(
        select(BookingCombo)
        .where(BookingCombo.booking_id == booking_id, BookingCombo.inventory_status == "RESERVED")
        .with_for_update()
    )
    for item in rows.scalars().all():
        item.inventory_status = "SOLD"
    await db.flush()


async def issue_booking_ticket(db: AsyncSession, booking: Booking) -> str:
    """Issue a ticket only after a payment has been verified."""
    showtime = await db.get(Showtime, booking.showtime_id)
    if showtime is None:
        raise ValueError("SHOWTIME_NOT_FOUND")
    branch = (
        await db.execute(
            select(Branch)
            .join(Auditorium, Auditorium.branch_id == Branch.id)
            .where(Auditorium.id == showtime.auditorium_id)
            .with_for_update()
        )
    ).scalar_one()
    if not booking.ticket_code:
        prefix = ticket_code_prefix(branch.code, showtime.starts_at)
        latest_code = await db.scalar(
            select(Booking.ticket_code)
            .where(Booking.ticket_code.like(f"{prefix}%"))
            .order_by(Booking.ticket_code.desc())
            .limit(1)
        )
        sequence = int(latest_code[-3:]) + 1 if latest_code else 1
        booking.ticket_code = build_ticket_code(branch.code, showtime.starts_at, sequence)
        await db.flush()
    seat_result = await db.execute(
        select(BookingSeat)
        .options(selectinload(BookingSeat.seat))
        .where(BookingSeat.booking_id == booking.id)
        .order_by(BookingSeat.id)
    )
    for position, booking_seat in enumerate(seat_result.scalars().all(), start=1):
        existing_ticket = await db.scalar(
            select(Ticket.id).where(Ticket.booking_seat_id == booking_seat.id)
        )
        if existing_ticket is not None:
            continue
        db.add(Ticket(
            id=uuid4(), booking_id=booking.id, booking_seat_id=booking_seat.id,
            seat_id=booking_seat.seat_id,
            unit_price=booking_seat.unit_price,
            pricing_details=booking_seat.pricing_details,
            ticket_code=f"{booking.ticket_code}-{position:02d}",
            scan_code=new_ticket_scan_code(),
            qr_nonce=secrets.token_hex(16),
            seat_row=booking_seat.seat.seat_row,
            seat_number=booking_seat.seat.seat_number,
            status="ISSUED",
        ))
    await db.flush()
    return booking.ticket_code


async def list_showtime_available_seats(db: AsyncSession, showtime_id: UUID, user_id: UUID | None = None) -> list[dict]:
    await cleanup_expired_reservations(db)
    showtime = await db.get(Showtime, showtime_id)
    base_price = Decimal(str(showtime.base_price)) if showtime else Decimal("0")
    result = await db.execute(
        select(Seat)
        .options(selectinload(Seat.seat_type))
        .join(Showtime, Showtime.auditorium_id == Seat.auditorium_id)
        .where(Showtime.id == showtime_id, Seat.is_active.is_(True))
        .order_by(Seat.seat_row, Seat.seat_number)
    )
    seats = list(result.scalars().all())
    booked_result = await db.execute(
        select(BookingSeat.seat_id)
        .join(Booking, Booking.id == BookingSeat.booking_id)
        .where(BookingSeat.showtime_id == showtime_id, Booking.status.in_(["PENDING", "CONFIRMED"]))
    )
    booked_ids = set(booked_result.scalars().all())
    holds_result = await db.execute(
        select(SeatHold.seat_id, SeatHold.user_id).where(
            SeatHold.showtime_id == showtime_id,
            SeatHold.expires_at > datetime.now(timezone.utc),
        )
    )
    holds = {row.seat_id: row.user_id for row in holds_result.all()}
    return [
        {
            "id": seat.id,
            "seat_row": seat.seat_row,
            "seat_number": seat.seat_number,
            "seat_type": seat.seat_type.code if seat.seat_type else "STANDARD",
            "is_active": seat.is_active,
            "is_booked": seat.id in booked_ids,
            "status": (
                "BOOKED"
                if seat.id in booked_ids
                else "HELD_BY_ME"
                if holds.get(seat.id) == user_id
                else "HOLD"
                if seat.id in holds
                else "AVAILABLE"
            ),
            "price": (
                Decimal(str(seat.seat_type.price_multiplier if seat.seat_type else 1))
                * base_price
            ),
        }
        for seat in seats
    ]


async def validate_showtime_exists(db: AsyncSession, showtime_id: UUID) -> bool:
    result = await db.execute(
        select(Showtime.id).where(
            Showtime.id == showtime_id,
            Showtime.status == "OPEN",
            Showtime.starts_at > func.now(),
            Showtime.booking_closes_at > func.now(),
        )
    )
    return result.scalar_one_or_none() is not None


async def validate_seats_available(
    db: AsyncSession,
    showtime_id: UUID,
    seat_ids: list[UUID],
    user_id: UUID | None = None,
    *,
    enforce_single_seat_gap: bool = True,
) -> tuple[bool, str]:
    await cleanup_expired_reservations(db)
    unique_ids = set(seat_ids)
    if not unique_ids:
        return False, "No seats selected"
    if len(unique_ids) != len(seat_ids):
        return False, "Duplicate seats are not allowed"
    if len(unique_ids) > 10:
        return False, "Maximum 10 seats per booking"

    showtime = await db.get(Showtime, showtime_id)
    if showtime is None:
        return False, "Showtime not found"
    result = await db.execute(
        select(Seat).where(
            Seat.id.in_(unique_ids),
            Seat.auditorium_id == showtime.auditorium_id,
            Seat.is_active.is_(True),
        )
    )
    if len(result.scalars().all()) != len(unique_ids):
        return False, "One or more seats are invalid for this showtime"
    booked = await db.execute(
        select(func.count(BookingSeat.id))
        .join(Booking, Booking.id == BookingSeat.booking_id)
        .where(
            BookingSeat.showtime_id == showtime_id,
            BookingSeat.seat_id.in_(unique_ids),
            Booking.status.in_(["PENDING", "CONFIRMED"]),
        )
    )
    if (booked.scalar() or 0) > 0:
        return False, "One or more seats are already booked"
    held = await db.execute(
        select(func.count(SeatHold.id)).where(
            SeatHold.showtime_id == showtime_id,
            SeatHold.seat_id.in_(unique_ids),
            SeatHold.expires_at > datetime.now(timezone.utc),
            SeatHold.user_id != user_id if user_id else SeatHold.user_id.is_not(None),
        )
    )
    if (held.scalar() or 0) > 0:
        return False, "One or more seats are temporarily held by another customer"

    if enforce_single_seat_gap:
        all_seats_result = await db.execute(
            select(Seat.id, Seat.seat_row, Seat.seat_number).where(
                Seat.auditorium_id == showtime.auditorium_id,
                Seat.is_active.is_(True),
            )
        )
        booked_ids_result = await db.execute(
            select(BookingSeat.seat_id)
            .join(Booking, Booking.id == BookingSeat.booking_id)
            .where(
                BookingSeat.showtime_id == showtime_id,
                Booking.status.in_(["PENDING", "CONFIRMED"]),
            )
        )
        held_ids_result = await db.execute(
            select(SeatHold.seat_id).where(
                SeatHold.showtime_id == showtime_id,
                SeatHold.expires_at > datetime.now(timezone.utc),
                SeatHold.user_id != user_id if user_id else SeatHold.user_id.is_not(None),
            )
        )
        unavailable_ids = set(booked_ids_result.scalars().all()) | set(
            held_ids_result.scalars().all()
        )
        seats = [(row.id, row.seat_row, row.seat_number) for row in all_seats_result.all()]
        if leaves_new_single_seat_gap(seats, unavailable_ids, unique_ids):
            return False, SINGLE_SEAT_GAP_MESSAGE
    return True, "Seats are available"


async def hold_showtime_seats(
    db: AsyncSession,
    showtime_id: UUID,
    user_id: UUID,
    seat_ids: list[UUID],
) -> datetime:
    if not await validate_showtime_exists(db, showtime_id):
        raise ValueError("SHOWTIME_UNAVAILABLE")
    valid, message = await validate_seats_available(
        db,
        showtime_id,
        seat_ids,
        user_id,
        enforce_single_seat_gap=False,
    )
    if not valid:
        raise ValueError(message)
    await db.execute(
        delete(SeatHold).where(
            SeatHold.showtime_id == showtime_id,
            SeatHold.user_id == user_id,
        )
    )
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=HOLD_MINUTES)
    db.add_all(
        [
            SeatHold(showtime_id=showtime_id, seat_id=seat_id, user_id=user_id, expires_at=expires_at)
            for seat_id in seat_ids
        ]
    )
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("One or more seats were just held by another customer") from None
    return expires_at


async def release_showtime_holds(db: AsyncSession, showtime_id: UUID, user_id: UUID) -> None:
    await db.execute(
        delete(SeatHold).where(SeatHold.showtime_id == showtime_id, SeatHold.user_id == user_id)
    )
    await db.commit()


def booking_to_dict(booking: Booking) -> dict:
    showtime = booking.showtime
    movie = showtime.movie
    auditorium = showtime.auditorium
    successful_payment = next(
        (payment for payment in booking.payments if payment.status == "SUCCESS"),
        None,
    )
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "showtime_id": booking.showtime_id,
        "movie_id": showtime.movie_id,
        "movie_title": movie.title,
        "poster_url": movie.poster_url,
        "branch_name": auditorium.branch.name,
        "auditorium_name": auditorium.name,
        "starts_at": showtime.starts_at,
        "ends_at": showtime.ends_at,
        "booking_date": booking.created_at,
        "seats": (
            [{"row": item.seat.seat_row, "number": item.seat.seat_number} for item in booking.seats]
            or list(booking.seat_snapshot or [])
        ),
        "quantity": len(booking.seats) or len(booking.seat_snapshot or []),
        "total_price": booking.total_price,
        "subtotal_price": booking.subtotal_price,
        "discount_amount": booking.discount_amount,
        "promotion_code": booking.promotion.code if booking.promotion else None,
        "status": booking.status,
        "ticket_code": booking.ticket_code,
        "qr_code": (
            ticket_qr_payload(booking.ticket_code)
            if booking.status == "CONFIRMED" and booking.ticket_code
            else None
        ),
        "tickets": [
            {
                "id": str(ticket.id),
                "ticket_code": ticket.ticket_code,
                "seat": f"{ticket.seat_row}{ticket.seat_number}",
                "unit_price": ticket.unit_price,
                "pricing_details": ticket.pricing_details,
                "status": ticket.status,
                "qr_code": (
                    f"{settings.frontend_url.rstrip('/')}/t/{ticket.scan_code}"
                    if booking.status == "CONFIRMED" and ticket.status == "ISSUED"
                    else None
                ),
                "checked_in_at": ticket.checked_in_at,
            }
            for ticket in booking.tickets
        ],
        "checked_in_at": booking.checked_in_at,
        "cancellation_reason": booking.cancellation_reason,
        "cancellation_requested_at": booking.cancellation_requested_at,
        "cancelled_at": booking.cancelled_at,
        "payment_method": successful_payment.payment_method if successful_payment else None,
        "created_at": booking.created_at,
    }


async def get_user_booking(db: AsyncSession, booking_id: UUID, user_id: UUID) -> Booking | None:
    result = await db.execute(
        select(Booking)
        .options(
            selectinload(Booking.showtime).selectinload(Showtime.movie),
            selectinload(Booking.showtime).selectinload(Showtime.auditorium).selectinload(Auditorium.branch),
            selectinload(Booking.seats).selectinload(BookingSeat.seat),
            selectinload(Booking.payments),
            selectinload(Booking.promotion),
            selectinload(Booking.tickets),
        )
        .where(Booking.id == booking_id, Booking.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user_booking(
    db: AsyncSession,
    user_id: UUID,
    showtime_id: UUID,
    seat_ids: list[UUID],
    combo_items: dict[UUID, int] | None = None,
    idempotency_key: str | None = None,
    require_hold: bool = True,
    sales_channel: str = "ONLINE",
    customer: dict | None = None,
    commit: bool = True,
) -> Booking:
    await cleanup_expired_reservations(db)
    showtime_result = await db.execute(
        select(Showtime).where(
            Showtime.id == showtime_id,
            Showtime.status == "OPEN",
            Showtime.starts_at > func.now(),
            Showtime.booking_closes_at > func.now(),
        )
    )
    showtime = showtime_result.scalar_one_or_none()
    if showtime is None:
        raise ValueError("SHOWTIME_UNAVAILABLE")
    holds_result = await db.execute(
        select(SeatHold.seat_id).where(
            SeatHold.showtime_id == showtime_id,
            SeatHold.user_id == user_id,
            SeatHold.seat_id.in_(seat_ids),
            SeatHold.expires_at > datetime.now(timezone.utc),
        )
    )
    if require_hold and set(holds_result.scalars().all()) != set(seat_ids):
        raise ValueError("SEAT_HOLD_REQUIRED")
    seat_result = await db.execute(
        select(Seat).options(selectinload(Seat.seat_type)).where(
            Seat.id.in_(seat_ids),
            Seat.auditorium_id == showtime.auditorium_id,
            Seat.is_active.is_(True),
        )
    )
    seats = list(seat_result.scalars().all())
    if len(seats) != len(set(seat_ids)):
        raise ValueError("INVALID_SEATS")
    auditorium = await db.get(Auditorium, showtime.auditorium_id)
    rules_result = await db.execute(
        select(PricingRule).where(
            PricingRule.is_active.is_(True),
            (PricingRule.branch_id.is_(None)) | (PricingRule.branch_id == auditorium.branch_id),
        ).order_by(PricingRule.priority.desc())
    )
    local_start = showtime.starts_at.astimezone(ZoneInfo(settings.business_timezone))
    applicable_rules = [
        rule for rule in rules_result.scalars().all()
        if (rule.screen_type is None or rule.screen_type == auditorium.screen_type)
        and (rule.day_of_week is None or rule.day_of_week == local_start.weekday())
        and (rule.starts_on is None or rule.starts_on <= showtime.starts_at)
        and (rule.ends_on is None or rule.ends_on >= showtime.starts_at)
        and (rule.time_from is None or rule.time_from <= local_start.time().replace(tzinfo=None))
        and (rule.time_to is None or rule.time_to >= local_start.time().replace(tzinfo=None))
    ]
    pricing_rule = applicable_rules[0] if applicable_rules else None
    booking_seats: list[BookingSeat] = []
    subtotal = Decimal("0")
    for seat in seats:
        seat_multiplier = Decimal(str(seat.seat_type.price_multiplier if seat.seat_type else 1))
        rule_multiplier = Decimal(str(pricing_rule.multiplier)) if pricing_rule else Decimal("1")
        surcharge = Decimal(str(pricing_rule.surcharge)) if pricing_rule else Decimal("0")
        unit_price = (Decimal(str(showtime.base_price)) * seat_multiplier * rule_multiplier + surcharge).quantize(Decimal("0.01"))
        subtotal += unit_price
        booking_seats.append(BookingSeat(
            showtime_id=showtime_id,
            seat_id=seat.id,
            unit_price=unit_price,
            pricing_details={
                "base_price": str(showtime.base_price),
                "seat_multiplier": str(seat_multiplier),
                "pricing_rule_id": str(pricing_rule.id) if pricing_rule else None,
                "pricing_rule": pricing_rule.name if pricing_rule else None,
                "rule_multiplier": str(rule_multiplier),
                "surcharge": str(surcharge),
            },
        ))
    booking_combos: list[BookingCombo] = []
    requested = combo_items or {}
    if requested:
        branch_id = await db.scalar(
            select(Auditorium.branch_id).where(Auditorium.id == showtime.auditorium_id)
        )
        combo_result = await db.execute(
            select(Combo)
            .where(Combo.id.in_(requested), Combo.branch_id == branch_id, Combo.is_active.is_(True))
            .with_for_update()
        )
        combos = list(combo_result.scalars().all())
        if len(combos) != len(requested):
            raise ValueError("COMBO_UNAVAILABLE")
        for combo in combos:
            quantity = requested[combo.id]
            if combo.stock_quantity is not None and combo.stock_quantity < quantity:
                raise ValueError(f"COMBO_OUT_OF_STOCK:{combo.name}")
            if combo.stock_quantity is not None:
                combo.stock_quantity -= quantity
            line_total = Decimal(str(combo.price)) * quantity
            subtotal += line_total
            booking_combos.append(BookingCombo(
                combo_id=combo.id,
                combo_name=combo.name,
                unit_price=combo.price,
                quantity=quantity,
                line_total=line_total,
                inventory_status="RESERVED",
            ))

    booking_id = uuid4()
    booking = Booking(
        id=booking_id,
        user_id=user_id,
        idempotency_key=idempotency_key,
        sales_channel=sales_channel,
        customer_name=(customer or {}).get("name"),
        customer_email=(customer or {}).get("email"),
        customer_phone=(customer or {}).get("phone"),
        showtime_id=showtime_id,
        subtotal_price=subtotal,
        discount_amount=Decimal("0"),
        total_price=subtotal,
        status="PENDING",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=HOLD_MINUTES),
        ticket_code=None,
        seats=booking_seats,
        combos=booking_combos,
    )
    db.add(booking)
    await db.execute(
        delete(SeatHold).where(
            SeatHold.showtime_id == showtime_id,
            SeatHold.user_id == user_id,
            SeatHold.seat_id.in_(seat_ids),
        )
    )
    try:
        if commit:
            await db.commit()
        else:
            await db.flush()
    except IntegrityError:
        await db.rollback()
        raise ValueError("SEAT_ALREADY_BOOKED") from None
    return await get_user_booking(db, booking.id, user_id)


async def list_user_booking_rows(db: AsyncSession, user_id: UUID, skip: int, limit: int) -> tuple[int, list[Booking]]:
    total_result = await db.execute(select(func.count(Booking.id)).where(Booking.user_id == user_id))
    result = await db.execute(
        select(Booking)
        .options(
            selectinload(Booking.showtime).selectinload(Showtime.movie),
            selectinload(Booking.showtime).selectinload(Showtime.auditorium).selectinload(Auditorium.branch),
            selectinload(Booking.seats).selectinload(BookingSeat.seat),
            selectinload(Booking.payments),
            selectinload(Booking.promotion),
            selectinload(Booking.tickets),
        )
        .where(Booking.user_id == user_id)
        .order_by(Booking.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return total_result.scalar() or 0, list(result.scalars().all())
