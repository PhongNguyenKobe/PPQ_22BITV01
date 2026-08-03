from datetime import date, datetime, time, timedelta, timezone
import re
import unicodedata
from uuid import UUID
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy import delete, func, or_, select, text
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
from app.db.session import get_db
from app.models.catalog import Auditorium, Branch, Movie, MovieGenre, Seat, SeatType, Showtime, Vendor
from app.core.config import settings
from app.core.tickets import parse_ticket_qr_payload, ticket_checkin_state
from app.models.commerce import Booking, BookingSeat, Payment, PaymentStatusHistory
from app.services.vnpay import query_transaction, refund_transaction, verify_refund_response
from app.models.user import Role, User
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


class TicketScanRequest(BaseModel):
    qr_data: str = Field(min_length=1, max_length=100)
    consume: bool = False


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
    result = await db.execute(
        select(Movie).options(selectinload(Movie.genres)).where(
            or_(Movie.tmdb_id == payload.tmdb_id, Movie.title == payload.title)
        )
    )
    existing = result.scalars().first()
    if existing is not None:
        existing.tmdb_id = payload.tmdb_id
        existing.original_title = payload.original_title or existing.original_title
        existing.description = payload.overview or existing.description
        existing.duration_min = payload.duration_min
        existing.release_date = payload.release_date or existing.release_date
        existing.language = payload.language or existing.language
        existing.trailer_url = payload.trailer_url or existing.trailer_url
        existing.poster_url = poster_url or existing.poster_url
        existing.director = payload.director or existing.director
        existing.cast_names = payload.cast_names or existing.cast_names
        existing.status = payload.status
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
        age_rating="P",
        language=payload.language,
        trailer_url=payload.trailer_url,
        poster_url=poster_url,
        director=payload.director,
        cast_names=payload.cast_names,
        status=payload.status,
    )
    movie.genres = await _resolve_genres(db, payload.genres)
    db.add(movie)
    await db.commit()
    await db.refresh(movie)

    return TmdbMovieImportResponse(id=movie.id, title=movie.title, imported=True)


@router.get("/stats", response_model=AdminStatsResponse)
async def read_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> AdminStatsResponse:
    return AdminStatsResponse(**await get_live_admin_stats(db))


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

        if payload.role_code != "CUSTOMER":
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Branch is required for branch-admin/staff") from None
        if message == "ROLE_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected role is not configured") from None
        raise

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
        updated.is_active = payload.is_active
        db.add(updated)
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

    updated_user = await set_user_role(db, user, payload)

    branch_rows = await list_users_with_branch_id(db)
    branch_id = next((item_branch for item_user, item_branch in branch_rows if item_user.id == updated_user.id), None)
    return AdminUserRead.model_validate(updated_user).model_copy(update={"branch_id": branch_id})


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> None:
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete yourself")

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = False
    db.add(user)
    await db.execute(text("UPDATE branch_staff SET is_active = FALSE WHERE user_id = :user_id"), {"user_id": str(user_id)})
    await db.commit()


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


@router.post("/branches", response_model=BranchManageRead, status_code=status.HTTP_201_CREATED)
async def create_branch_simple(
    payload: BranchManageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> BranchManageRead:
    return await create_admin_branch(payload, db, current_user)


@router.put("/branches/{branch_id:uuid}", response_model=BranchManageRead)
async def update_branch_simple(
    branch_id: UUID,
    payload: BranchManageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> BranchManageRead:
    return await update_admin_branch(branch_id, payload, db, current_user)


@router.delete("/branches/{branch_id:uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_branch_simple(
    branch_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> None:
    await delete_admin_branch(branch_id, db, current_user)


# ---------------------------------------------------------------------------
# Branch management (full implementation)
# ---------------------------------------------------------------------------

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
        rows.append(
            BranchManageRead(
                id=branch.id,
                vendor_id=branch.vendor_id,
                code=branch.code,
                name=branch.name,
                address_line=branch.address_line,
                city=branch.city,
                district=branch.district,
                phone=branch.phone,
                is_active=branch.is_active,
                auditoriums_count=int(count or 0),
            )
        )
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
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Branch code must be unique") from None

    await db.refresh(branch)
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
        auditoriums_count=0,
    )


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

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(branch, key, value)

    db.add(branch)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Branch update conflict") from None

    count_result = await db.execute(select(func.count(Auditorium.id)).where(Auditorium.branch_id == branch.id))
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
        auditoriums_count=int(count_result.scalar() or 0),
    )


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

    await db.delete(branch)
    try:
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
    rows: list[AuditoriumRead] = []
    for item in result.scalars().all():
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

    item = Auditorium(**payload.model_dump())
    db.add(item)
    try:
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

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    db.add(item)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Auditorium update conflict") from None

    return AuditoriumRead(
        id=item.id,
        branch_id=item.branch_id,
        branch_name=item.branch.name if item.branch else "",
        code=item.code,
        name=item.name,
        total_seats=item.total_seats,
        screen_type=item.screen_type,
        is_active=item.is_active,
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

    conflict = await db.scalar(
        select(func.count(Showtime.id)).where(
            Showtime.auditorium_id == payload.auditorium_id,
            Showtime.status != "CANCELLED",
            Showtime.starts_at < payload.ends_at,
            Showtime.ends_at > payload.starts_at,
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

    ordered = sorted(payload.showtimes, key=lambda item: (str(item.auditorium_id), item.starts_at))
    for index, item in enumerate(ordered):
        if item.starts_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="All showtimes must start in the future")
        if item.ends_at <= item.starts_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Every end time must be after its start time")
        booking_closes_at = item.booking_closes_at or item.starts_at - timedelta(minutes=15)
        if item.status == "OPEN" and booking_closes_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot create an open showtime after its sales closing time",
            )
        for other in ordered[index + 1:]:
            if other.auditorium_id != item.auditorium_id:
                continue
            if other.starts_at < item.ends_at and other.ends_at > item.starts_at:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Generated schedule contains overlapping showtimes")

    min_start = min(item.starts_at for item in ordered)
    max_end = max(item.ends_at for item in ordered)
    existing_result = await db.execute(
        select(Showtime).where(
            Showtime.auditorium_id.in_(auditorium_ids),
            Showtime.status != "CANCELLED",
            Showtime.starts_at < max_end,
            Showtime.ends_at > min_start,
        )
    )
    existing = list(existing_result.scalars().all())
    for item in ordered:
        if any(
            row.auditorium_id == item.auditorium_id
            and row.starts_at < item.ends_at
            and row.ends_at > item.starts_at
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
            Showtime.ends_at > new_starts_at,
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


def _booking_admin_dict(booking: Booking) -> dict:
    showtime = booking.showtime
    auditorium = showtime.auditorium
    return {
        "id": booking.id,
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
        "total_price": float(booking.total_price),
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

    base = (
        select(Booking)
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .options(
            selectinload(Booking.showtime).selectinload(Showtime.movie),
            selectinload(Booking.showtime).selectinload(Showtime.auditorium).selectinload(Auditorium.branch),
            selectinload(Booking.seats).selectinload(BookingSeat.seat),
        )
        .where(*filters)
    )
    total = await db.scalar(select(func.count()).select_from(base.subquery()))
    rows = await db.execute(base.order_by(Booking.created_at.desc()).offset(skip).limit(limit))
    return {"total": total or 0, "bookings": [_booking_admin_dict(item) for item in rows.scalars().all()]}


@router.put("/bookings/{booking_id}/cancel", dependencies=[Depends(require_roles("BRANCH_ADMIN"))])
async def cancel_booking(
    booking_id: UUID,
    request: Request,
    reason: str | None = None,
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
    if not booking.seat_snapshot:
        booking.seat_snapshot = [
            {"id": str(item.seat_id), "row": item.seat.seat_row, "number": item.seat.seat_number}
            for item in booking.seats
        ]
    booking.status = "CANCELLED"
    booking.cancellation_reason = reason
    booking.cancelled_at = datetime.now(timezone.utc)
    booking.cancelled_by = current_user.id
    booking.cancellation_review_note = reason
    booking.cancellation_reviewed_at = datetime.now(timezone.utc)
    booking.cancellation_reviewed_by = current_user.id
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
                note=reason or "Booking cancelled by branch",
                raw_payload={},
            ))
    await db.commit()
    await db.refresh(booking)
    await seat_events.broadcast(booking.showtime_id, "SEATS_UPDATED")
    for payment in payments_to_refund:
        await _execute_vnpay_refund(
            payment=payment, booking=booking, current_user=current_user,
            request=request, db=db, reason=reason or "Booking cancellation approved",
        )
    return {**_booking_admin_dict(booking), "cancel_reason": reason}


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
    await db.commit()
    return _booking_admin_dict(booking)


@router.get("/payments", dependencies=[Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN"))])
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    payment_status: str | None = Query(None, alias="status"),
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = [Payment.status == payment_status.upper()] if payment_status else []
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
        .options(selectinload(Payment.booking))
        .where(*filters)
    )
    total = await db.scalar(select(func.count()).select_from(base.subquery()))
    result = await db.execute(
        base
        .order_by(Payment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
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
        }
        for item in result.scalars().all()
    ]
    return {"total": total or 0, "payments": payments}


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
    response = await query_transaction(
        request_id=uuid.uuid4().hex,
        txn_ref=payment.provider_ref,
        transaction_date=payment.created_at,
        ip_address=ip_address,
    )
    provider_status = str(response.get("vnp_TransactionStatus", ""))
    response_code = str(response.get("vnp_ResponseCode", ""))
    transaction_type = str(response.get("vnp_TransactionType", ""))
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
    if payment.status in {"REFUND_PENDING", "REFUND_FAILED"} and response_code == "00":
        if transaction_type in {"02", "03"} and provider_status == "00":
            payment.status = "REFUNDED"
            payment.refunded_at = datetime.now(timezone.utc)
            payment.refund_error = None
        elif provider_status in {"05", "06"}:
            payment.status = "REFUND_PENDING"
        elif provider_status == "09":
            payment.status = "REFUND_FAILED"
            payment.refund_error = "VNPAY rejected the refund"
    db.add(PaymentStatusHistory(
        payment_id=payment.id,
        old_status=old_status,
        new_status=payment.status,
        source="QUERY_DR",
        response_code=response_code or None,
        provider_status=provider_status or None,
        signature_valid=None,
        note="Matched" if amount_matches and status_matches else "Reconciliation mismatch",
        raw_payload={str(key): str(value) for key, value in response.items()},
    ))
    await db.commit()
    return {
        "matched": amount_matches and status_matches and response_code == "00",
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
    reason: str | None = None,
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
        return {"id": payment.id, "status": payment.status, "reason": reason}
    if payment.status == "REFUND_PENDING":
        return {
            "id": payment.id,
            "booking_id": payment.booking_id,
            "status": payment.status,
            "reason": reason,
            "refund_error": payment.refund_error,
            "refund_transaction_no": payment.refund_transaction_no,
        }
    if payment.status not in {"SUCCESS", "REFUND_FAILED"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only successful payments can be refunded")
    if booking is not None:
        seat_rows = await db.execute(
            select(BookingSeat)
            .options(selectinload(BookingSeat.seat))
            .where(BookingSeat.booking_id == booking.id)
        )
        booked_seats = list(seat_rows.scalars().all())
        if not booking.seat_snapshot:
            booking.seat_snapshot = [
                {"id": str(item.seat_id), "row": item.seat.seat_row, "number": item.seat.seat_number}
                for item in booked_seats
            ]
        await db.execute(delete(BookingSeat).where(BookingSeat.booking_id == booking.id))
        booking.status = "CANCELLED"
        booking.cancellation_reason = reason
        booking.cancelled_at = datetime.now(timezone.utc)
        booking.cancelled_by = current_user.id
    await db.commit()
    await _execute_vnpay_refund(
        payment=payment, booking=booking, current_user=current_user,
        request=request, db=db, reason=reason or "Refund requested by branch",
    )
    return {
        "id": payment.id, "booking_id": payment.booking_id, "status": payment.status,
        "reason": reason, "refund_error": payment.refund_error,
        "refund_transaction_no": payment.refund_transaction_no,
    }


@router.post("/tickets/scan", dependencies=[Depends(require_roles("BRANCH_ADMIN"))])
async def scan_ticket(
    payload: TicketScanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        ticket_code = parse_ticket_qr_payload(payload.qr_data)
    except ValueError:
        return {"state": "INVALID", "message": "Mã QR không đúng định dạng vé CineAI."}

    result = await db.execute(
        select(Booking)
        .options(
            selectinload(Booking.showtime).selectinload(Showtime.movie),
            selectinload(Booking.showtime)
            .selectinload(Showtime.auditorium)
            .selectinload(Auditorium.branch),
            selectinload(Booking.seats).selectinload(BookingSeat.seat),
        )
        .where(Booking.ticket_code == ticket_code)
        .with_for_update()
    )
    booking = result.scalar_one_or_none()
    if booking is None:
        return {"state": "NOT_FOUND", "message": "Không tìm thấy vé này trong hệ thống."}

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
        booking.checked_in_at,
        now,
    )
    if payload.consume and state == "VALID":
        booking.checked_in_at = now
        booking.checked_in_by = current_user.id
        await db.commit()
        state = "CHECKED_IN"

    messages = {
        "VALID": "Vé hợp lệ, có thể xác nhận cho khách vào rạp.",
        "CHECKED_IN": "Soát vé thành công.",
        "ALREADY_USED": "Vé đã được sử dụng trước đó.",
        "EXPIRED": "Vé đã hết hạn vì suất chiếu đã kết thúc.",
        "CANCELLED": "Vé đã bị hủy.",
        "CANCEL_REQUESTED": "Vé đang chờ xử lý yêu cầu hủy.",
        "NOT_CONFIRMED": "Vé chưa được thanh toán hoặc chưa xác nhận.",
    }
    return {
        "state": state,
        "message": messages[state],
        "ticket_code": booking.ticket_code,
        "movie_title": booking.showtime.movie.title,
        "branch_name": branch.name,
        "auditorium_name": booking.showtime.auditorium.name,
        "starts_at": booking.showtime.starts_at,
        "ends_at": booking.showtime.ends_at,
        "seats": [f"{item.seat.seat_row}{item.seat.seat_number}" for item in booking.seats],
        "checked_in_at": booking.checked_in_at,
    }


@router.get("/reports/revenue", dependencies=[Depends(require_admin)])
async def get_revenue_report(
    start_date: str,
    end_date: str,
    group_by: str = Query("day", pattern="day|week|month"),
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = _parse_date_boundary(start_date)
    end = _parse_date_boundary(end_date, end=True)
    if start > end:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="start_date must be before end_date")
    if group_by == "month":
        bucket = func.date_trunc("month", Payment.paid_at)
    elif group_by == "week":
        bucket = func.date_trunc("week", Payment.paid_at)
    else:
        bucket = func.date_trunc("day", Payment.paid_at)
    filters = [Payment.status == "SUCCESS", Payment.paid_at >= start, Payment.paid_at <= end]
    if branch_id is not None:
        filters.append(Auditorium.branch_id == branch_id)
    result = await db.execute(
        select(bucket.label("bucket"), func.coalesce(func.sum(Payment.amount), 0).label("revenue"))
        .join(Booking, Booking.id == Payment.booking_id)
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .where(*filters)
        .group_by(bucket)
        .order_by(bucket)
    )
    data = [{"label": row.bucket.date().isoformat(), "value": float(row.revenue)} for row in result]
    return {"start_date": start_date, "end_date": end_date, "group_by": group_by, "total": sum(x["value"] for x in data), "data": data}


@router.get("/reports/occupancy", dependencies=[Depends(require_admin)])
async def get_occupancy_report(
    start_date: str,
    end_date: str,
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = _parse_date_boundary(start_date)
    end = _parse_date_boundary(end_date, end=True)
    filters = [Showtime.starts_at >= start, Showtime.starts_at <= end]
    if branch_id:
        filters.append(Auditorium.branch_id == branch_id)
    capacity = func.sum(Auditorium.total_seats)
    sold = func.count(BookingSeat.id)
    result = await db.execute(
        select(
            Branch.id,
            Branch.name,
            capacity.label("capacity"),
            sold.label("sold"),
        )
        .select_from(Showtime)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .join(Branch, Branch.id == Auditorium.branch_id)
        .outerjoin(Booking, (Booking.showtime_id == Showtime.id) & (Booking.status == "CONFIRMED"))
        .outerjoin(BookingSeat, BookingSeat.booking_id == Booking.id)
        .where(*filters)
        .group_by(Branch.id, Branch.name)
    )
    data = []
    for row in result:
        cap, booked = int(row.capacity or 0), int(row.sold or 0)
        data.append({"branch_id": row.id, "branch_name": row.name, "capacity": cap, "sold": booked, "occupancy_rate": round(booked * 100 / cap, 2) if cap else 0})
    return {"start_date": start_date, "end_date": end_date, "data": data}


@router.get("/reports/top-movies", dependencies=[Depends(require_admin)])
async def get_top_movies(
    start_date: str,
    end_date: str,
    limit: int = Query(10, ge=1, le=50),
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = _parse_date_boundary(start_date)
    end = _parse_date_boundary(end_date, end=True)
    assigned_branch_id = await _staff_branch_id(db, current_user)
    if assigned_branch_id is not None:
        if branch_id is not None and branch_id != assigned_branch_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view another branch")
        branch_id = assigned_branch_id

    payment_totals = (
        select(
            Payment.booking_id.label("booking_id"),
            func.sum(Payment.amount).label("revenue"),
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
        )
        .group_by(BookingSeat.booking_id)
        .subquery()
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
            func.coalesce(func.sum(ticket_totals.c.tickets_sold), 0).label("tickets_sold"),
            func.coalesce(func.sum(payment_totals.c.revenue), 0).label("revenue"),
            func.sum(func.sum(ticket_totals.c.tickets_sold)).over().label("total_tickets_sold"),
            func.count(Movie.id).over().label("total_movies"),
        )
        .select_from(Movie)
        .join(Showtime, Showtime.movie_id == Movie.id)
        .join(Auditorium, Auditorium.id == Showtime.auditorium_id)
        .join(Booking, Booking.showtime_id == Showtime.id)
        .join(payment_totals, payment_totals.c.booking_id == Booking.id)
        .join(ticket_totals, ticket_totals.c.booking_id == Booking.id)
        .where(*filters)
        .group_by(Movie.id, Movie.title)
        .order_by(
            func.sum(payment_totals.c.revenue).desc(),
            func.sum(ticket_totals.c.tickets_sold).desc(),
            Movie.title.asc(),
        )
        .limit(limit)
    )
    return [
        {
            "rank": rank,
            "movie_id": row.id,
            "title": row.title,
            "tickets_sold": int(row.tickets_sold),
            "revenue": float(row.revenue),
            "total_tickets_sold": int(row.total_tickets_sold),
            "total_movies": int(row.total_movies),
        }
        for rank, row in enumerate(result, start=1)
    ]
    booking = await db.get(Booking, payment.booking_id)
    showtime = await db.get(Showtime, booking.showtime_id)
    auditorium = await db.get(Auditorium, showtime.auditorium_id)
    await _ensure_branch_access(db, current_user, auditorium.branch_id)
