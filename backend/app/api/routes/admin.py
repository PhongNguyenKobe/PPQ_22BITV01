from datetime import date, datetime, time, timedelta, timezone
import re
import unicodedata
from uuid import UUID
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_roles
from app.core.permissions import require_admin, require_branch_admin
from app.crud.admin import get_live_admin_stats, list_users_with_branch_id, set_user_role
from app.crud.user import create_user, get_user_by_id, update_user
from app.db.session import get_db
from app.models.catalog import Auditorium, Branch, Movie, MovieGenre, Seat, SeatType, Showtime, Vendor
from app.models.commerce import Booking, BookingSeat, Payment
from app.models.user import User
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
    SeatAdminRead,
    SeatAdminUpdate,
    SeatTypeRead,
    TmdbMovieImportPayload,
    TmdbMovieImportResponse,
    ShowtimeAdminCreate,
    ShowtimeAdminRead,
    ShowtimeAdminUpdate,
    UserRoleUpdate,
)
from app.schemas.movie import MovieRead
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter()


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


async def _resolve_genres(db: AsyncSession, values: list[str]) -> list[MovieGenre]:
    cleaned = list(dict.fromkeys(value.strip() for value in values if value.strip()))
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
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
) -> TmdbMovieImportResponse:
    tmdb_ref_url = f"https://www.themoviedb.org/movie/{payload.tmdb_id}"
    result = await db.execute(
        select(Movie).where(or_(Movie.trailer_url == tmdb_ref_url, Movie.title == payload.title))
    )
    existing = result.scalars().first()
    if existing is not None:
        return TmdbMovieImportResponse(id=existing.id, title=existing.title, imported=False)

    poster_url = f"https://image.tmdb.org/t/p/w500{payload.poster_path}" if payload.poster_path else None

    movie = Movie(
        title=payload.title,
        original_title=payload.original_title or payload.title,
        description=payload.overview,
        duration_min=payload.duration_min,
        release_date=payload.release_date,
        age_rating="P",
        language=payload.language,
        trailer_url=tmdb_ref_url,
        poster_url=poster_url,
        status="NOW_SHOWING",
    )
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
        message = str(exc)
        if message in {"EMAIL_EXISTS", "PHONE_EXISTS"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from None
        if message == "BRANCH_REQUIRED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Branch is required for branch-admin/staff") from None
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
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
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
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
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
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
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
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
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


@router.patch("/seats/{seat_id}", response_model=SeatAdminRead)
async def update_admin_seat(
    seat_id: UUID,
    payload: SeatAdminUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
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
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
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
    rows: list[ShowtimeAdminRead] = []
    for item in result.scalars().all():
        rows.append(
            ShowtimeAdminRead(
                id=item.id,
                movie_id=item.movie_id,
                movie_title=item.movie.title if item.movie else "",
                auditorium_id=item.auditorium_id,
                auditorium_name=item.auditorium.name if item.auditorium else "",
                branch_name=item.auditorium.branch.name if item.auditorium and item.auditorium.branch else "",
                starts_at=item.starts_at,
                ends_at=item.ends_at,
                status=item.status,
                base_price=float(item.base_price),
            )
        )
    return rows


@router.post("/showtimes", response_model=ShowtimeAdminRead, status_code=status.HTTP_201_CREATED)
async def create_admin_showtime(
    payload: ShowtimeAdminCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
) -> ShowtimeAdminRead:
    if payload.ends_at <= payload.starts_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ends_at must be after starts_at")

    movie_row = await db.execute(select(Movie).where(Movie.id == payload.movie_id))
    movie = movie_row.scalar_one_or_none()
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    auditorium_row = await db.execute(select(Auditorium).options(selectinload(Auditorium.branch)).where(Auditorium.id == payload.auditorium_id))
    auditorium = auditorium_row.scalar_one_or_none()
    if auditorium is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auditorium not found")
    await _ensure_branch_access(db, current_user, auditorium.branch_id)

    showtime = Showtime(
        movie_id=payload.movie_id,
        auditorium_id=payload.auditorium_id,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        status=payload.status,
        base_price=payload.base_price,
        created_by=current_user.id,
    )
    db.add(showtime)
    await db.commit()
    await db.refresh(showtime)

    return ShowtimeAdminRead(
        id=showtime.id,
        movie_id=showtime.movie_id,
        movie_title=movie.title,
        auditorium_id=showtime.auditorium_id,
        auditorium_name=auditorium.name,
        branch_name=auditorium.branch.name if auditorium.branch else "",
        starts_at=showtime.starts_at,
        ends_at=showtime.ends_at,
        status=showtime.status,
        base_price=float(showtime.base_price),
    )


@router.patch("/showtimes/{showtime_id}", response_model=ShowtimeAdminRead)
async def update_admin_showtime(
    showtime_id: UUID,
    payload: ShowtimeAdminUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
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
    new_starts_at = updates.get("starts_at", showtime.starts_at)
    new_ends_at = updates.get("ends_at", showtime.ends_at)
    if new_ends_at <= new_starts_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ends_at must be after starts_at")

    if "auditorium_id" in updates and updates["auditorium_id"] is not None:
        auditorium_row = await db.execute(select(Auditorium).where(Auditorium.id == updates["auditorium_id"]))
        target_auditorium = auditorium_row.scalar_one_or_none()
        if target_auditorium is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auditorium not found")
        await _ensure_branch_access(db, current_user, target_auditorium.branch_id)

    for key, value in updates.items():
        setattr(showtime, key, value)

    db.add(showtime)
    await db.commit()

    refreshed_row = await db.execute(
        select(Showtime)
        .options(selectinload(Showtime.movie), selectinload(Showtime.auditorium).selectinload(Auditorium.branch))
        .where(Showtime.id == showtime_id)
    )
    refreshed = refreshed_row.scalar_one_or_none()
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Showtime not found")

    return ShowtimeAdminRead(
        id=refreshed.id,
        movie_id=refreshed.movie_id,
        movie_title=refreshed.movie.title if refreshed.movie else "",
        auditorium_id=refreshed.auditorium_id,
        auditorium_name=refreshed.auditorium.name if refreshed.auditorium else "",
        branch_name=refreshed.auditorium.branch.name if refreshed.auditorium and refreshed.auditorium.branch else "",
        starts_at=refreshed.starts_at,
        ends_at=refreshed.ends_at,
        status=refreshed.status,
        base_price=float(refreshed.base_price),
    )


@router.delete("/showtimes/{showtime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_showtime(
    showtime_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")),
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
        "seats": [
            {"id": item.seat_id, "row": item.seat.seat_row, "number": item.seat.seat_number}
            for item in booking.seats
        ],
        "quantity": len(booking.seats),
        "total_price": float(booking.total_price),
        "status": booking.status,
        "created_at": booking.created_at,
    }

@router.get("/bookings", dependencies=[Depends(require_branch_admin)])
async def list_branch_bookings(
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
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
        filters.append(Auditorium.branch_id == assigned_branch_id)
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


@router.put("/bookings/{booking_id}/cancel", dependencies=[Depends(require_branch_admin)])
async def cancel_booking(
    booking_id: UUID,
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
    if booking.status not in {"PENDING", "CONFIRMED"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking cannot be cancelled")
    booking.status = "CANCELLED"
    for payment in (await db.execute(select(Payment).where(Payment.booking_id == booking.id))).scalars():
        if payment.status == "SUCCESS":
            payment.status = "REFUNDED"
    await db.commit()
    await db.refresh(booking)
    return {**_booking_admin_dict(booking), "cancel_reason": reason}


@router.get("/payments", dependencies=[Depends(require_admin)])
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = [Payment.status == status.upper()] if status else []
    total = await db.scalar(select(func.count(Payment.id)).where(*filters))
    result = await db.execute(
        select(Payment)
        .options(selectinload(Payment.booking))
        .where(*filters)
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
            "paid_at": item.paid_at,
            "created_at": item.created_at,
        }
        for item in result.scalars().all()
    ]
    return {"total": total or 0, "payments": payments}


@router.post("/payments/{payment_id}/refund", dependencies=[Depends(require_admin)])
async def refund_payment(
    payment_id: UUID,
    reason: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    if payment.status == "REFUNDED":
        return {"id": payment.id, "status": payment.status, "reason": reason}
    if payment.status != "SUCCESS":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only successful payments can be refunded")
    payment.status = "REFUNDED"
    booking = await db.get(Booking, payment.booking_id)
    if booking is not None:
        booking.status = "CANCELLED"
    await db.commit()
    return {"id": payment.id, "booking_id": payment.booking_id, "status": payment.status, "reason": reason}


@router.get("/reports/revenue", dependencies=[Depends(require_admin)])
async def get_revenue_report(
    start_date: str,
    end_date: str,
    group_by: str = Query("day", pattern="day|week|month"),
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
    result = await db.execute(
        select(bucket.label("bucket"), func.coalesce(func.sum(Payment.amount), 0).label("revenue"))
        .where(Payment.status == "SUCCESS", Payment.paid_at >= start, Payment.paid_at <= end)
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = _parse_date_boundary(start_date)
    end = _parse_date_boundary(end_date, end=True)
    result = await db.execute(
        select(
            Movie.id,
            Movie.title,
            func.count(BookingSeat.id).label("tickets_sold"),
            func.coalesce(func.sum(Booking.total_price), 0).label("revenue"),
        )
        .select_from(Movie)
        .join(Showtime, Showtime.movie_id == Movie.id)
        .join(Booking, Booking.showtime_id == Showtime.id)
        .join(BookingSeat, BookingSeat.booking_id == Booking.id)
        .where(Booking.status == "CONFIRMED", Booking.created_at >= start, Booking.created_at <= end)
        .group_by(Movie.id, Movie.title)
        .order_by(func.count(BookingSeat.id).desc())
        .limit(limit)
    )
    return [
        {"movie_id": row.id, "title": row.title, "tickets_sold": row.tickets_sold, "revenue": float(row.revenue)}
        for row in result
    ]
