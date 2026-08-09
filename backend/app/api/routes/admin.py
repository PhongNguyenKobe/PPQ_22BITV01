from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
import re
import json
import unicodedata
from uuid import UUID
import uuid
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy import case, delete, func, or_, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field

from app.api.deps import get_current_user, require_roles
from app.core.permissions import require_admin, require_branch_admin
from app.core.seat_events import seat_events
from app.crud.admin import get_live_admin_stats, list_users_with_branch_id, set_user_role
from app.crud.user import create_user, get_user_by_id, update_user
from app.crud.showtime import effective_showtime_status
from app.crud.booking import (
    confirm_booking_combo_inventory,
    create_user_booking,
    issue_booking_ticket,
    release_booking_combo_inventory,
)
from app.db.session import get_db
from app.models.catalog import Auditorium, Branch, Movie, MovieGenre, Seat, SeatType, Showtime, Vendor
from app.core.config import settings
from app.core.tickets import parse_compact_ticket_qr, parse_signed_ticket_qr, parse_ticket_qr_payload, parse_ticket_scan_code, ticket_checkin_state, verify_compact_ticket_qr
from app.models.commerce import AuditEvent, Booking, BookingCombo, BookingSeat, Combo, Payment, PaymentStatusHistory, PricingRule, Promotion, PromotionRedemption, Ticket
from app.services.vnpay import query_transaction, refund_transaction, verify_refund_response
from app.models.user import Role, User, user_roles_table
from app.schemas.admin import (
    AdminStatsResponse,
    AdminUserCreate,
    AdminUserRead,
    AdminUserUpdate,
    AuditoriumCreate,
    AuditoriumRead,
    AuditoriumUpdate,
    BranchManageCreate,
    BranchManageRead,
    BranchManageUpdate,
    BranchRead,
    MovieDraftPayload,
    SeatAdminCreate,
    SeatLayoutRead,
    SeatLayoutUpdate,
    SeatAdminRead,
    SeatAdminUpdate,
    SeatTypeRead,
    TmdbMovieImportPayload,
    TmdbMovieImportResponse,
    ShowtimeAdminCreate,
    ShowtimeBulkCreate,
    ShowtimeBulkPublish,
    ShowtimeAdminRead,
    ShowtimeAdminUpdate,
    UserRoleUpdate,
)


async def _execute_vnpay_refund(
    *,
    payment: Payment,
    booking: Booking,
    current_user: User,
    request: Request,
    db: AsyncSession,
    reason: str,
) -> Payment:
    old_status = payment.status
    if payment.status == "REFUNDED":
        return payment
    if payment.payment_method != "VNPAY":
        payment.status = "REFUND_PENDING"
        payment.refund_error = "Manual refund required for this payment method"
        db.add(PaymentStatusHistory(
            payment_id=payment.id, old_status=old_status, new_status=payment.status,
            source="REFUND", note=payment.refund_error, raw_payload={},
        ))
        await db.commit()
        return payment
    if payment.signature_valid is not True or not payment.provider_ref or not payment.provider_transaction_no:
        payment.status = "REFUND_FAILED"
        payment.refund_error = "VNPAY payment has not been verified or is missing provider transaction data"
        db.add(PaymentStatusHistory(
            payment_id=payment.id, old_status=old_status, new_status=payment.status,
            source="REFUND", note=payment.refund_error, raw_payload={},
        ))
        await db.commit()
        return payment
    if not settings.vnpay_enabled:
        payment.status = "REFUND_FAILED"
        payment.refund_error = "VNPAY is not configured"
        await db.commit()
        return payment

    request_id = uuid.uuid4().hex
    payment.status = "REFUND_PENDING"
    payment.refund_request_id = request_id
    payment.refund_attempts += 1
    payment.refund_requested_at = datetime.now(timezone.utc)
    payment.refund_error = None
    await db.commit()

    try:
        response = await refund_transaction(
            request_id=request_id,
            txn_ref=payment.provider_ref,
            amount=int(payment.amount),
            transaction_no=payment.provider_transaction_no,
            transaction_date=payment.created_at,
            created_by=current_user.id.hex,
            ip_address=request.client.host if request.client else "127.0.0.1",
            reason=reason,
        )
        signature_valid = verify_refund_response(response)
        response_code = str(response.get("vnp_ResponseCode", ""))
        provider_status = str(response.get("vnp_TransactionStatus", ""))
        payment.refund_response_code = response_code or None
        payment.refund_provider_status = provider_status or None
        payment.refund_transaction_no = str(response.get("vnp_TransactionNo", "")) or None

        if not signature_valid:
            payment.status = "REFUND_FAILED"
            payment.refund_error = "Invalid VNPAY refund response signature"
        elif response_code == "00" and provider_status == "00":
            payment.status = "REFUNDED"
            payment.refunded_at = datetime.now(timezone.utc)
            await _release_used_promotion(db, payment.id)
        elif response_code in {"00", "94"} or provider_status in {"05", "06"}:
            payment.status = "REFUND_PENDING"
            payment.refund_error = str(response.get("vnp_Message", "")) or "VNPAY is processing the refund"
        else:
            payment.status = "REFUND_FAILED"
            payment.refund_error = str(response.get("vnp_Message", "")) or f"VNPAY refund failed ({response_code})"

        db.add(PaymentStatusHistory(
            payment_id=payment.id,
            old_status=old_status,
            new_status=payment.status,
            source="VNPAY_REFUND",
            response_code=response_code or None,
            provider_status=provider_status or None,
            signature_valid=signature_valid,
            note=payment.refund_error or reason,
            raw_payload={str(key): str(value) for key, value in response.items()},
        ))
    except Exception as exc:
        payment.status = "REFUND_FAILED"
        payment.refund_error = f"Cannot reach VNPAY refund API: {exc}"
        db.add(PaymentStatusHistory(
            payment_id=payment.id, old_status=old_status, new_status=payment.status,
            source="VNPAY_REFUND", signature_valid=None,
            note=payment.refund_error, raw_payload={},
        ))
    await db.commit()
    return payment
from app.schemas.movie import MovieRead
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter()


async def _release_used_promotion(db: AsyncSession, payment_id: UUID) -> None:
    redemption = (await db.execute(
        select(PromotionRedemption)
        .where(PromotionRedemption.payment_id == payment_id)
        .with_for_update()
    )).scalar_one_or_none()
    if redemption is None or redemption.status != "USED":
        return
    promotion = await db.get(Promotion, redemption.promotion_id, with_for_update=True)
    redemption.status = "RELEASED"
    if promotion:
        promotion.used_count = max(0, promotion.used_count - 1)
        promotion.used_amount = max(0, promotion.used_amount - redemption.discount_amount)


class TicketScanRequest(BaseModel):
    qr_data: str = Field(min_length=1, max_length=100)
    consume: bool = False


class PosBookingRequest(BaseModel):
    showtime_id: UUID
    seat_ids: list[UUID] = Field(min_length=1, max_length=10)
    payment_method: str = Field(default="CASH", pattern="^(CASH|CARD_POS)$")
    customer_name: str | None = Field(default=None, max_length=150)
    customer_email: str | None = Field(default=None, max_length=255)
    customer_phone: str | None = Field(default=None, max_length=20)


class PricingRuleRequest(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    branch_id: UUID | None = None
    screen_type: str | None = None
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    starts_on: datetime | None = None
    ends_on: datetime | None = None
    time_from: time | None = None
    time_to: time | None = None
    multiplier: Decimal = Field(default=Decimal("1"), gt=0)
    surcharge: Decimal = Field(default=Decimal("0"))
    priority: int = 0
    is_active: bool = True


def _showtime_admin_read(
    item: Showtime,
    *,
    booking_count: int = 0,
    sold_seats: int = 0,
    revenue: float = 0,
) -> ShowtimeAdminRead:
    return ShowtimeAdminRead(
        id=item.id,
        movie_id=item.movie_id,
        movie_title=item.movie.title if item.movie else "",
        auditorium_id=item.auditorium_id,
        auditorium_name=item.auditorium.name if item.auditorium else "",
        branch_name=item.auditorium.branch.name if item.auditorium and item.auditorium.branch else "",
        starts_at=item.starts_at,
        ends_at=item.ends_at,
        status=effective_showtime_status(item),
        stored_status=item.status,
        booking_closes_at=item.booking_closes_at,
        cancellation_reason=item.cancellation_reason,
        base_price=float(item.base_price),
        booking_count=booking_count,
        sold_seats=sold_seats,
        revenue=revenue,
        total_seats=int(item.auditorium.total_seats or 0) if item.auditorium else 0,
        occupancy_rate=round((sold_seats / item.auditorium.total_seats) * 100, 1) if item.auditorium and item.auditorium.total_seats else 0,
        branch_is_active=bool(item.auditorium.branch.is_active) if item.auditorium and item.auditorium.branch else False,
        auditorium_is_active=bool(item.auditorium.is_active) if item.auditorium else False,
    )


async def _branch_id_map(db: AsyncSession) -> dict[UUID, UUID]:
    rows = await db.execute(text("SELECT user_id, branch_id FROM branch_staff WHERE is_active = TRUE"))
    return {row.user_id: row.branch_id for row in rows}


def _is_super_admin(user: User) -> bool:
    return any(role.code == "SUPER_ADMIN" for role in user.roles)


async def _staff_branch_id(db: AsyncSession, user: User) -> UUID | None:
    if _is_super_admin(user):
        return None
    row = await db.execute(
        text(
            "SELECT branch_id FROM branch_staff "
            "WHERE user_id = :user_id AND is_active = TRUE LIMIT 1"
        ),
        {"user_id": str(user.id)},
    )
    branch_id = row.scalar_one_or_none()
    if branch_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No active branch assignment")
    return branch_id


async def _ensure_branch_access(db: AsyncSession, user: User, branch_id: UUID) -> None:
    assigned_branch_id = await _staff_branch_id(db, user)
    if assigned_branch_id is not None and assigned_branch_id != branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot manage another branch")


async def _ensure_default_seat_types(db: AsyncSession) -> None:
    result = await db.execute(select(SeatType))
    if list(result.scalars().all()):
        return

    db.add_all(
        [
            SeatType(id=1, code="STANDARD", name="Standard"),
            SeatType(id=2, code="VIP", name="VIP"),
            SeatType(id=3, code="COUPLE", name="Couple"),
        ]
    )
    await db.commit()


CANONICAL_MOVIE_GENRES = {
    "Hành động", "Phiêu lưu", "Hoạt hình", "Hài", "Tội phạm", "Tài liệu",
    "Chính kịch", "Gia đình", "Kỳ ảo", "Lịch sử", "Kinh dị", "Âm nhạc",
    "Bí ẩn", "Lãng mạn", "Khoa học viễn tưởng", "Phim truyền hình",
    "Giật gân", "Chiến tranh", "Miền Tây",
}
CANONICAL_MOVIE_GENRES_BY_CASEFOLD = {
    value.casefold(): value for value in CANONICAL_MOVIE_GENRES
}


async def _resolve_genres(db: AsyncSession, values: list[str]) -> list[MovieGenre]:
    cleaned = list(dict.fromkeys(
        canonical
        for value in values
        if (canonical := CANONICAL_MOVIE_GENRES_BY_CASEFOLD.get(value.strip().casefold()))
    ))
    if not cleaned:
        return []
    result = await db.execute(
        select(MovieGenre).where(
            or_(MovieGenre.code.in_([value.upper() for value in cleaned]), MovieGenre.name.in_(cleaned))
        )
    )
    genres = list(result.scalars().all())
    matched = {genre.code.upper() for genre in genres} | {genre.name.casefold() for genre in genres}
    next_id = (await db.scalar(select(func.coalesce(func.max(MovieGenre.id), 0)))) + 1
    for value in cleaned:
        if value.upper() in matched or value.casefold() in matched:
            continue
        ascii_name = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
        code = re.sub(r"[^A-Z0-9]+", "_", ascii_name.upper()).strip("_") or f"GENRE_{next_id}"
        genre = MovieGenre(id=next_id, code=code[:40], name=value)
        db.add(genre)
        genres.append(genre)
        next_id += 1
    return genres


@router.post("/movies/import-tmdb", response_model=TmdbMovieImportResponse, status_code=status.HTTP_201_CREATED)
async def import_tmdb_movie(
    payload: TmdbMovieImportPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> TmdbMovieImportResponse:
    poster_url = f"https://image.tmdb.org/t/p/w500{payload.poster_path}" if payload.poster_path else None
    normalized_title = payload.title.strip().casefold()
    normalized_original_title = (payload.original_title or '').strip().casefold()
    duplicate_conditions = [
        Movie.tmdb_id == payload.tmdb_id,
        func.lower(Movie.title) == normalized_title,
    ]
    if normalized_original_title:
        duplicate_conditions.extend([
            func.lower(Movie.original_title) == normalized_original_title,
            func.lower(Movie.title) == normalized_original_title,
        ])
    result = await db.execute(
        select(Movie).options(selectinload(Movie.genres)).where(or_(*duplicate_conditions))
    )
    existing = result.scalars().first()
    if existing is not None:
        existing.tmdb_id = payload.tmdb_id
        existing.title = payload.title
        existing.original_title = payload.original_title or existing.original_title
        existing.description = payload.overview or existing.description
        existing.duration_min = payload.duration_min
        existing.release_date = payload.release_date or existing.release_date
        existing.language = payload.language or existing.language
        existing.trailer_url = payload.trailer_url or existing.trailer_url
        existing.poster_url = poster_url or existing.poster_url
        existing.director = payload.director or existing.director
        existing.cast_names = payload.cast_names or existing.cast_names
        # Re-import only synchronizes TMDB metadata. Never move a movie that is
        # already on sale back to UPCOMING because of an import operation.
        if payload.genres:
            existing.genres = await _resolve_genres(db, payload.genres)
        await db.commit()
        return TmdbMovieImportResponse(id=existing.id, title=existing.title, imported=False)

    movie = Movie(
        tmdb_id=payload.tmdb_id,
        title=payload.title,
        original_title=payload.original_title or payload.title,
        description=payload.overview,
        duration_min=payload.duration_min,
        release_date=payload.release_date,
        age_rating=None,
        language=payload.language,
        trailer_url=payload.trailer_url,
        poster_url=poster_url,
        director=payload.director,
        cast_names=payload.cast_names,
        status="UPCOMING",
    )
    movie.genres = await _resolve_genres(db, payload.genres)
    db.add(movie)
    await db.commit()
    await db.refresh(movie)

    return TmdbMovieImportResponse(id=movie.id, title=movie.title, imported=True)


@router.get("/stats", response_model=AdminStatsResponse)
async def read_admin_stats(
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> AdminStatsResponse:
    try:
        data = await get_live_admin_stats(db, branch_id=branch_id)
    except ValueError as exc:
        if str(exc) == "BRANCH_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found") from None
        raise
    return AdminStatsResponse(**data)


@router.get("/users", response_model=list[AdminUserRead])
async def read_admin_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> list[AdminUserRead]:
    rows = await list_users_with_branch_id(db)
    result: list[AdminUserRead] = []
    for user, branch_id in rows:
        user_read = AdminUserRead.model_validate(user)
        result.append(user_read.model_copy(update={"branch_id": branch_id}))
    return result


@router.post("/users", response_model=AdminUserRead, status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    payload: AdminUserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> AdminUserRead:
    target_role = (
        await db.execute(select(Role).where(Role.code == payload.role_code))
    ).scalar_one_or_none()
    if target_role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role {payload.role_code} is not configured",
        )
    if payload.role_code == "BRANCH_ADMIN" and payload.branch_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Branch is required for branch admin")
    if payload.branch_id is not None:
        branch_exists = (
            await db.execute(select(Branch.id).where(Branch.id == payload.branch_id, Branch.is_active.is_(True)))
        ).scalar_one_or_none()
        if branch_exists is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Branch is invalid or inactive")

    created: User | None = None
    try:
        created = await create_user(
            db,
            UserCreate(
                email=payload.email,
                phone=payload.phone,
                full_name=payload.full_name,
                date_of_birth=payload.date_of_birth,
                gender=payload.gender,
                password=payload.password,
            ),
            default_role_code="CUSTOMER",
        )

        created = await set_user_role(
            db,
            created,
            UserRoleUpdate(role_code=payload.role_code, branch_id=payload.branch_id),
        )
    except ValueError as exc:
        if created is not None:
            await db.delete(created)
            await db.commit()
        message = str(exc)
        if message in {"EMAIL_EXISTS", "PHONE_EXISTS"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from None
        if message == "BRANCH_REQUIRED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Branch is required for branch admin") from None
        if message == "ROLE_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected role is not configured") from None
        raise

    db.add(AuditEvent(
        entity_type="USER",
        entity_id=str(created.id),
        action="CREATE_ADMIN_ACCOUNT",
        new_data={"role": payload.role_code, "branch_id": str(payload.branch_id) if payload.branch_id else None},
        transaction_id=str(current_user.id),
    ))
    await db.commit()
    branch_map = await _branch_id_map(db)
    return AdminUserRead.model_validate(created).model_copy(update={"branch_id": branch_map.get(created.id)})


@router.patch("/users/{user_id}", response_model=AdminUserRead)
async def update_admin_user(
    user_id: UUID,
    payload: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> AdminUserRead:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_user.id and payload.is_active is not None and not payload.is_active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="CANNOT_LOCK_YOURSELF")
    if payload.is_active is False and any(role.code == "SUPER_ADMIN" for role in user.roles):
        active_super_admins = await db.scalar(
            select(func.count(User.id))
            .join(user_roles_table, user_roles_table.c.user_id == User.id)
            .join(Role, Role.id == user_roles_table.c.role_id)
            .where(Role.code == "SUPER_ADMIN", User.is_active.is_(True))
        )
        if (active_super_admins or 0) <= 1:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="LAST_ACTIVE_SUPER_ADMIN")

    if payload.is_active is True and any(role.code == "BRANCH_ADMIN" for role in user.roles):
        assignment = await db.scalar(text("""
            SELECT COUNT(*) FROM branch_staff bs
            JOIN branches b ON b.id = bs.branch_id
            WHERE bs.user_id = :user_id AND bs.is_active = TRUE AND b.is_active = TRUE
        """), {"user_id": str(user.id)})
        if assignment != 1:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="BRANCH_ADMIN_REQUIRES_ONE_ACTIVE_BRANCH")

    profile_payload = UserUpdate(
        full_name=payload.full_name,
        phone=payload.phone,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
    )

    try:
        updated = await update_user(db, user, profile_payload)
    except ValueError as exc:
        if str(exc) == "PHONE_EXISTS":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="PHONE_EXISTS") from None
        raise

    if payload.is_active is not None:
        old_active = updated.is_active
        updated.is_active = payload.is_active
        db.add(updated)
        db.add(AuditEvent(
            entity_type="USER",
            entity_id=str(updated.id),
            action="UNLOCK_ACCOUNT" if payload.is_active else "LOCK_ACCOUNT",
            old_data={"is_active": old_active},
            new_data={"is_active": payload.is_active},
            transaction_id=str(current_user.id),
        ))
        await db.commit()
        refreshed = await get_user_by_id(db, user_id)
        if refreshed is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        updated = refreshed

    branch_map = await _branch_id_map(db)
    return AdminUserRead.model_validate(updated).model_copy(update={"branch_id": branch_map.get(updated.id)})


@router.patch("/users/{user_id}/role", response_model=AdminUserRead)
async def update_admin_user_role(
    user_id: UUID,
    payload: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> AdminUserRead:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="CANNOT_CHANGE_YOUR_OWN_ROLE")
    if payload.role_code == "BRANCH_ADMIN":
        if payload.branch_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Branch is required for branch admin")
        valid_branch = await db.scalar(select(Branch.id).where(Branch.id == payload.branch_id, Branch.is_active.is_(True)))
        if valid_branch is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Branch is invalid or inactive")

    old_role = next((role.code for role in user.roles), "CUSTOMER")
    old_branch = (await _branch_id_map(db)).get(user.id)
    if old_role == "SUPER_ADMIN" and payload.role_code != "SUPER_ADMIN":
        active_super_admins = await db.scalar(
            select(func.count(User.id))
            .join(user_roles_table, user_roles_table.c.user_id == User.id)
            .join(Role, Role.id == user_roles_table.c.role_id)
            .where(Role.code == "SUPER_ADMIN", User.is_active.is_(True))
        )
        if (active_super_admins or 0) <= 1:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="LAST_ACTIVE_SUPER_ADMIN")

    updated_user = await set_user_role(db, user, payload)
    db.add(AuditEvent(
        entity_type="USER",
        entity_id=str(user.id),
        action="CHANGE_ROLE",
        old_data={"role": old_role, "branch_id": str(old_branch) if old_branch else None},
        new_data={"role": payload.role_code, "branch_id": str(payload.branch_id) if payload.branch_id else None},
        transaction_id=str(current_user.id),
    ))
    await db.commit()

    branch_rows = await list_users_with_branch_id(db)
    branch_id = next((item_branch for item_user, item_branch in branch_rows if item_user.id == updated_user.id), None)
    return AdminUserRead.model_validate(updated_user).model_copy(update={"branch_id": branch_id})


# ---------------------------------------------------------------------------
# Movies (simple stub CRUD kept from previous branch — no equivalent existed
# on the other branch, so nothing to merge here; still stubs, not wired to DB)
# ---------------------------------------------------------------------------

@router.post("/movies", response_model=MovieRead, status_code=status.HTTP_201_CREATED)
async def create_movie(
    payload: MovieDraftPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> MovieRead:
    if payload.status != "UPCOMING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "NEW_MOVIE_MUST_BE_UPCOMING"},
        )
    data = payload.model_dump(exclude={"genres"})
    movie = Movie(**data)
    movie.genres = await _resolve_genres(db, payload.genres)
    db.add(movie)
    await db.commit()
    refreshed = await db.execute(select(Movie).options(selectinload(Movie.genres)).where(Movie.id == movie.id))
    return MovieRead.model_validate(refreshed.scalar_one())


@router.put("/movies/{movie_id}", response_model=MovieRead)
async def update_movie(
    movie_id: UUID,
    payload: MovieDraftPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> MovieRead:
    row = await db.execute(select(Movie).options(selectinload(Movie.genres)).where(Movie.id == movie_id))
    movie = row.scalar_one_or_none()
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    for key, value in payload.model_dump(exclude={"genres"}).items():
        setattr(movie, key, value)
    movie.genres = await _resolve_genres(db, payload.genres)
    await db.commit()
    refreshed = await db.execute(select(Movie).options(selectinload(Movie.genres)).where(Movie.id == movie.id))
    return MovieRead.model_validate(refreshed.scalar_one())


@router.get("/movies/usage", response_model=dict[str, int])
async def movie_usage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> dict[str, int]:
    rows = await db.execute(
        select(Movie.id, func.count(Showtime.id))
        .outerjoin(Showtime, Showtime.movie_id == Movie.id)
        .group_by(Movie.id)
    )
    return {str(movie_id): int(showtime_count) for movie_id, showtime_count in rows.all()}


@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> None:
    row = await db.execute(select(Movie).where(Movie.id == movie_id))
    movie = row.scalar_one_or_none()
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    await db.delete(movie)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot delete a movie with showtimes") from None


# ---------------------------------------------------------------------------
# Branches (simple stub, path /branches — kept separate from the fully
# implemented /branches/manage below since paths don't collide)
# ---------------------------------------------------------------------------

@router.get("/branches", response_model=list[BranchRead])
async def list_branches_simple(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> list[BranchRead]:
    result = await db.execute(select(Branch).order_by(Branch.name))
    return [BranchRead.model_validate(item) for item in result.scalars().all()]


# ---------------------------------------------------------------------------
# Branch management (full implementation)
# ---------------------------------------------------------------------------

async def _branch_operational_counts(db: AsyncSession, branch_id: UUID) -> tuple[int, int, int]:
    staff_count = int((await db.execute(
        text("SELECT COUNT(*) FROM branch_staff WHERE branch_id = :branch_id AND is_active = TRUE"),
        {"branch_id": str(branch_id)},
    )).scalar() or 0)
    future_showtimes = int((await db.execute(
        select(func.count(Showtime.id))
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .where(
            Auditorium.branch_id == branch_id,
            Showtime.starts_at > datetime.now(timezone.utc),
            Showtime.status != "CANCELLED",
        )
    )).scalar() or 0)
    operational_data_count = int((await db.execute(
        select(func.count(Combo.id)).where(Combo.branch_id == branch_id)
    )).scalar() or 0)
    operational_data_count += int((await db.execute(
        select(func.count(PricingRule.id)).where(PricingRule.branch_id == branch_id)
    )).scalar() or 0)
    operational_data_count += int((await db.execute(
        text("SELECT COUNT(*) FROM promotions WHERE branch_ids @> CAST(:branch_ids AS jsonb)"),
        {"branch_ids": json.dumps([str(branch_id)])},
    )).scalar() or 0)
    return staff_count, future_showtimes, operational_data_count


async def _branch_manage_response(
    db: AsyncSession,
    branch: Branch,
    auditoriums_count: int,
) -> BranchManageRead:
    staff_count, future_showtimes, combo_count = await _branch_operational_counts(db, branch.id)
    return BranchManageRead(
        id=branch.id,
        vendor_id=branch.vendor_id,
        code=branch.code,
        name=branch.name,
        address_line=branch.address_line,
        city=branch.city,
        district=branch.district,
        phone=branch.phone,
        is_active=branch.is_active,
        auditoriums_count=auditoriums_count,
        active_staff_count=staff_count,
        future_showtimes_count=future_showtimes,
        is_ready=branch.is_active and auditoriums_count > 0,
        can_delete=auditoriums_count == 0 and staff_count == 0 and combo_count == 0,
    )

@router.get("/branches/manage", response_model=list[BranchManageRead])
async def read_admin_branches_manage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> list[BranchManageRead]:
    result = await db.execute(
        select(Branch, func.count(Auditorium.id))
        .outerjoin(Auditorium, Auditorium.branch_id == Branch.id)
        .group_by(Branch.id)
        .order_by(Branch.name.asc())
    )
    rows: list[BranchManageRead] = []
    for branch, count in result.all():
        rows.append(await _branch_manage_response(db, branch, int(count or 0)))
    return rows


@router.post("/branches/manage", response_model=BranchManageRead, status_code=status.HTTP_201_CREATED)
async def create_admin_branch(
    payload: BranchManageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> BranchManageRead:
    vendor_id = payload.vendor_id
    if vendor_id is None:
        vendor_row = await db.execute(select(Vendor).order_by(Vendor.created_at.asc()))
        vendor = vendor_row.scalars().first()
        if vendor is None:
            vendor = Vendor(
                id=uuid.uuid4(),
                code="DEFAULT_VENDOR",
                name="Default Vendor",
                description="Auto-created default vendor",
                is_active=True,
            )
            db.add(vendor)
            await db.commit()
            await db.refresh(vendor)
        vendor_id = vendor.id

    branch = Branch(
        vendor_id=vendor_id,
        code=payload.code,
        name=payload.name,
        address_line=payload.address_line,
        city=payload.city,
        district=payload.district,
        phone=payload.phone,
        is_active=payload.is_active,
    )
    db.add(branch)
    try:
        await db.flush()
        db.add(AuditEvent(
            entity_type="BRANCH",
            entity_id=str(branch.id),
            action="CREATE_BRANCH",
            old_data=None,
            new_data={"code": branch.code, "name": branch.name, "performed_by": str(current_user.id)},
        ))
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Branch code must be unique") from None

    await db.refresh(branch)
    return await _branch_manage_response(db, branch, 0)


@router.patch("/branches/manage/{branch_id}", response_model=BranchManageRead)
async def update_admin_branch(
    branch_id: UUID,
    payload: BranchManageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> BranchManageRead:
    row = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = row.scalar_one_or_none()
    if branch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
    await _ensure_branch_access(db, current_user, branch.id)

    changes = payload.model_dump(exclude_unset=True)
    if changes.get("is_active") is False and branch.is_active:
        _, future_showtimes, _ = await _branch_operational_counts(db, branch.id)
        if future_showtimes > 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="BRANCH_HAS_FUTURE_SHOWTIMES")

    old_data = {key: getattr(branch, key) for key in changes}
    for key, value in changes.items():
        setattr(branch, key, value)

    db.add(branch)
    try:
        await db.flush()
        db.add(AuditEvent(
            entity_type="BRANCH",
            entity_id=str(branch.id),
            action="UPDATE_BRANCH",
            old_data=old_data,
            new_data={**changes, "performed_by": str(current_user.id)},
        ))
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Branch update conflict") from None

    count_result = await db.execute(select(func.count(Auditorium.id)).where(Auditorium.branch_id == branch.id))
    return await _branch_manage_response(db, branch, int(count_result.scalar() or 0))


@router.delete("/branches/manage/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_branch(
    branch_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> None:
    row = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = row.scalar_one_or_none()
    if branch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")

    auditorium_count = int((await db.execute(
        select(func.count(Auditorium.id)).where(Auditorium.branch_id == branch.id)
    )).scalar() or 0)
    staff_count, future_showtimes, combo_count = await _branch_operational_counts(db, branch.id)
    if auditorium_count or staff_count or future_showtimes or combo_count:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="BRANCH_HAS_OPERATIONAL_DATA")

    await db.delete(branch)
    try:
        db.add(AuditEvent(
            entity_type="BRANCH",
            entity_id=str(branch.id),
            action="DELETE_BRANCH",
            old_data={"code": branch.code, "name": branch.name, "performed_by": str(current_user.id)},
            new_data=None,
        ))
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot delete branch that is referenced by other records") from None


@router.get("/auditoriums", response_model=list[AuditoriumRead])
async def read_admin_auditoriums(
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
) -> list[AuditoriumRead]:
    assigned_branch_id = await _staff_branch_id(db, current_user)
    if assigned_branch_id is not None:
        if branch_id is not None and branch_id != assigned_branch_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view another branch")
        branch_id = assigned_branch_id
    query = select(Auditorium).options(selectinload(Auditorium.branch)).order_by(Auditorium.name.asc())
    if branch_id:
        query = query.where(Auditorium.branch_id == branch_id)
    result = await db.execute(query)
    items = list(result.scalars().all())
    auditorium_ids = [item.id for item in items]
    active_seats: dict[UUID, int] = {}
    total_showtimes: dict[UUID, int] = {}
    future_showtimes: dict[UUID, int] = {}
    if auditorium_ids:
        seat_rows = await db.execute(
            select(Seat.auditorium_id, func.count(Seat.id))
            .where(Seat.auditorium_id.in_(auditorium_ids), Seat.is_active.is_(True))
            .group_by(Seat.auditorium_id)
        )
        active_seats = {room_id: int(count) for room_id, count in seat_rows.all()}
        showtime_rows = await db.execute(
            select(
                Showtime.auditorium_id,
                func.count(Showtime.id),
                func.count(Showtime.id).filter(
                    Showtime.ends_at > datetime.now(timezone.utc),
                    Showtime.status != "CANCELLED",
                ),
            )
            .where(Showtime.auditorium_id.in_(auditorium_ids))
            .group_by(Showtime.auditorium_id)
        )
        for room_id, total_count, future_count in showtime_rows.all():
            total_showtimes[room_id] = int(total_count)
            future_showtimes[room_id] = int(future_count)
    rows: list[AuditoriumRead] = []
    for item in items:
        seat_count = active_seats.get(item.id, 0)
        showtime_count = total_showtimes.get(item.id, 0)
        rows.append(
            AuditoriumRead(
                id=item.id,
                branch_id=item.branch_id,
                branch_name=item.branch.name if item.branch else "",
                code=item.code,
                name=item.name,
                total_seats=item.total_seats,
                screen_type=item.screen_type,
                is_active=item.is_active,
                active_seats_count=seat_count,
                total_showtimes_count=showtime_count,
                future_showtimes_count=future_showtimes.get(item.id, 0),
                is_ready=bool(item.is_active and seat_count > 0),
                can_delete=showtime_count == 0,
            )
        )
    return rows


@router.post("/auditoriums", response_model=AuditoriumRead, status_code=status.HTTP_201_CREATED)
async def create_admin_auditorium(
    payload: AuditoriumCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> AuditoriumRead:
    row = await db.execute(select(Branch).where(Branch.id == payload.branch_id))
    branch = row.scalar_one_or_none()
    if branch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
    await _ensure_branch_access(db, current_user, branch.id)

    await _ensure_default_seat_types(db)
    standard = (await db.execute(select(SeatType).where(SeatType.code == "STANDARD"))).scalar_one()
    data = payload.model_dump(exclude={"rows", "seats_per_row"})
    row_count = payload.rows
    column_count = payload.seats_per_row
    if (row_count is None) != (column_count is None):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="AUDITORIUM_LAYOUT_DIMENSIONS_REQUIRED")
    if row_count and column_count:
        data["total_seats"] = row_count * column_count
    item = Auditorium(**data)
    db.add(item)
    try:
        await db.flush()
        if row_count and column_count:
            db.add_all([
                Seat(
                    auditorium_id=item.id,
                    seat_row=chr(65 + row_index),
                    seat_number=seat_number,
                    seat_type_id=standard.id,
                    is_active=True,
                )
                for row_index in range(row_count)
                for seat_number in range(1, column_count + 1)
            ])
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Auditorium create conflict") from None

    await db.refresh(item)
    return AuditoriumRead(
        id=item.id,
        branch_id=item.branch_id,
        branch_name=branch.name,
        code=item.code,
        name=item.name,
        total_seats=item.total_seats,
        screen_type=item.screen_type,
        is_active=item.is_active,
        active_seats_count=item.total_seats if row_count and column_count else 0,
        total_showtimes_count=0,
        future_showtimes_count=0,
        is_ready=bool(item.is_active and row_count and column_count),
        can_delete=True,
    )


@router.patch("/auditoriums/{auditorium_id}", response_model=AuditoriumRead)
async def update_admin_auditorium(
    auditorium_id: UUID,
    payload: AuditoriumUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> AuditoriumRead:
    row = await db.execute(select(Auditorium).options(selectinload(Auditorium.branch)).where(Auditorium.id == auditorium_id))
    item = row.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auditorium not found")
    await _ensure_branch_access(db, current_user, item.branch_id)

    updates = payload.model_dump(exclude_unset=True)
    future_count = int((await db.execute(
        select(func.count(Showtime.id)).where(
            Showtime.auditorium_id == item.id,
            Showtime.ends_at > datetime.now(timezone.utc),
            Showtime.status != "CANCELLED",
        )
    )).scalar_one())
    if updates.get("is_active") is False and future_count:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="AUDITORIUM_HAS_FUTURE_SHOWTIMES")
    if updates.get("is_active") is True:
        active_count = int((await db.execute(
            select(func.count(Seat.id)).where(Seat.auditorium_id == item.id, Seat.is_active.is_(True))
        )).scalar_one())
        if active_count == 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="AUDITORIUM_NEEDS_ACTIVE_SEATS")

    for key, value in updates.items():
        setattr(item, key, value)

    db.add(item)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Auditorium update conflict") from None

    active_count = int((await db.execute(
        select(func.count(Seat.id)).where(Seat.auditorium_id == item.id, Seat.is_active.is_(True))
    )).scalar_one())
    total_count = int((await db.execute(
        select(func.count(Showtime.id)).where(Showtime.auditorium_id == item.id)
    )).scalar_one())
    return AuditoriumRead(
        id=item.id,
        branch_id=item.branch_id,
        branch_name=item.branch.name if item.branch else "",
        code=item.code,
        name=item.name,
        total_seats=item.total_seats,
        screen_type=item.screen_type,
        is_active=item.is_active,
        active_seats_count=active_count,
        total_showtimes_count=total_count,
        future_showtimes_count=future_count,
        is_ready=bool(item.is_active and active_count > 0),
        can_delete=total_count == 0,
    )


@router.delete("/auditoriums/{auditorium_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_auditorium(
    auditorium_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> None:
    row = await db.execute(select(Auditorium).where(Auditorium.id == auditorium_id))
    item = row.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auditorium not found")
    await _ensure_branch_access(db, current_user, item.branch_id)

    showtime_count = int((await db.execute(
        select(func.count(Showtime.id)).where(Showtime.auditorium_id == item.id)
    )).scalar_one())
    if showtime_count:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="AUDITORIUM_HAS_OPERATIONAL_DATA")

    await db.delete(item)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot delete auditorium that is referenced") from None


@router.get("/seat-types", response_model=list[SeatTypeRead])
async def read_admin_seat_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
) -> list[SeatTypeRead]:
    await _ensure_default_seat_types(db)
    result = await db.execute(select(SeatType).order_by(SeatType.id.asc()))
    return [SeatTypeRead(id=item.id, code=item.code, name=item.name) for item in result.scalars().all()]


@router.get("/seats", response_model=list[SeatAdminRead])
async def read_admin_seats(
    auditorium_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
) -> list[SeatAdminRead]:
    assigned_branch_id = await _staff_branch_id(db, current_user)
    query = (
        select(Seat)
        .options(selectinload(Seat.auditorium).selectinload(Auditorium.branch), selectinload(Seat.seat_type))
        .order_by(Seat.seat_row.asc(), Seat.seat_number.asc())
    )
    if auditorium_id:
        query = query.where(Seat.auditorium_id == auditorium_id)
    if assigned_branch_id is not None:
        query = query.join(Auditorium, Seat.auditorium_id == Auditorium.id).where(
            Auditorium.branch_id == assigned_branch_id
        )

    result = await db.execute(query)
    data: list[SeatAdminRead] = []
    for item in result.scalars().all():
        data.append(
            SeatAdminRead(
                id=item.id,
                auditorium_id=item.auditorium_id,
                auditorium_name=item.auditorium.name if item.auditorium else "",
                branch_name=item.auditorium.branch.name if item.auditorium and item.auditorium.branch else "",
                seat_row=item.seat_row,
                seat_number=item.seat_number,
                seat_type_id=item.seat_type_id,
                seat_type_code=item.seat_type.code if item.seat_type else "",
                is_active=item.is_active,
            )
        )
    return data


@router.post("/seats", response_model=SeatAdminRead, status_code=status.HTTP_201_CREATED)
async def create_admin_seat(
    payload: SeatAdminCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> SeatAdminRead:
    await _ensure_default_seat_types(db)
    auditorium_row = await db.execute(select(Auditorium).options(selectinload(Auditorium.branch)).where(Auditorium.id == payload.auditorium_id))
    auditorium = auditorium_row.scalar_one_or_none()
    if auditorium is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auditorium not found")
    await _ensure_branch_access(db, current_user, auditorium.branch_id)
    type_row = await db.execute(select(SeatType).where(SeatType.id == payload.seat_type_id))
    seat_type = type_row.scalar_one_or_none()
    if seat_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat type not found")

    seat = Seat(**payload.model_dump())
    db.add(seat)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Seat position already exists") from None

    await db.refresh(seat)
    return SeatAdminRead(
        id=seat.id,
        auditorium_id=seat.auditorium_id,
        auditorium_name=auditorium.name,
        branch_name=auditorium.branch.name if auditorium.branch else "",
        seat_row=seat.seat_row,
        seat_number=seat.seat_number,
        seat_type_id=seat.seat_type_id,
        seat_type_code=seat_type.code,
        is_active=seat.is_active,
    )


@router.put("/auditoriums/{auditorium_id}/seat-layout", response_model=SeatLayoutRead)
async def replace_admin_seat_layout(
    auditorium_id: UUID,
    payload: SeatLayoutUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> SeatLayoutRead:
    """Create/update an entire room layout atomically."""
    await _ensure_default_seat_types(db)
    room_row = await db.execute(
        select(Auditorium)
        .options(selectinload(Auditorium.branch), selectinload(Auditorium.seats))
        .where(Auditorium.id == auditorium_id)
    )
    room = room_row.scalar_one_or_none()
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auditorium not found")
    await _ensure_branch_access(db, current_user, room.branch_id)

    positions = [(cell.seat_row.strip().upper(), cell.seat_number) for cell in payload.seats]
    if len(positions) != len(set(positions)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seat positions must be unique")
    if not any(cell.is_active for cell in payload.seats):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="AUDITORIUM_NEEDS_ACTIVE_SEATS")

    type_ids = {cell.seat_type_id for cell in payload.seats}
    valid_types = set(
        (
            await db.execute(select(SeatType.id).where(SeatType.id.in_(type_ids)))
        ).scalars().all()
    )
    if valid_types != type_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more seat types were not found")

    existing = {(seat.seat_row.upper(), seat.seat_number): seat for seat in room.seats}
    referenced_ids = set(
        (
            await db.execute(
                select(BookingSeat.seat_id)
                .join(Seat, Seat.id == BookingSeat.seat_id)
                .join(Booking, Booking.id == BookingSeat.booking_id)
                .join(Showtime, Showtime.id == Booking.showtime_id)
                .where(
                    Seat.auditorium_id == auditorium_id,
                    Booking.status == "CONFIRMED",
                    Showtime.ends_at > func.now(),
                    Showtime.status != "CANCELLED",
                )
            )
        ).scalars().all()
    )

    submitted = set(positions)
    for cell in payload.seats:
        position = (cell.seat_row.strip().upper(), cell.seat_number)
        seat = existing.get(position)
        if seat is None:
            seat = Seat(
                auditorium_id=auditorium_id,
                seat_row=position[0],
                seat_number=position[1],
                seat_type_id=cell.seat_type_id,
                is_active=cell.is_active,
            )
            db.add(seat)
            continue
        changed = seat.seat_type_id != cell.seat_type_id or seat.is_active != cell.is_active
        if changed and seat.id in referenced_ids:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Seat {seat.seat_row}{seat.seat_number} has a ticket for an upcoming showtime and cannot be changed",
            )
        seat.seat_type_id = cell.seat_type_id
        seat.is_active = cell.is_active

    # Positions removed from the editor become inactive, preserving ticket history.
    for position, seat in existing.items():
        if position not in submitted:
            if seat.id in referenced_ids:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Seat {seat.seat_row}{seat.seat_number} has a ticket for an upcoming showtime and cannot be removed",
                )
            seat.is_active = False

    room.total_seats = sum(1 for cell in payload.seats if cell.is_active)
    db.add(room)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Seat layout update conflict") from None

    result = await db.execute(
        select(Seat)
        .options(selectinload(Seat.auditorium).selectinload(Auditorium.branch), selectinload(Seat.seat_type))
        .where(Seat.auditorium_id == auditorium_id)
        .order_by(Seat.seat_row.asc(), Seat.seat_number.asc())
    )
    output = [
        SeatAdminRead(
            id=seat.id,
            auditorium_id=seat.auditorium_id,
            auditorium_name=room.name,
            branch_name=room.branch.name if room.branch else "",
            seat_row=seat.seat_row,
            seat_number=seat.seat_number,
            seat_type_id=seat.seat_type_id,
            seat_type_code=seat.seat_type.code if seat.seat_type else "",
            is_active=seat.is_active,
        )
        for seat in result.scalars().all()
    ]
    return SeatLayoutRead(auditorium_id=room.id, active_seats=room.total_seats, seats=output)


@router.patch("/seats/{seat_id}", response_model=SeatAdminRead)
async def update_admin_seat(
    seat_id: UUID,
    payload: SeatAdminUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> SeatAdminRead:
    await _ensure_default_seat_types(db)
    row = await db.execute(
        select(Seat)
        .options(selectinload(Seat.auditorium).selectinload(Auditorium.branch), selectinload(Seat.seat_type))
        .where(Seat.id == seat_id)
    )
    seat = row.scalar_one_or_none()
    if seat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found")
    await _ensure_branch_access(db, current_user, seat.auditorium.branch_id)

    updates = payload.model_dump(exclude_unset=True)
    if "seat_type_id" in updates and updates["seat_type_id"] is not None:
        type_row = await db.execute(select(SeatType).where(SeatType.id == updates["seat_type_id"]))
        if type_row.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat type not found")

    for key, value in updates.items():
        setattr(seat, key, value)

    db.add(seat)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Seat update conflict") from None

    await db.refresh(seat)
    return SeatAdminRead(
        id=seat.id,
        auditorium_id=seat.auditorium_id,
        auditorium_name=seat.auditorium.name if seat.auditorium else "",
        branch_name=seat.auditorium.branch.name if seat.auditorium and seat.auditorium.branch else "",
        seat_row=seat.seat_row,
        seat_number=seat.seat_number,
        seat_type_id=seat.seat_type_id,
        seat_type_code=seat.seat_type.code if seat.seat_type else "",
        is_active=seat.is_active,
    )


@router.delete("/seats/{seat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_seat(
    seat_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> None:
    row = await db.execute(
        select(Seat)
        .options(selectinload(Seat.auditorium))
        .where(Seat.id == seat_id)
    )
    seat = row.scalar_one_or_none()
    if seat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found")
    await _ensure_branch_access(db, current_user, seat.auditorium.branch_id)

    await db.delete(seat)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot delete seat that is referenced") from None


@router.get("/showtimes", response_model=list[ShowtimeAdminRead])
async def read_admin_showtimes(
    branch_id: UUID | None = None,
    starts_from: datetime | None = None,
    starts_to: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
) -> list[ShowtimeAdminRead]:
    assigned_branch_id = await _staff_branch_id(db, current_user)
    if assigned_branch_id is not None:
        if branch_id is not None and branch_id != assigned_branch_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view another branch")
        branch_id = assigned_branch_id
    query = (
        select(Showtime)
        .options(selectinload(Showtime.movie), selectinload(Showtime.auditorium).selectinload(Auditorium.branch))
        .order_by(Showtime.starts_at.desc())
    )
    if branch_id:
        query = query.join(Auditorium, Showtime.auditorium_id == Auditorium.id).where(Auditorium.branch_id == branch_id)
    if starts_from:
        query = query.where(Showtime.starts_at >= starts_from)
    if starts_to:
        query = query.where(Showtime.starts_at < starts_to)

    result = await db.execute(query)
    items = list(result.scalars().all())
    ids = [item.id for item in items]
    stats_by_id: dict[UUID, tuple[int, int, float]] = {}
    if ids:
        stats_rows = await db.execute(
            text(
                """
                SELECT b.showtime_id,
                       COUNT(b.id) AS bookings,
                       COALESCE(SUM((
                           SELECT COUNT(*) FROM booking_seats bs WHERE bs.booking_id = b.id
                       )), 0) AS seats,
                       COALESCE(SUM((
                           SELECT SUM(p.amount) FROM payments p
                           WHERE p.booking_id = b.id AND p.status = 'SUCCESS'
                       )), 0) AS revenue
                FROM bookings b
                WHERE b.showtime_id = ANY(:showtime_ids)
                  AND b.status = 'CONFIRMED'
                GROUP BY b.showtime_id
                """
            ),
            {"showtime_ids": ids},
        )
        stats_by_id = {
            row[0]: (int(row[1] or 0), int(row[2] or 0), float(row[3] or 0))
            for row in stats_rows.all()
        }
    rows: list[ShowtimeAdminRead] = []
    for item in items:
        booking_count, sold_seats, revenue = stats_by_id.get(item.id, (0, 0, 0))
        rows.append(_showtime_admin_read(item, booking_count=booking_count, sold_seats=sold_seats, revenue=revenue))
    return rows


@router.post("/showtimes", response_model=ShowtimeAdminRead, status_code=status.HTTP_201_CREATED)
async def create_admin_showtime(
    payload: ShowtimeAdminCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> ShowtimeAdminRead:
    if payload.starts_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="starts_at must be in the future")
    if payload.ends_at <= payload.starts_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ends_at must be after starts_at")
    booking_closes_at = payload.booking_closes_at or payload.starts_at - timedelta(minutes=15)
    if booking_closes_at > payload.starts_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="booking_closes_at cannot be after starts_at")
    if payload.status == "OPEN" and booking_closes_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot open sales because the sales closing time has already passed",
        )

    movie_row = await db.execute(select(Movie).where(Movie.id == payload.movie_id))
    movie = movie_row.scalar_one_or_none()
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    if payload.status == "NOW_SHOWING" and movie.status != "NOW_SHOWING":
        open_showtimes = await db.scalar(
            select(func.count(Showtime.id)).where(
                Showtime.movie_id == movie.id,
                Showtime.status == "OPEN",
                Showtime.starts_at > datetime.now(timezone.utc),
            )
        )
        if not open_showtimes:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "MOVIE_NEEDS_OPEN_SHOWTIME"},
            )
    if payload.status == "ENDED" and movie.status != "ENDED":
        future_showtimes = await db.scalar(
            select(func.count(Showtime.id)).where(
                Showtime.movie_id == movie.id,
                Showtime.status == "OPEN",
                Showtime.starts_at > datetime.now(timezone.utc),
            )
        )
        if future_showtimes:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "MOVIE_HAS_FUTURE_SHOWTIMES", "count": int(future_showtimes)},
            )
    if payload.ends_at < payload.starts_at + timedelta(minutes=movie.duration_min):
        raise HTTPException(status_code=400, detail="Showtime cannot end before the movie duration")
    maximum_end = payload.starts_at + timedelta(minutes=movie.duration_min + 60)
    if payload.ends_at > maximum_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Showtime duration is too long for this movie",
        )

    auditorium_row = await db.execute(select(Auditorium).options(selectinload(Auditorium.branch)).where(Auditorium.id == payload.auditorium_id))
    auditorium = auditorium_row.scalar_one_or_none()
    if auditorium is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auditorium not found")
    await _ensure_branch_access(db, current_user, auditorium.branch_id)

    active_seat_count = int((await db.execute(
        select(func.count(Seat.id)).where(
            Seat.auditorium_id == auditorium.id,
            Seat.is_active.is_(True),
        )
    )).scalar_one())
    if not auditorium.is_active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="AUDITORIUM_IS_INACTIVE")
    if active_seat_count == 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="AUDITORIUM_NEEDS_ACTIVE_SEATS")

    conflict = await db.scalar(
        select(func.count(Showtime.id)).where(
            Showtime.auditorium_id == payload.auditorium_id,
            Showtime.status != "CANCELLED",
            Showtime.starts_at < payload.ends_at,
            Showtime.ends_at + timedelta(minutes=settings.showtime_turnaround_minutes) > payload.starts_at,
        )
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The auditorium already has a showtime in this time range",
        )

    showtime = Showtime(
        movie_id=payload.movie_id,
        auditorium_id=payload.auditorium_id,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        booking_closes_at=booking_closes_at,
        status=payload.status,
        base_price=payload.base_price,
        created_by=current_user.id,
    )
    db.add(showtime)
    if payload.status == "OPEN" and movie.status == "UPCOMING":
        movie.status = "NOW_SHOWING"
    await db.commit()
    await db.refresh(showtime)

    showtime.movie = movie
    showtime.auditorium = auditorium
    return _showtime_admin_read(showtime)


@router.post("/showtimes/bulk", response_model=list[ShowtimeAdminRead], status_code=status.HTTP_201_CREATED)
async def create_admin_showtimes_bulk(
    payload: ShowtimeBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> list[ShowtimeAdminRead]:
    movie_ids = {item.movie_id for item in payload.showtimes}
    auditorium_ids = {item.auditorium_id for item in payload.showtimes}
    movies_result = await db.execute(select(Movie).where(Movie.id.in_(movie_ids)))
    auditoriums_result = await db.execute(
        select(Auditorium)
        .options(selectinload(Auditorium.branch))
        .where(Auditorium.id.in_(auditorium_ids))
    )
    movies_by_id = {item.id: item for item in movies_result.scalars().all()}
    auditoriums_by_id = {item.id: item for item in auditoriums_result.scalars().all()}
    if len(movies_by_id) != len(movie_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more movies were not found")
    if len(auditoriums_by_id) != len(auditorium_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more auditoriums were not found")
    for auditorium in auditoriums_by_id.values():
        await _ensure_branch_access(db, current_user, auditorium.branch_id)
        if not auditorium.is_active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="AUDITORIUM_IS_INACTIVE")
    active_seat_rows = await db.execute(
        select(Seat.auditorium_id, func.count(Seat.id))
        .where(Seat.auditorium_id.in_(auditorium_ids), Seat.is_active.is_(True))
        .group_by(Seat.auditorium_id)
    )
    active_seat_counts = {room_id: int(count) for room_id, count in active_seat_rows.all()}
    if any(active_seat_counts.get(room_id, 0) == 0 for room_id in auditorium_ids):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="AUDITORIUM_NEEDS_ACTIVE_SEATS")

    ordered = sorted(payload.showtimes, key=lambda item: (str(item.auditorium_id), item.starts_at))
    for index, item in enumerate(ordered):
        if item.starts_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="All showtimes must start in the future")
        if item.ends_at <= item.starts_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Every end time must be after its start time")
        if item.ends_at < item.starts_at + timedelta(minutes=movies_by_id[item.movie_id].duration_min):
            raise HTTPException(status_code=400, detail="A showtime cannot end before the movie duration")
        booking_closes_at = item.booking_closes_at or item.starts_at - timedelta(minutes=15)
        if item.status == "OPEN" and booking_closes_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot create an open showtime after its sales closing time",
            )
        for other in ordered[index + 1:]:
            if other.auditorium_id != item.auditorium_id:
                continue
            if other.starts_at < item.ends_at + timedelta(minutes=settings.showtime_turnaround_minutes) and other.ends_at + timedelta(minutes=settings.showtime_turnaround_minutes) > item.starts_at:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Generated schedule contains overlapping showtimes")

    min_start = min(item.starts_at for item in ordered)
    max_end = max(item.ends_at for item in ordered)
    existing_result = await db.execute(
        select(Showtime).where(
            Showtime.auditorium_id.in_(auditorium_ids),
            Showtime.status != "CANCELLED",
            Showtime.starts_at < max_end,
            Showtime.ends_at + timedelta(minutes=settings.showtime_turnaround_minutes) > min_start,
        )
    )
    existing = list(existing_result.scalars().all())
    for item in ordered:
        if any(
            row.auditorium_id == item.auditorium_id
            and row.starts_at < item.ends_at
            and row.ends_at + timedelta(minutes=settings.showtime_turnaround_minutes) > item.starts_at
            for row in existing
        ):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A generated showtime overlaps the current schedule")

    created = [
        Showtime(
            movie_id=item.movie_id,
            auditorium_id=item.auditorium_id,
            starts_at=item.starts_at,
            ends_at=item.ends_at,
            booking_closes_at=item.booking_closes_at or item.starts_at - timedelta(minutes=15),
            status=item.status,
            base_price=item.base_price,
            created_by=current_user.id,
        )
        for item in ordered
    ]
    db.add_all(created)
    for movie_id in {item.movie_id for item in ordered if item.status == "OPEN"}:
        movie = movies_by_id[movie_id]
        if movie.status == "UPCOMING":
            movie.status = "NOW_SHOWING"
    await db.commit()
    for item in created:
        await db.refresh(item)

    for item in created:
        item.movie = movies_by_id[item.movie_id]
        item.auditorium = auditoriums_by_id[item.auditorium_id]
    return [_showtime_admin_read(item) for item in created]


@router.post("/showtimes/publish", response_model=list[ShowtimeAdminRead])
async def publish_admin_showtimes(
    payload: ShowtimeBulkPublish,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> list[ShowtimeAdminRead]:
    result = await db.execute(
        select(Showtime)
        .options(selectinload(Showtime.movie), selectinload(Showtime.auditorium).selectinload(Auditorium.branch))
        .where(Showtime.id.in_(payload.showtime_ids))
    )
    items = list(result.scalars().all())
    if len(items) != len(set(payload.showtime_ids)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more draft showtimes were not found")
    for item in items:
        await _ensure_branch_access(db, current_user, item.auditorium.branch_id)
        if item.status != "DRAFT":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only draft showtimes can be published")
        if item.booking_closes_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot publish a showtime after sales closing time")
        item.status = "OPEN"
        if item.movie.status == "UPCOMING":
            item.movie.status = "NOW_SHOWING"
    await db.commit()
    return [_showtime_admin_read(item) for item in items]


@router.patch("/showtimes/{showtime_id}", response_model=ShowtimeAdminRead)
async def update_admin_showtime(
    showtime_id: UUID,
    payload: ShowtimeAdminUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> ShowtimeAdminRead:
    row = await db.execute(
        select(Showtime)
        .options(selectinload(Showtime.movie), selectinload(Showtime.auditorium).selectinload(Auditorium.branch))
        .where(Showtime.id == showtime_id)
    )
    showtime = row.scalar_one_or_none()
    if showtime is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Showtime not found")
    await _ensure_branch_access(db, current_user, showtime.auditorium.branch_id)

    updates = payload.model_dump(exclude_unset=True)
    confirmed_bookings = int(
        await db.scalar(
            select(func.count(Booking.id)).where(
                Booking.showtime_id == showtime.id,
                Booking.status == "CONFIRMED",
            )
        ) or 0
    )
    sensitive_fields = {"auditorium_id", "starts_at", "ends_at", "booking_closes_at"}
    if confirmed_bookings and sensitive_fields.intersection(updates):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot change room or time because {confirmed_bookings} confirmed booking(s) are affected. Cancel the showtime instead.",
        )
    if confirmed_bookings and updates.get("status") == "DRAFT":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A showtime with confirmed bookings cannot be moved back to draft",
        )
    if updates.get("status") == "CANCELLED" and not str(updates.get("cancellation_reason") or "").strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A cancellation reason is required")
    new_starts_at = updates.get("starts_at", showtime.starts_at)
    new_ends_at = updates.get("ends_at", showtime.ends_at)
    if "starts_at" in updates and new_starts_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="starts_at must be in the future")
    if new_ends_at <= new_starts_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ends_at must be after starts_at")
    if new_ends_at > new_starts_at + timedelta(minutes=showtime.movie.duration_min + 60):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Showtime duration is too long for this movie",
        )
    if new_ends_at < new_starts_at + timedelta(minutes=showtime.movie.duration_min):
        raise HTTPException(status_code=400, detail="Showtime cannot end before the movie duration")
    new_booking_closes_at = updates.get("booking_closes_at", showtime.booking_closes_at)
    if new_booking_closes_at > new_starts_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="booking_closes_at cannot be after starts_at")

    if "auditorium_id" in updates and updates["auditorium_id"] is not None:
        auditorium_row = await db.execute(select(Auditorium).where(Auditorium.id == updates["auditorium_id"]))
        target_auditorium = auditorium_row.scalar_one_or_none()
        if target_auditorium is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auditorium not found")
        await _ensure_branch_access(db, current_user, target_auditorium.branch_id)

    target_auditorium_id = updates.get("auditorium_id", showtime.auditorium_id)
    conflict = await db.scalar(
        select(func.count(Showtime.id)).where(
            Showtime.id != showtime.id,
            Showtime.auditorium_id == target_auditorium_id,
            Showtime.status != "CANCELLED",
            Showtime.starts_at < new_ends_at,
            Showtime.ends_at + timedelta(minutes=settings.showtime_turnaround_minutes) > new_starts_at,
        )
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The auditorium already has a showtime in this time range",
        )

    for key, value in updates.items():
        setattr(showtime, key, value)

    payments_to_refund: list[tuple[Payment, Booking]] = []
    if updates.get("status") == "CANCELLED":
        bookings_result = await db.execute(
            select(Booking).where(
                Booking.showtime_id == showtime.id,
                Booking.status.in_(["CONFIRMED", "CANCEL_REQUESTED"]),
            )
        )
        affected_bookings = list(bookings_result.scalars().all())
        for booking in affected_bookings:
            seat_rows = await db.execute(
                select(BookingSeat)
                .options(selectinload(BookingSeat.seat))
                .where(BookingSeat.booking_id == booking.id)
            )
            if not booking.seat_snapshot:
                booking.seat_snapshot = [
                    {"id": str(item.seat_id), "row": item.seat.seat_row, "number": item.seat.seat_number}
                    for item in seat_rows.scalars().all()
                ]
            booking.status = "CANCELLED"
            booking.cancellation_reason = str(updates.get("cancellation_reason") or "").strip()
            booking.cancelled_at = datetime.now(timezone.utc)
            booking.cancelled_by = current_user.id
        if affected_bookings:
            await release_booking_combo_inventory(
                db, [booking.id for booking in affected_bookings], include_sold=True
            )
            await db.execute(
                update(Ticket)
                .where(Ticket.booking_id.in_([booking.id for booking in affected_bookings]))
                .values(status="CANCELLED")
            )
            await db.execute(
                delete(BookingSeat).where(
                    BookingSeat.booking_id.in_([booking.id for booking in affected_bookings])
                )
            )
        payment_result = await db.execute(
            select(Payment)
            .join(Booking, Booking.id == Payment.booking_id)
            .where(
                Booking.showtime_id == showtime.id,
                Payment.status == "SUCCESS",
            )
        )
        for payment in payment_result.scalars().all():
            payment.status = "REFUND_PENDING"
            related_booking = next((item for item in affected_bookings if item.id == payment.booking_id), None)
            if related_booking is not None:
                payments_to_refund.append((payment, related_booking))
            db.add(PaymentStatusHistory(
                payment_id=payment.id,
                old_status="SUCCESS",
                new_status="REFUND_PENDING",
                source="BRANCH_ADMIN",
                note=f"Showtime cancelled: {showtime.cancellation_reason or ''}",
                raw_payload={},
            ))

    db.add(showtime)
    await db.commit()
    await seat_events.broadcast(showtime.id, "SEATS_UPDATED")
    for payment, booking in payments_to_refund:
        await _execute_vnpay_refund(
            payment=payment,
            booking=booking,
            current_user=current_user,
            request=request,
            db=db,
            reason=f"Showtime cancelled: {showtime.cancellation_reason or ''}",
        )

    refreshed_row = await db.execute(
        select(Showtime)
        .options(selectinload(Showtime.movie), selectinload(Showtime.auditorium).selectinload(Auditorium.branch))
        .where(Showtime.id == showtime_id)
    )
    refreshed = refreshed_row.scalar_one_or_none()
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Showtime not found")

    return _showtime_admin_read(refreshed, booking_count=confirmed_bookings)


@router.delete("/showtimes/{showtime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_showtime(
    showtime_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> None:
    row = await db.execute(
        select(Showtime)
        .options(selectinload(Showtime.auditorium))
        .where(Showtime.id == showtime_id)
    )
    showtime = row.scalar_one_or_none()
    if showtime is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Showtime not found")
    await _ensure_branch_access(db, current_user, showtime.auditorium.branch_id)

    booking_count = int(
        await db.scalar(select(func.count(Booking.id)).where(Booking.showtime_id == showtime.id)) or 0
    )
    if booking_count:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a showtime with bookings. Cancel it with a reason instead.",
        )

    await db.delete(showtime)
    await db.commit()


# ---------------------------------------------------------------------------
# Bookings / payments / reports
# ---------------------------------------------------------------------------


@router.get("/pricing-rules", dependencies=[Depends(require_branch_admin)])
async def list_pricing_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    branch_id = await _staff_branch_id(db, current_user)
    query = select(PricingRule).order_by(PricingRule.priority.desc(), PricingRule.name)
    if branch_id is not None:
        query = query.where(or_(PricingRule.branch_id == branch_id, PricingRule.branch_id.is_(None)))
    return list((await db.execute(query)).scalars().all())


@router.get("/audit-events", dependencies=[Depends(require_admin)])
async def list_audit_events(
    entity_type: str | None = None,
    entity_id: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditEvent)
    if entity_type:
        query = query.where(AuditEvent.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditEvent.entity_id == entity_id)
    rows = await db.execute(query.order_by(AuditEvent.created_at.desc()).limit(limit))
    return list(rows.scalars().all())


@router.post("/pricing-rules", dependencies=[Depends(require_branch_admin)])
async def create_pricing_rule(
    payload: PricingRuleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.branch_id is not None:
        await _ensure_branch_access(db, current_user, payload.branch_id)
    elif not _is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Branch pricing rule requires a branch")
    rule = PricingRule(**payload.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.patch("/pricing-rules/{rule_id}", dependencies=[Depends(require_branch_admin)])
async def update_pricing_rule(
    rule_id: UUID,
    payload: PricingRuleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = await db.get(PricingRule, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    if rule.branch_id is not None:
        await _ensure_branch_access(db, current_user, rule.branch_id)
    for key, value in payload.model_dump().items():
        setattr(rule, key, value)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.post("/pos/bookings", dependencies=[Depends(require_roles("BRANCH_ADMIN"))])
async def create_pos_booking(
    payload: PosBookingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    showtime = await db.get(Showtime, payload.showtime_id)
    if showtime is None:
        raise HTTPException(status_code=404, detail="Showtime not found")
    auditorium = await db.get(Auditorium, showtime.auditorium_id)
    await _ensure_branch_access(db, current_user, auditorium.branch_id)
    try:
        booking = await create_user_booking(
            db,
            current_user.id,
            payload.showtime_id,
            payload.seat_ids,
            require_hold=False,
            sales_channel="POS",
            customer={
                "name": payload.customer_name,
                "email": payload.customer_email,
                "phone": payload.customer_phone,
            },
            commit=False,
        )
        payment = Payment(
            booking_id=booking.id,
            user_id=current_user.id,
            amount=booking.total_price,
            payment_method=payload.payment_method,
            status="SUCCESS",
            paid_at=datetime.now(timezone.utc),
        )
        db.add(payment)
        booking.status = "CONFIRMED"
        await confirm_booking_combo_inventory(db, booking.id)
        await issue_booking_ticket(db, booking)
        await db.commit()
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from None
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="One or more seats were just sold") from None
    return {
        "booking_id": booking.id,
        "ticket_code": booking.ticket_code,
        "status": booking.status,
        "amount": booking.total_price,
        "payment_method": payload.payment_method,
    }


def _parse_date_boundary(value: str | None, *, end: bool = False) -> datetime | None:
    if not value:
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Date must use YYYY-MM-DD format",
        ) from exc
    boundary = time.max if end else time.min
    return datetime.combine(parsed, boundary, tzinfo=timezone.utc)


def _booking_admin_dict(booking: Booking, customer: User | None = None) -> dict:
    showtime = booking.showtime
    auditorium = showtime.auditorium
    tickets = list(booking.tickets)
    checked_in_count = sum(1 for item in tickets if item.status == "USED")
    checkin_status = "NOT_ISSUED" if not tickets else "CHECKED_IN" if checked_in_count == len(tickets) else "PARTIAL" if checked_in_count else "NOT_CHECKED_IN"
    can_cancel = booking.status in {"PENDING", "CONFIRMED", "CANCEL_REQUESTED"} and showtime.starts_at > datetime.now(timezone.utc) and checked_in_count == 0 and booking.checked_in_at is None
    return {
        "id": booking.id,
        "ticket_code": booking.ticket_code,
        "user_id": booking.user_id,
        "showtime_id": booking.showtime_id,
        "movie_id": showtime.movie_id,
        "movie_title": showtime.movie.title,
        "branch_id": auditorium.branch_id,
        "branch_name": auditorium.branch.name,
        "auditorium_name": auditorium.name,
        "starts_at": showtime.starts_at,
        "seats": (
            [{"id": item.seat_id, "row": item.seat.seat_row, "number": item.seat.seat_number} for item in booking.seats]
            or list(booking.seat_snapshot or [])
        ),
        "quantity": len(booking.seats) or len(booking.seat_snapshot or []),
        "ticket_count": len(tickets),
        "checked_in_count": checked_in_count,
        "checkin_status": checkin_status,
        "checked_in_at": booking.checked_in_at or next((item.checked_in_at for item in tickets if item.checked_in_at), None),
        "can_cancel": can_cancel,
        "total_price": float(booking.total_price),
        "subtotal_price": float(booking.subtotal_price),
        "discount_amount": float(booking.discount_amount),
        "sales_channel": booking.sales_channel,
        "customer_name": booking.customer_name or (customer.full_name if customer else "Khách hàng"),
        "customer_email": booking.customer_email or (customer.email if customer else None),
        "customer_phone": booking.customer_phone or (customer.phone if customer else None),
        "promotion_code": booking.promotion.code if booking.promotion else None,
        "combos": [
            {
                "name": item.combo_name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "line_total": float(item.line_total),
                "inventory_status": item.inventory_status,
            }
            for item in booking.combos
        ],
        "payments": [
            {
                "id": item.id,
                "method": item.payment_method,
                "status": item.status,
                "amount": float(item.amount),
                "provider_ref": item.provider_ref,
                "transaction_no": item.provider_transaction_no or item.transaction_id,
                "paid_at": item.paid_at,
                "refund_error": item.refund_error,
            }
            for item in sorted(booking.payments, key=lambda row: row.created_at, reverse=True)
        ],
        "status": booking.status,
        "cancellation_reason": booking.cancellation_reason,
        "cancellation_requested_at": booking.cancellation_requested_at,
        "cancellation_review_note": booking.cancellation_review_note,
        "cancellation_reviewed_at": booking.cancellation_reviewed_at,
        "cancelled_at": booking.cancelled_at,
        "created_at": booking.created_at,
    }

@router.get("/bookings", dependencies=[Depends(require_branch_admin)])
async def list_branch_bookings(
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
    search: str | None = Query(None, max_length=100),
    movie_id: UUID | None = None,
    branch_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = _parse_date_boundary(start_date)
    end = _parse_date_boundary(end_date, end=True)
    assigned_branch_id = await _staff_branch_id(db, current_user)
    filters = []
    if assigned_branch_id is not None:
        if branch_id is not None and branch_id != assigned_branch_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view another branch")
        filters.append(Auditorium.branch_id == assigned_branch_id)
    elif branch_id is not None:
        filters.append(Auditorium.branch_id == branch_id)
    if start is not None:
        filters.append(Booking.created_at >= start)
    if end is not None:
        filters.append(Booking.created_at <= end)
    if status:
        filters.append(Booking.status == status.upper())
    if movie_id is not None:
        filters.append(Showtime.movie_id == movie_id)
    term = (search or "").strip()
    if term:
        search_filters = [
            Booking.ticket_code.ilike(f"%{term}%"),
            Booking.customer_name.ilike(f"%{term}%"),
            Booking.customer_email.ilike(f"%{term}%"),
            Booking.customer_phone.ilike(f"%{term}%"),
            User.full_name.ilike(f"%{term}%"),
            User.email.ilike(f"%{term}%"),
            User.phone.ilike(f"%{term}%"),
            Movie.title.ilike(f"%{term}%"),
        ]
        try:
            search_filters.append(Booking.id == UUID(term.lstrip("#")))
        except ValueError:
            pass
        filters.append(or_(*search_filters))

    base = (
        select(Booking, User)
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .join(Movie, Movie.id == Showtime.movie_id)
        .outerjoin(User, User.id == Booking.user_id)
        .options(
            selectinload(Booking.showtime).selectinload(Showtime.movie),
            selectinload(Booking.showtime).selectinload(Showtime.auditorium).selectinload(Auditorium.branch),
            selectinload(Booking.seats).selectinload(BookingSeat.seat),
            selectinload(Booking.payments),
            selectinload(Booking.combos),
            selectinload(Booking.promotion),
        )
        .where(*filters)
    )
    total = await db.scalar(select(func.count()).select_from(base.subquery()))
    summary_rows = (await db.execute(
        select(Booking.status, func.count(Booking.id), func.coalesce(func.sum(Booking.total_price), 0))
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .join(Movie, Movie.id == Showtime.movie_id)
        .outerjoin(User, User.id == Booking.user_id)
        .where(*filters)
        .group_by(Booking.status)
    )).all()
    rows = await db.execute(base.order_by(Booking.created_at.desc()).offset(skip).limit(limit))
    summary = {row_status: int(count) for row_status, count, _ in summary_rows}
    confirmed_value = sum(float(amount) for row_status, _, amount in summary_rows if row_status == "CONFIRMED")
    return {
        "total": total or 0,
        "summary": {**summary, "CONFIRMED_VALUE": confirmed_value},
        "bookings": [_booking_admin_dict(booking, customer) for booking, customer in rows.all()],
    }


@router.put("/bookings/{booking_id}/cancel", dependencies=[Depends(require_roles("BRANCH_ADMIN"))])
async def cancel_booking(
    booking_id: UUID,
    request: Request,
    reason: str = Query(min_length=5, max_length=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Booking)
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .options(
            selectinload(Booking.showtime).selectinload(Showtime.movie),
            selectinload(Booking.showtime).selectinload(Showtime.auditorium).selectinload(Auditorium.branch),
            selectinload(Booking.seats).selectinload(BookingSeat.seat),
        )
        .where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    await _ensure_branch_access(db, current_user, booking.showtime.auditorium.branch_id)
    if booking.status == "CANCELLED":
        return _booking_admin_dict(booking)
    if booking.status not in {"PENDING", "CONFIRMED", "CANCEL_REQUESTED"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking cannot be cancelled")
    if booking.showtime.starts_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "BOOKING_SHOWTIME_STARTED"})
    checked_in_tickets = await db.scalar(select(func.count(Ticket.id)).where(Ticket.booking_id == booking.id, Ticket.status == "USED"))
    if booking.checked_in_at is not None or checked_in_tickets:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "BOOKING_ALREADY_CHECKED_IN"})
    if not booking.seat_snapshot:
        booking.seat_snapshot = [
            {"id": str(item.seat_id), "row": item.seat.seat_row, "number": item.seat.seat_number}
            for item in booking.seats
        ]
    previous_status = booking.status
    booking.status = "CANCELLED"
    booking.cancellation_reason = reason.strip()
    booking.cancelled_at = datetime.now(timezone.utc)
    booking.cancelled_by = current_user.id
    booking.cancellation_review_note = reason.strip()
    booking.cancellation_reviewed_at = datetime.now(timezone.utc)
    booking.cancellation_reviewed_by = current_user.id
    await release_booking_combo_inventory(db, [booking.id], include_sold=True)
    await db.execute(
        update(Ticket).where(Ticket.booking_id == booking.id).values(status="CANCELLED")
    )
    await db.execute(delete(BookingSeat).where(BookingSeat.booking_id == booking.id))
    payments_to_refund: list[Payment] = []
    for payment in (await db.execute(select(Payment).where(Payment.booking_id == booking.id))).scalars():
        if payment.status == "SUCCESS":
            payment.status = "REFUND_PENDING"
            payments_to_refund.append(payment)
            db.add(PaymentStatusHistory(
                payment_id=payment.id,
                old_status="SUCCESS",
                new_status="REFUND_PENDING",
                source="BRANCH_ADMIN",
                note=reason.strip(),
                raw_payload={},
            ))
    db.add(AuditEvent(
        entity_type="BOOKING",
        entity_id=str(booking.id),
        action="CANCEL",
        old_data={"status": previous_status},
        new_data={"status": "CANCELLED", "reason": reason.strip()},
        transaction_id=str(current_user.id),
    ))
    await db.commit()
    await db.refresh(booking)
    await seat_events.broadcast(booking.showtime_id, "SEATS_UPDATED")
    for payment in payments_to_refund:
        await _execute_vnpay_refund(
            payment=payment, booking=booking, current_user=current_user,
            request=request, db=db, reason=reason.strip(),
        )
    return {**_booking_admin_dict(booking), "cancel_reason": reason.strip()}


@router.put("/bookings/{booking_id}/reject-cancellation", dependencies=[Depends(require_roles("BRANCH_ADMIN"))])
async def reject_booking_cancellation(
    booking_id: UUID,
    reason: str = Query(min_length=5, max_length=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.showtime).selectinload(Showtime.auditorium).selectinload(Auditorium.branch))
        .where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    await _ensure_branch_access(db, current_user, booking.showtime.auditorium.branch_id)
    if booking.status != "CANCEL_REQUESTED":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking has no cancellation request")
    booking.status = "CONFIRMED"
    booking.cancellation_review_note = reason.strip()
    booking.cancellation_reviewed_at = datetime.now(timezone.utc)
    booking.cancellation_reviewed_by = current_user.id
    booking.cancellation_requested_at = None
    db.add(AuditEvent(
        entity_type="BOOKING",
        entity_id=str(booking.id),
        action="REJECT_CANCEL",
        old_data={"status": "CANCEL_REQUESTED"},
        new_data={"status": "CONFIRMED", "reason": reason.strip()},
        transaction_id=str(current_user.id),
    ))
    await db.commit()
    return _booking_admin_dict(booking)


@router.get("/payments", dependencies=[Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN"))])
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    payment_status: str | None = Query(None, alias="status"),
    payment_id: UUID | None = None,
    booking_id: UUID | None = None,
    search: str | None = Query(None, max_length=120),
    payment_method: str | None = None,
    verification: str | None = None,
    attention_only: bool = False,
    start_date: str | None = None,
    end_date: str | None = None,
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = [Payment.status == payment_status.upper()] if payment_status else []
    if payment_id is not None:
        filters.append(Payment.id == payment_id)
    if booking_id is not None:
        filters.append(Payment.booking_id == booking_id)
    if payment_method:
        filters.append(Payment.payment_method == payment_method.upper())
    if verification:
        verification_key = verification.upper()
        if verification_key == "VALID":
            filters.append(Payment.signature_valid.is_(True))
        elif verification_key == "INVALID":
            filters.append(Payment.signature_valid.is_(False))
        elif verification_key == "UNVERIFIED":
            filters.append(Payment.signature_valid.is_(None))
    if attention_only:
        filters.append(or_(
            Payment.status.in_(["REFUND_PENDING", "REFUND_FAILED", "RECONCILIATION_REQUIRED"]),
            Payment.signature_valid.is_(False),
        ))
    start = _parse_date_boundary(start_date)
    end = _parse_date_boundary(end_date, end=True)
    if start is not None:
        filters.append(Payment.created_at >= start)
    if end is not None:
        filters.append(Payment.created_at <= end)
    term = (search or "").strip()
    if term:
        search_filters = [
            Payment.transaction_id.ilike(f"%{term}%"),
            Payment.provider_ref.ilike(f"%{term}%"),
            Payment.provider_transaction_no.ilike(f"%{term}%"),
            Payment.bank_transaction_no.ilike(f"%{term}%"),
            Booking.ticket_code.ilike(f"%{term}%"),
            Booking.customer_name.ilike(f"%{term}%"),
            Booking.customer_email.ilike(f"%{term}%"),
            User.full_name.ilike(f"%{term}%"),
            User.email.ilike(f"%{term}%"),
            Movie.title.ilike(f"%{term}%"),
        ]
        try:
            query_id = UUID(term.lstrip("#"))
            search_filters.extend([Payment.id == query_id, Booking.id == query_id])
        except ValueError:
            pass
        filters.append(or_(*search_filters))
    assigned_branch_id = await _staff_branch_id(db, current_user)
    if assigned_branch_id is not None:
        if branch_id is not None and branch_id != assigned_branch_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view another branch")
        branch_id = assigned_branch_id
    if branch_id is not None:
        filters.append(Auditorium.branch_id == branch_id)
    base = (
        select(Payment)
        .join(Booking, Booking.id == Payment.booking_id)
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .join(Movie, Movie.id == Showtime.movie_id)
        .outerjoin(User, User.id == Booking.user_id)
        .options(
            selectinload(Payment.booking).selectinload(Booking.showtime).selectinload(Showtime.movie),
            selectinload(Payment.booking).selectinload(Booking.showtime).selectinload(Showtime.auditorium).selectinload(Auditorium.branch),
            selectinload(Payment.booking).selectinload(Booking.seats).selectinload(BookingSeat.seat),
            selectinload(Payment.booking).selectinload(Booking.combos),
            selectinload(Payment.booking).selectinload(Booking.promotion),
        )
        .where(*filters)
    )
    total = await db.scalar(select(func.count()).select_from(base.subquery()))
    summary_rows = (await db.execute(
        select(Payment.status, func.count(Payment.id), func.coalesce(func.sum(Payment.amount), 0))
        .join(Booking, Booking.id == Payment.booking_id)
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .join(Movie, Movie.id == Showtime.movie_id)
        .outerjoin(User, User.id == Booking.user_id)
        .where(*filters)
        .group_by(Payment.status)
    )).all()
    attention_count = await db.scalar(
        select(func.count(Payment.id))
        .join(Booking, Booking.id == Payment.booking_id)
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .join(Movie, Movie.id == Showtime.movie_id)
        .outerjoin(User, User.id == Booking.user_id)
        .where(
            *filters,
            or_(
                Payment.status.in_(["REFUND_PENDING", "REFUND_FAILED", "RECONCILIATION_REQUIRED"]),
                Payment.signature_valid.is_(False),
            ),
        )
    )
    result = await db.execute(
        base
        .order_by(Payment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    payment_items = list(result.scalars().unique().all())
    customer_ids = {item.booking.user_id for item in payment_items}
    customers = {
        customer.id: customer
        for customer in (await db.execute(select(User).where(User.id.in_(customer_ids)))).scalars().all()
    } if customer_ids else {}
    payments = [
        {
            "id": item.id,
            "booking_id": item.booking_id,
            "user_id": item.user_id,
            "amount": float(item.amount),
            "payment_method": item.payment_method,
            "status": item.status,
            "transaction_id": item.transaction_id,
            "provider_ref": item.provider_ref,
            "provider_transaction_no": item.provider_transaction_no,
            "bank_transaction_no": item.bank_transaction_no,
            "bank_code": item.bank_code,
            "card_type": item.card_type,
            "response_code": item.response_code,
            "provider_status": item.provider_status,
            "signature_valid": item.signature_valid,
            "provider_paid_at": item.provider_paid_at,
            "last_verified_at": item.last_verified_at,
            "refund_transaction_no": item.refund_transaction_no,
            "refund_response_code": item.refund_response_code,
            "refund_provider_status": item.refund_provider_status,
            "refund_error": item.refund_error,
            "refund_attempts": item.refund_attempts,
            "refund_requested_at": item.refund_requested_at,
            "refunded_at": item.refunded_at,
            "paid_at": item.paid_at,
            "created_at": item.created_at,
            "booking_status": item.booking.status,
            "booking_code": item.booking.ticket_code,
            "movie_title": item.booking.showtime.movie.title,
            "showtime_starts_at": item.booking.showtime.starts_at,
            "branch_name": item.booking.showtime.auditorium.branch.name,
            "auditorium_name": item.booking.showtime.auditorium.name,
            "customer_name": item.booking.customer_name or (customers.get(item.booking.user_id).full_name if customers.get(item.booking.user_id) else "Khách hàng"),
            "customer_email": item.booking.customer_email or (customers.get(item.booking.user_id).email if customers.get(item.booking.user_id) else None),
            "customer_phone": item.booking.customer_phone or (customers.get(item.booking.user_id).phone if customers.get(item.booking.user_id) else None),
            "seats": [
                {"row": seat.seat.seat_row, "number": seat.seat.seat_number}
                for seat in item.booking.seats
            ] or list(item.booking.seat_snapshot or []),
            "combos": [
                {"name": combo.combo_name, "quantity": combo.quantity, "line_total": float(combo.line_total)}
                for combo in item.booking.combos
            ],
            "promotion_code": item.booking.promotion.code if item.booking.promotion else None,
        }
        for item in payment_items
    ]
    summary = {row_status: int(count) for row_status, count, _ in summary_rows}
    summary["SUCCESS_VALUE"] = sum(float(amount) for row_status, _, amount in summary_rows if row_status == "SUCCESS")
    summary["ATTENTION"] = int(attention_count or 0)
    return {"total": total or 0, "summary": summary, "payments": payments}


@router.get("/payments/{payment_id}/history", dependencies=[Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN"))])
async def payment_history(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    booking = await db.get(Booking, payment.booking_id)
    showtime = await db.get(Showtime, booking.showtime_id)
    auditorium = await db.get(Auditorium, showtime.auditorium_id)
    await _ensure_branch_access(db, current_user, auditorium.branch_id)
    result = await db.execute(
        select(PaymentStatusHistory)
        .where(PaymentStatusHistory.payment_id == payment_id)
        .order_by(PaymentStatusHistory.created_at.desc())
    )
    return [
        {
            "id": item.id,
            "old_status": item.old_status,
            "new_status": item.new_status,
            "source": item.source,
            "response_code": item.response_code,
            "provider_status": item.provider_status,
            "signature_valid": item.signature_valid,
            "note": item.note,
            "raw_payload": item.raw_payload,
            "created_at": item.created_at,
        }
        for item in result.scalars().all()
    ]


@router.post("/payments/{payment_id}/reconcile", dependencies=[Depends(require_roles("BRANCH_ADMIN"))])
async def reconcile_payment(
    payment_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    if payment.payment_method != "VNPAY" or not payment.provider_ref:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This is not a VNPAY transaction")
    booking = await db.get(Booking, payment.booking_id)
    showtime = await db.get(Showtime, booking.showtime_id)
    auditorium = await db.get(Auditorium, showtime.auditorium_id)
    await _ensure_branch_access(db, current_user, auditorium.branch_id)
    if not settings.vnpay_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="VNPAY Sandbox is not configured")
    ip_address = request.client.host if request.client else "127.0.0.1"
    try:
        response = await query_transaction(
            request_id=uuid.uuid4().hex,
            txn_ref=payment.provider_ref,
            transaction_date=payment.created_at,
            ip_address=ip_address,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Không thể kết nối VNPAY để đối soát. Vui lòng thử lại sau.",
        ) from exc
    provider_status = str(response.get("vnp_TransactionStatus", ""))
    response_code = str(response.get("vnp_ResponseCode", ""))
    transaction_type = str(response.get("vnp_TransactionType", ""))
    response_signature_valid = verify_refund_response(response)
    provider_amount = float(response.get("vnp_Amount", 0) or 0) / 100
    amount_matches = provider_amount == float(payment.amount)
    if payment.status in {"REFUND_PENDING", "REFUND_FAILED", "REFUNDED"}:
        status_matches = transaction_type in {"02", "03"} and provider_status in {"00", "05", "06", "09"}
    else:
        status_matches = (
            (payment.status == "SUCCESS" and provider_status == "00")
            or (payment.status != "SUCCESS" and provider_status != "00")
        )
    payment.last_verified_at = datetime.now(timezone.utc)
    old_status = payment.status
    matched = response_signature_valid and amount_matches and status_matches and response_code == "00"
    if response_signature_valid and payment.status in {"REFUND_PENDING", "REFUND_FAILED"} and response_code == "00":
        if transaction_type in {"02", "03"} and provider_status == "00":
            payment.status = "REFUNDED"
            payment.refunded_at = datetime.now(timezone.utc)
            payment.refund_error = None
            await _release_used_promotion(db, payment.id)
        elif provider_status in {"05", "06"}:
            payment.status = "REFUND_PENDING"
        elif provider_status == "09":
            payment.status = "REFUND_FAILED"
            payment.refund_error = "VNPAY rejected the refund"
    elif response_signature_valid and response_code == "00" and not matched and payment.status not in {"REFUND_PENDING", "REFUND_FAILED", "REFUNDED"}:
        payment.status = "RECONCILIATION_REQUIRED"
    db.add(PaymentStatusHistory(
        payment_id=payment.id,
        old_status=old_status,
        new_status=payment.status,
        source="QUERY_DR",
        response_code=response_code or None,
        provider_status=provider_status or None,
        signature_valid=response_signature_valid,
        note="Matched" if matched else "Invalid VNPAY response signature" if not response_signature_valid else "Reconciliation mismatch",
        raw_payload={str(key): str(value) for key, value in response.items()},
    ))
    await db.commit()
    return {
        "matched": matched,
        "response_signature_valid": response_signature_valid,
        "amount_matches": amount_matches,
        "status_matches": status_matches,
        "local_status": payment.status,
        "provider_status": provider_status,
        "provider_transaction_no": response.get("vnp_TransactionNo"),
        "provider_amount": provider_amount,
        "response": response,
    }


@router.post("/payments/{payment_id}/refund", dependencies=[Depends(require_roles("BRANCH_ADMIN"))])
async def refund_payment(
    payment_id: UUID,
    request: Request,
    reason: str = Query(min_length=5, max_length=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    booking = await db.get(Booking, payment.booking_id)
    showtime = await db.get(Showtime, booking.showtime_id)
    auditorium = await db.get(Auditorium, showtime.auditorium_id)
    await _ensure_branch_access(db, current_user, auditorium.branch_id)
    if payment.status == "REFUNDED":
        return {"id": payment.id, "status": payment.status, "reason": reason.strip()}
    if payment.status == "REFUND_PENDING":
        return {
            "id": payment.id,
            "booking_id": payment.booking_id,
            "status": payment.status,
            "reason": reason.strip(),
            "refund_error": payment.refund_error,
            "refund_transaction_no": payment.refund_transaction_no,
        }
    if payment.status not in {"SUCCESS", "REFUND_FAILED"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only successful payments can be refunded")
    if booking is None or booking.status != "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cancel or approve the booking cancellation before refunding its payment",
        )
    await _execute_vnpay_refund(
        payment=payment, booking=booking, current_user=current_user,
        request=request, db=db, reason=reason.strip(),
    )
    return {
        "id": payment.id, "booking_id": payment.booking_id, "status": payment.status,
        "reason": reason.strip(), "refund_error": payment.refund_error,
        "refund_transaction_no": payment.refund_transaction_no,
    }


@router.post("/tickets/scan", dependencies=[Depends(require_roles("BRANCH_ADMIN"))])
async def scan_ticket(
    payload: TicketScanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket_id = None
    legacy_code = None
    scan_code = None
    compact_signature = None
    try:
        ticket_id = parse_signed_ticket_qr(payload.qr_data)
    except ValueError:
        try:
            scan_code = parse_ticket_scan_code(payload.qr_data)
        except ValueError:
            try:
                legacy_code, compact_signature = parse_compact_ticket_qr(payload.qr_data)
            except ValueError:
                try:
                    legacy_code = parse_ticket_qr_payload(payload.qr_data)
                except ValueError:
                    return {"state": "INVALID", "message": "Mã QR không đúng định dạng hoặc chữ ký không hợp lệ."}

    ticket_filter = (
        Ticket.id == ticket_id
        if ticket_id
        else Ticket.scan_code == scan_code
        if scan_code
        else or_(Ticket.ticket_code == legacy_code, Ticket.booking.has(Booking.ticket_code == legacy_code))
    )
    result = await db.execute(
        select(Ticket)
        .options(
            selectinload(Ticket.booking).selectinload(Booking.showtime).selectinload(Showtime.movie),
            selectinload(Ticket.booking).selectinload(Booking.showtime)
            .selectinload(Showtime.auditorium)
            .selectinload(Auditorium.branch),
        )
        .where(ticket_filter)
        .order_by(Ticket.ticket_code)
        .limit(1)
        .with_for_update()
    )
    ticket = result.scalar_one_or_none()
    if ticket is None:
        return {"state": "NOT_FOUND", "message": "Không tìm thấy vé này trong hệ thống."}
    if compact_signature and not verify_compact_ticket_qr(ticket.ticket_code, ticket.qr_nonce, compact_signature):
        return {"state": "INVALID", "message": "Chữ ký QR không hợp lệ."}
    booking = ticket.booking
    customer = await db.get(User, booking.user_id)
    booking_ticket_rows = await db.execute(
        select(Ticket)
        .where(Ticket.booking_id == booking.id)
        .order_by(Ticket.ticket_code)
        .with_for_update()
    )
    booking_tickets = list(booking_ticket_rows.scalars().all())

    branch = booking.showtime.auditorium.branch
    assigned_branch_id = await _staff_branch_id(db, current_user)
    if assigned_branch_id is not None and assigned_branch_id != branch.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vé này thuộc một chi nhánh khác.",
        )

    now = datetime.now(timezone.utc)
    state = ticket_checkin_state(
        booking.status,
        booking.showtime.ends_at,
        None,
        now,
        booking.showtime.starts_at,
    )
    if any(item.status == "CANCELLED" for item in booking_tickets):
        state = "CANCELLED"
    elif booking_tickets and all(item.status == "USED" for item in booking_tickets):
        state = "ALREADY_USED"
    if payload.consume and state == "VALID":
        checked_in_ticket_codes = [item.ticket_code for item in booking_tickets if item.status != "USED"]
        for item in booking_tickets:
            if item.status != "USED":
                item.status = "USED"
                item.checked_in_at = now
                item.checked_in_by = current_user.id
        booking.checked_in_at = now
        booking.checked_in_by = current_user.id
        db.add(AuditEvent(
            entity_type="BOOKING",
            entity_id=str(booking.id),
            action="CHECK_IN_BOOKING",
            old_data={"ticket_codes": checked_in_ticket_codes},
            new_data={
                "ticket_codes": [item.ticket_code for item in booking_tickets],
                "seats": [f"{item.seat_row}{item.seat_number}" for item in booking_tickets],
                "checked_in_by": str(current_user.id),
            },
            transaction_id=str(current_user.id),
        ))
        await db.commit()
        state = "CHECKED_IN"

    messages = {
        "VALID": "Vé hợp lệ, có thể xác nhận cho khách vào rạp.",
        "CHECKED_IN": "Đã check-in toàn bộ ghế trong đơn đặt vé.",
        "ALREADY_USED": "Toàn bộ ghế trong đơn đã được check-in trước đó.",
        "EXPIRED": "Vé đã hết hạn vì suất chiếu đã kết thúc.",
        "CANCELLED": "Vé đã bị hủy.",
        "CANCEL_REQUESTED": "Vé đang chờ xử lý yêu cầu hủy.",
        "NOT_CONFIRMED": "Vé chưa được thanh toán hoặc chưa xác nhận.",
        "TOO_EARLY": "Chưa đến thời gian cho phép soát vé.",
    }
    return {
        "state": state,
        "message": messages[state],
        "ticket_code": booking.ticket_code,
        "scanned_ticket_code": ticket.ticket_code,
        "booking_ticket_code": booking.ticket_code,
        "ticket_codes": [item.ticket_code for item in booking_tickets],
        "ticket_count": len(booking_tickets),
        "used_count": sum(1 for item in booking_tickets if item.status == "USED"),
        "remaining_count": sum(1 for item in booking_tickets if item.status != "USED"),
        "ticket_details": [
            {
                "ticket_code": item.ticket_code,
                "seat": f"{item.seat_row}{item.seat_number}",
                "status": item.status,
                "checked_in_at": item.checked_in_at,
            }
            for item in booking_tickets
        ],
        "customer_name": booking.customer_name or (customer.full_name if customer else "Khách vãng lai"),
        "movie_title": booking.showtime.movie.title,
        "branch_name": branch.name,
        "auditorium_name": booking.showtime.auditorium.name,
        "starts_at": booking.showtime.starts_at,
        "ends_at": booking.showtime.ends_at,
        "checkin_opens_at": booking.showtime.starts_at - timedelta(minutes=60),
        "server_time": now,
        "seats": [f"{item.seat_row}{item.seat_number}" for item in booking_tickets],
        "checked_in_at": booking.checked_in_at or next((item.checked_in_at for item in booking_tickets if item.checked_in_at), None),
    }


REPORT_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


def _report_boundaries(start_value: str, end_value: str) -> tuple[datetime, datetime]:
    try:
        start_day = date.fromisoformat(start_value)
        end_day = date.fromisoformat(end_value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Date must use YYYY-MM-DD format") from exc
    if start_day > end_day:
        raise HTTPException(status_code=422, detail="start_date must be before end_date")
    start = datetime.combine(start_day, time.min, tzinfo=REPORT_TIMEZONE).astimezone(timezone.utc)
    end = datetime.combine(end_day, time.max, tzinfo=REPORT_TIMEZONE).astimezone(timezone.utc)
    return start, end


def _successful_payment_scope(start: datetime, end: datetime, branch_id: UUID | None):
    filters = [Payment.status == "SUCCESS", Payment.paid_at >= start, Payment.paid_at <= end]
    if branch_id is not None:
        filters.append(Auditorium.branch_id == branch_id)
    return filters


@router.get("/reports/revenue", dependencies=[Depends(require_admin)])
async def get_revenue_report(
    start_date: str,
    end_date: str,
    group_by: str = Query("day", pattern="day|week|month"),
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    start, end = _report_boundaries(start_date, end_date)
    local_paid_at = func.timezone("Asia/Ho_Chi_Minh", Payment.paid_at)
    bucket = func.date_trunc(group_by, local_paid_at)
    filters = _successful_payment_scope(start, end, branch_id)
    trend_rows = await db.execute(
        select(bucket.label("bucket"), func.coalesce(func.sum(Payment.amount), 0).label("revenue"))
        .join(Booking, Booking.id == Payment.booking_id)
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .where(*filters)
        .group_by(bucket)
        .order_by(bucket)
    )
    data = [{"label": row.bucket.date().isoformat(), "value": float(row.revenue)} for row in trend_rows]

    ticket_totals = (
        select(
            BookingSeat.booking_id.label("booking_id"),
            func.coalesce(func.sum(BookingSeat.unit_price), 0).label("ticket_revenue"),
            func.count(BookingSeat.id).label("tickets_sold"),
        )
        .group_by(BookingSeat.booking_id)
        .subquery()
    )
    combo_totals = (
        select(
            BookingCombo.booking_id.label("booking_id"),
            func.coalesce(func.sum(BookingCombo.line_total), 0).label("combo_revenue"),
        )
        .group_by(BookingCombo.booking_id)
        .subquery()
    )
    recorded_ticket_revenue = func.coalesce(ticket_totals.c.ticket_revenue, 0)
    recorded_combo_revenue = func.coalesce(combo_totals.c.combo_revenue, 0)
    gross_booking_value = func.greatest(
        func.coalesce(Booking.subtotal_price, 0),
        func.coalesce(Booking.total_price, 0) + func.coalesce(Booking.discount_amount, 0),
    )
    effective_ticket_revenue = case(
        (recorded_ticket_revenue > 0, recorded_ticket_revenue),
        else_=func.greatest(gross_booking_value - recorded_combo_revenue, 0),
    )
    breakdown = (await db.execute(
        select(
            func.coalesce(func.sum(Payment.amount), 0).label("total"),
            func.coalesce(func.sum(effective_ticket_revenue), 0).label("ticket_revenue"),
            func.coalesce(func.sum(recorded_combo_revenue), 0).label("combo_revenue"),
            func.coalesce(func.sum(Booking.discount_amount), 0).label("discount_amount"),
            func.coalesce(func.sum(ticket_totals.c.tickets_sold), 0).label("tickets_sold"),
        )
        .select_from(Payment)
        .join(Booking, Booking.id == Payment.booking_id)
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .outerjoin(ticket_totals, ticket_totals.c.booking_id == Booking.id)
        .outerjoin(combo_totals, combo_totals.c.booking_id == Booking.id)
        .where(*filters)
    )).one()

    period_days = (date.fromisoformat(end_date) - date.fromisoformat(start_date)).days + 1
    previous_end = start - timedelta(microseconds=1)
    previous_start = previous_end - timedelta(days=period_days) + timedelta(microseconds=1)
    previous_filters = _successful_payment_scope(previous_start, previous_end, branch_id)
    previous_total = float(await db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .join(Booking, Booking.id == Payment.booking_id)
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .where(*previous_filters)
    ) or 0)
    current_total = float(breakdown.total)
    change_percent = round((current_total - previous_total) * 100 / previous_total, 1) if previous_total else None

    refund_filters = [Payment.status == "REFUNDED", Payment.refunded_at >= start, Payment.refunded_at <= end]
    if branch_id is not None:
        refund_filters.append(Auditorium.branch_id == branch_id)
    refunded_amount = float(await db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .join(Booking, Booking.id == Payment.booking_id)
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .where(*refund_filters)
    ) or 0)
    return {
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "Asia/Ho_Chi_Minh",
        "group_by": group_by,
        "total": current_total,
        "ticket_revenue": float(breakdown.ticket_revenue),
        "combo_revenue": float(breakdown.combo_revenue),
        "discount_amount": float(breakdown.discount_amount),
        "refunded_amount": refunded_amount,
        "tickets_sold": int(breakdown.tickets_sold),
        "previous_total": previous_total,
        "change_percent": change_percent,
        "data": data,
    }


@router.get("/reports/occupancy", dependencies=[Depends(require_admin)])
async def get_occupancy_report(
    start_date: str,
    end_date: str,
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    start, end = _report_boundaries(start_date, end_date)
    showtime_filters = [Showtime.starts_at >= start, Showtime.starts_at <= end, Showtime.status != "CANCELLED"]
    if branch_id is not None:
        showtime_filters.append(Auditorium.branch_id == branch_id)
    offered = (
        select(
            Showtime.id.label("showtime_id"),
            Auditorium.branch_id.label("branch_id"),
            Auditorium.total_seats.label("capacity"),
        )
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .where(*showtime_filters)
        .subquery()
    )
    sold = (
        select(Booking.showtime_id.label("showtime_id"), func.count(BookingSeat.id).label("sold"))
        .join(BookingSeat, BookingSeat.booking_id == Booking.id)
        .where(Booking.status == "CONFIRMED")
        .group_by(Booking.showtime_id)
        .subquery()
    )
    result = await db.execute(
        select(
            Branch.id,
            Branch.name,
            func.count(offered.c.showtime_id).label("showtimes"),
            func.coalesce(func.sum(offered.c.capacity), 0).label("capacity"),
            func.coalesce(func.sum(sold.c.sold), 0).label("sold"),
        )
        .select_from(offered)
        .join(Branch, Branch.id == offered.c.branch_id)
        .outerjoin(sold, sold.c.showtime_id == offered.c.showtime_id)
        .group_by(Branch.id, Branch.name)
        .order_by(Branch.name)
    )
    data = []
    for row in result:
        capacity, booked = int(row.capacity), int(row.sold)
        data.append({
            "branch_id": row.id,
            "branch_name": row.name,
            "showtimes": int(row.showtimes),
            "capacity": capacity,
            "sold": booked,
            "occupancy_rate": round(booked * 100 / capacity, 2) if capacity else 0,
        })
    total_capacity = sum(item["capacity"] for item in data)
    total_sold = sum(item["sold"] for item in data)
    return {
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "Asia/Ho_Chi_Minh",
        "total_capacity": total_capacity,
        "total_sold": total_sold,
        "occupancy_rate": round(total_sold * 100 / total_capacity, 2) if total_capacity else 0,
        "data": data,
    }


@router.get("/reports/top-movies", dependencies=[Depends(require_admin)])
async def get_top_movies(
    start_date: str,
    end_date: str,
    limit: int = Query(10, ge=1, le=50),
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    start, end = _report_boundaries(start_date, end_date)
    payment_totals = (
        select(
            Payment.booking_id.label("booking_id"),
            func.sum(Payment.amount).label("order_revenue"),
            func.max(Payment.paid_at).label("paid_at"),
        )
        .where(Payment.status == "SUCCESS")
        .group_by(Payment.booking_id)
        .subquery()
    )
    ticket_totals = (
        select(
            BookingSeat.booking_id.label("booking_id"),
            func.count(BookingSeat.id).label("tickets_sold"),
            func.sum(BookingSeat.unit_price).label("ticket_revenue"),
        )
        .group_by(BookingSeat.booking_id)
        .subquery()
    )
    combo_totals = (
        select(
            BookingCombo.booking_id.label("booking_id"),
            func.coalesce(func.sum(BookingCombo.line_total), 0).label("combo_revenue"),
        )
        .group_by(BookingCombo.booking_id)
        .subquery()
    )
    recorded_ticket_revenue = func.coalesce(ticket_totals.c.ticket_revenue, 0)
    recorded_combo_revenue = func.coalesce(combo_totals.c.combo_revenue, 0)
    gross_booking_value = func.greatest(
        func.coalesce(Booking.subtotal_price, 0),
        func.coalesce(Booking.total_price, 0) + func.coalesce(Booking.discount_amount, 0),
    )
    effective_ticket_revenue = case(
        (recorded_ticket_revenue > 0, recorded_ticket_revenue),
        else_=func.greatest(gross_booking_value - recorded_combo_revenue, 0),
    )
    filters = [
        Booking.status == "CONFIRMED",
        payment_totals.c.paid_at >= start,
        payment_totals.c.paid_at <= end,
    ]
    if branch_id is not None:
        filters.append(Auditorium.branch_id == branch_id)
    result = await db.execute(
        select(
            Movie.id,
            Movie.title,
            Movie.poster_url,
            func.sum(ticket_totals.c.tickets_sold).label("tickets_sold"),
            func.sum(effective_ticket_revenue).label("ticket_revenue"),
            func.sum(payment_totals.c.order_revenue).label("order_revenue"),
            func.sum(func.sum(ticket_totals.c.tickets_sold)).over().label("total_tickets_sold"),
            func.count(Movie.id).over().label("total_movies"),
        )
        .select_from(Movie)
        .join(Showtime, Showtime.movie_id == Movie.id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .join(Booking, Booking.showtime_id == Showtime.id)
        .join(payment_totals, payment_totals.c.booking_id == Booking.id)
        .join(ticket_totals, ticket_totals.c.booking_id == Booking.id)
        .outerjoin(combo_totals, combo_totals.c.booking_id == Booking.id)
        .where(*filters)
        .group_by(Movie.id, Movie.title, Movie.poster_url)
        .order_by(func.sum(effective_ticket_revenue).desc(), func.sum(ticket_totals.c.tickets_sold).desc())
        .limit(limit)
    )
    return [
        {
            "rank": rank,
            "movie_id": row.id,
            "title": row.title,
            "poster_url": row.poster_url,
            "tickets_sold": int(row.tickets_sold),
            "revenue": float(row.ticket_revenue),
            "ticket_revenue": float(row.ticket_revenue),
            "order_revenue": float(row.order_revenue),
            "total_tickets_sold": int(row.total_tickets_sold),
            "total_movies": int(row.total_movies),
        }
        for rank, row in enumerate(result, start=1)
    ]
