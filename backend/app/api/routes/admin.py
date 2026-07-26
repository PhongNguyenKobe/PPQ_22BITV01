from datetime import date
from uuid import UUID
<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status, Query
=======
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import IntegrityError
>>>>>>> f220d3b (SS12)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

<<<<<<< HEAD
from app.api.deps import get_current_user
from app.core.permissions import require_admin, require_branch_admin
from app.db.session import get_db
from app.schemas.movie import MovieRead
from app.schemas.admin import AdminStatsResponse, BranchRead, UserRoleUpdate, AdminUserRead
from app.models.user import User

router = APIRouter()

@router.get("/stats", response_model=AdminStatsResponse, dependencies=[Depends(require_admin)])
async def get_admin_stats(
=======
from app.api.deps import require_roles
from app.crud.admin import get_admin_stats, list_branches, list_users_with_branch_id, set_user_role
from app.crud.user import create_user, get_user_by_id, update_user
from app.db.session import get_db
from app.models.catalog import Auditorium, Branch, Movie, Seat, SeatType, Showtime, Vendor
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
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter()


async def _branch_id_map(db: AsyncSession) -> dict[UUID, UUID]:
    rows = await db.execute(text("SELECT user_id, branch_id FROM branch_staff WHERE is_active = TRUE"))
    return {row.user_id: row.branch_id for row in rows}


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
>>>>>>> f220d3b (SS12)
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AdminStatsResponse:
    return AdminStatsResponse(
        totalBranches=5,
        totalMovies=12,
        totalUsers=1250,
        totalRevenue=125000000,
        revenueChartData=[]
    )

@router.get("/users", dependencies=[Depends(require_admin)])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {"total": 0, "users": []}

<<<<<<< HEAD
@router.put("/users/{user_id}/role", response_model=AdminUserRead, dependencies=[Depends(require_admin)])
async def update_user_role(
=======

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


@router.patch("/users/{user_id}/role", response_model=AdminUserRead)
async def update_admin_user_role(
>>>>>>> f220d3b (SS12)
    user_id: UUID,
    payload: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AdminUserRead:
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

<<<<<<< HEAD
@router.post("/movies", response_model=MovieRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_movie(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MovieRead:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid movie data")

@router.put("/movies/{movie_id}", response_model=MovieRead, dependencies=[Depends(require_admin)])
async def update_movie(
    movie_id: UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MovieRead:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_movie(
    movie_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.post("/showtimes", dependencies=[Depends(require_branch_admin)])
async def create_showtime(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.put("/showtimes/{showtime_id}", dependencies=[Depends(require_branch_admin)])
async def update_showtime(
    showtime_id: UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.delete("/showtimes/{showtime_id}", dependencies=[Depends(require_branch_admin)])
async def delete_showtime(
    showtime_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.get("/branches", dependencies=[Depends(require_admin)])
async def list_branches(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return []

@router.post("/branches", dependencies=[Depends(require_admin)])
async def create_branch(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.put("/branches/{branch_id}", dependencies=[Depends(require_admin)])
async def update_branch(
    branch_id: UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.delete("/branches/{branch_id}", dependencies=[Depends(require_admin)])
async def delete_branch(
    branch_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.get("/bookings", dependencies=[Depends(require_branch_admin)])
async def list_branch_bookings(
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {"total": 0, "bookings": []}

@router.put("/bookings/{booking_id}/cancel", dependencies=[Depends(require_branch_admin)])
async def cancel_booking(
    booking_id: UUID,
    reason: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.get("/payments", dependencies=[Depends(require_admin)])
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {"total": 0, "payments": []}

@router.post("/payments/{payment_id}/refund", dependencies=[Depends(require_admin)])
async def refund_payment(
    payment_id: UUID,
    reason: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass

@router.get("/reports/revenue", dependencies=[Depends(require_admin)])
async def get_revenue_report(
    start_date: str,
    end_date: str,
    group_by: str = Query("day", pattern="day|week|month"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {}

@router.get("/reports/occupancy", dependencies=[Depends(require_admin)])
async def get_occupancy_report(
    start_date: str,
    end_date: str,
    branch_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {}

@router.get("/reports/top-movies", dependencies=[Depends(require_admin)])
async def get_top_movies(
    start_date: str,
    end_date: str,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return []
=======
    branch_rows = await list_users_with_branch_id(db)
    branch_id = next((item_branch for item_user, item_branch in branch_rows if item_user.id == updated_user.id), None)
    return AdminUserRead.model_validate(updated_user).model_copy(update={"branch_id": branch_id})


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
    query = (
        select(Seat)
        .options(selectinload(Seat.auditorium).selectinload(Auditorium.branch), selectinload(Seat.seat_type))
        .order_by(Seat.seat_row.asc(), Seat.seat_number.asc())
    )
    if auditorium_id:
        query = query.where(Seat.auditorium_id == auditorium_id)

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
    row = await db.execute(select(Seat).where(Seat.id == seat_id))
    seat = row.scalar_one_or_none()
    if seat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found")

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

    updates = payload.model_dump(exclude_unset=True)
    new_starts_at = updates.get("starts_at", showtime.starts_at)
    new_ends_at = updates.get("ends_at", showtime.ends_at)
    if new_ends_at <= new_starts_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ends_at must be after starts_at")

    if "auditorium_id" in updates and updates["auditorium_id"] is not None:
        auditorium_row = await db.execute(select(Auditorium).where(Auditorium.id == updates["auditorium_id"]))
        if auditorium_row.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auditorium not found")

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
    row = await db.execute(select(Showtime).where(Showtime.id == showtime_id))
    showtime = row.scalar_one_or_none()
    if showtime is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Showtime not found")

    await db.delete(showtime)
    await db.commit()
>>>>>>> f220d3b (SS12)
