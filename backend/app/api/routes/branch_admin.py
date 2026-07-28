from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.catalog import Auditorium, Branch, Movie, MovieChangeRequest, Seat, Showtime
from app.models.commerce import Booking, BookingSeat, Payment, Promotion
from app.models.user import User
from app.schemas.admin import (
    AuditoriumRead,
    BranchAdminStatsResponse,
    BranchAdminSalesPoint,
    MovieRequestCreate,
    MovieRequestRead,
    SeatAdminRead,
    ShowtimeAdminRead,
)

router = APIRouter()


def _movie_request_read(item: MovieChangeRequest) -> MovieRequestRead:
    return MovieRequestRead(
        id=item.id,
        requested_by_id=item.requested_by_id,
        target_movie_id=item.target_movie_id,
        request_type=item.request_type,
        status=item.status,
        payload=item.payload,
        review_note=item.review_note,
        created_at=item.created_at,
    )


async def _get_staff_branch_id(db: AsyncSession, user_id: UUID) -> UUID:
    """Return the branch_id this branch-admin/staff user is assigned to."""
    result = await db.execute(
        text(
            "SELECT branch_id FROM branch_staff "
            "WHERE user_id = :user_id AND is_active = TRUE "
            "ORDER BY assigned_at DESC LIMIT 1"
        ),
        {"user_id": str(user_id)},
    )
    row = result.first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active branch assignment found for this user",
        )
    return row.branch_id


@router.get("/dashboard")
async def read_branch_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
):
    branch_id = await _get_staff_branch_id(db, current_user.id)

    branch_row = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = branch_row.scalar_one_or_none()
    if branch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")

    auditoriums_count_row = await db.execute(
        select(Auditorium).where(Auditorium.branch_id == branch_id)
    )
    auditoriums_count = len(list(auditoriums_count_row.scalars().all()))

    showtimes_count_row = await db.execute(
        select(Showtime)
        .join(Auditorium, Showtime.auditorium_id == Auditorium.id)
        .where(Auditorium.branch_id == branch_id)
    )
    showtimes_count = len(list(showtimes_count_row.scalars().all()))

    return {
        "branch_id": branch.id,
        "branch_name": branch.name,
        "auditoriums_count": auditoriums_count,
        "showtimes_count": showtimes_count,
    }


@router.get("/stats", response_model=BranchAdminStatsResponse)
async def read_branch_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> BranchAdminStatsResponse:
    branch_id = await _get_staff_branch_id(db, current_user.id)
    branch = await db.get(Branch, branch_id)
    if branch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")

    showtime_result = await db.execute(
        select(Showtime)
        .join(Auditorium, Showtime.auditorium_id == Auditorium.id)
        .options(selectinload(Showtime.movie), selectinload(Showtime.auditorium).selectinload(Auditorium.branch))
        .where(Auditorium.branch_id == branch_id)
        .order_by(Showtime.starts_at.desc())
    )


    showtimes = list(showtime_result.scalars().all())
    showtime_ids = [item.id for item in showtimes]
    tickets_sold = 0
    revenue = 0
    orders = 0
    if showtime_ids:
        tickets_sold = await db.scalar(
            select(func.count(BookingSeat.id))
            .join(Booking, Booking.id == BookingSeat.booking_id)
            .where(Booking.showtime_id.in_(showtime_ids), Booking.status == "CONFIRMED")
        ) or 0
        revenue = await db.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0))
            .join(Booking, Booking.id == Payment.booking_id)
            .where(Booking.showtime_id.in_(showtime_ids), Payment.status == "SUCCESS")
        ) or 0
        orders = await db.scalar(
            select(func.count(Booking.id)).where(
                Booking.showtime_id.in_(showtime_ids),
                Booking.status == "CONFIRMED",
            )
        ) or 0

    promotion_result = await db.execute(
        select(Promotion).where(
            Promotion.is_active.is_(True),
            Promotion.starts_at <= func.now(),
            Promotion.ends_at >= func.now(),
        ).order_by(Promotion.ends_at.asc())
    )
    promotions = list(promotion_result.scalars().all())
    total_capacity = sum(item.auditorium.total_seats for item in showtimes if item.auditorium)

    return BranchAdminStatsResponse(
        branch_id=branch.id,
        branch_name=branch.name,
        ticketsSold=int(tickets_sold),
        activeShowtimes=sum(1 for item in showtimes if item.status == "OPEN"),
        activePromos=len(promotions),
        branchRevenue=int(revenue),
        orders=int(orders),
        seatsSold=int(tickets_sold),
        occupancyRate=round(int(tickets_sold) * 100 / total_capacity, 2) if total_capacity else 0,
        movieCount=len({item.movie_id for item in showtimes}),
        showtimeCount=len(showtimes),
        salesChartData=[BranchAdminSalesPoint(label="Tổng", tickets=int(tickets_sold))],
        showtimesList=[
            {
                "id": item.id,
                "movie_id": item.movie_id,
                "movie_title": item.movie.title if item.movie else "",
                "auditorium_id": item.auditorium_id,
                "auditorium_name": item.auditorium.name if item.auditorium else "",
                "branch_name": branch.name,
                "starts_at": item.starts_at,
                "ends_at": item.ends_at,
                "status": item.status,
                "base_price": float(item.base_price),
            }
            for item in showtimes
        ],
        promotionsList=[
            {
                "code": item.code,
                "discount": int(item.discount_value),
                "desc": item.name,
                "active": item.is_active,
            }
            for item in promotions
        ],
    )


@router.get("/movie-requests", response_model=list[MovieRequestRead])
async def read_my_movie_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> list[MovieRequestRead]:
    result = await db.execute(
        select(MovieChangeRequest)
        .where(MovieChangeRequest.requested_by_id == current_user.id)
        .order_by(MovieChangeRequest.created_at.desc())
    )
    return [_movie_request_read(item) for item in result.scalars().all()]


@router.post("/movie-requests", response_model=MovieRequestRead, status_code=status.HTTP_201_CREATED)
async def create_movie_request(
    payload: MovieRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> MovieRequestRead:
    if payload.request_type in {"UPDATE", "DELETE"}:
        if payload.target_movie_id is None or await db.get(Movie, payload.target_movie_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target movie not found")
    item = MovieChangeRequest(
        requested_by_id=current_user.id,
        target_movie_id=payload.target_movie_id,
        request_type=payload.request_type,
        payload=payload.payload.model_dump(mode="json"),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return _movie_request_read(item)


@router.get("/auditoriums", response_model=list[AuditoriumRead])
async def read_branch_auditoriums(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> list[AuditoriumRead]:
    branch_id = await _get_staff_branch_id(db, current_user.id)

    result = await db.execute(
        select(Auditorium)
        .options(selectinload(Auditorium.branch))
        .where(Auditorium.branch_id == branch_id)
        .order_by(Auditorium.name.asc())
    )
    return [
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
        for item in result.scalars().all()
    ]


@router.get("/seats", response_model=list[SeatAdminRead])
async def read_branch_seats(
    auditorium_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> list[SeatAdminRead]:
    branch_id = await _get_staff_branch_id(db, current_user.id)

    query = (
        select(Seat)
        .join(Auditorium, Seat.auditorium_id == Auditorium.id)
        .options(
            selectinload(Seat.auditorium).selectinload(Auditorium.branch),
            selectinload(Seat.seat_type),
        )
        .where(Auditorium.branch_id == branch_id)
        .order_by(Seat.seat_row.asc(), Seat.seat_number.asc())
    )
    if auditorium_id:
        query = query.where(Seat.auditorium_id == auditorium_id)

    result = await db.execute(query)
    return [
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
        for item in result.scalars().all()
    ]


@router.get("/showtimes", response_model=list[ShowtimeAdminRead])
async def read_branch_showtimes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> list[ShowtimeAdminRead]:
    branch_id = await _get_staff_branch_id(db, current_user.id)

    result = await db.execute(
        select(Showtime)
        .join(Auditorium, Showtime.auditorium_id == Auditorium.id)
        .options(
            selectinload(Showtime.movie),
            selectinload(Showtime.auditorium).selectinload(Auditorium.branch),
        )
        .where(Auditorium.branch_id == branch_id)
        .order_by(Showtime.starts_at.desc())
    )
    return [
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
        for item in result.scalars().all()
    ]
