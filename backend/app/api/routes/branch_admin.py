from datetime import datetime, time, timedelta, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.catalog import Auditorium, Branch, Movie, Seat, Showtime
from app.models.commerce import Booking, BookingSeat, Payment, Promotion
from app.models.user import User
from app.schemas.admin import (
    AuditoriumRead,
    BranchAdminStatsResponse,
    BranchAdminSalesPoint,
    BranchAdminTopMovie,
    SeatAdminRead,
    ShowtimeAdminRead,
)

router = APIRouter()


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
async def read_branch_operational_stats(
    period: str = "today",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN")),
) -> BranchAdminStatsResponse:
    if period not in {"today", "7d", "month"}:
        raise HTTPException(status_code=422, detail="Invalid dashboard period")
    branch_id = await _get_staff_branch_id(db, current_user.id)
    branch = await db.get(Branch, branch_id)
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")

    vn_tz = ZoneInfo("Asia/Ho_Chi_Minh")
    now = datetime.now(timezone.utc)
    today = now.astimezone(vn_tz).date()
    start_date = today - timedelta(days=6) if period == "7d" else today.replace(day=1) if period == "month" else today
    start_at = datetime.combine(start_date, time.min, tzinfo=vn_tz).astimezone(timezone.utc)
    end_at = datetime.combine(today + timedelta(days=1), time.min, tzinfo=vn_tz).astimezone(timezone.utc)

    result = await db.execute(
        select(Showtime)
        .join(Auditorium, Showtime.auditorium_id == Auditorium.id)
        .options(selectinload(Showtime.movie), selectinload(Showtime.auditorium))
        .where(Auditorium.branch_id == branch_id, Showtime.starts_at >= start_at, Showtime.starts_at < end_at)
        .order_by(Showtime.starts_at.asc())
    )
    showtimes = list(result.scalars().all())
    ids = [item.id for item in showtimes]
    valid = [item for item in showtimes if item.status != "CANCELLED"]
    sold_by_showtime: dict[UUID, int] = {}
    revenue_by_showtime: dict[UUID, int] = {}
    orders = pending = refunds = 0
    top_movies: list[BranchAdminTopMovie] = []
    if ids:
        sold_rows = await db.execute(
            select(Booking.showtime_id, func.count(BookingSeat.id)).join(Booking, Booking.id == BookingSeat.booking_id)
            .where(Booking.showtime_id.in_(ids), Booking.status == "CONFIRMED").group_by(Booking.showtime_id)
        )
        sold_by_showtime = {row[0]: int(row[1] or 0) for row in sold_rows.all()}
        revenue_rows = await db.execute(
            select(Booking.showtime_id, func.coalesce(func.sum(Payment.amount), 0)).join(Booking, Booking.id == Payment.booking_id)
            .where(Booking.showtime_id.in_(ids), Payment.status == "SUCCESS").group_by(Booking.showtime_id)
        )
        revenue_by_showtime = {row[0]: int(row[1] or 0) for row in revenue_rows.all()}
        orders = int(await db.scalar(select(func.count(Booking.id)).where(Booking.showtime_id.in_(ids), Booking.status == "CONFIRMED")) or 0)
        pending = int(await db.scalar(select(func.count(Payment.id)).join(Booking, Booking.id == Payment.booking_id).where(Booking.showtime_id.in_(ids), Payment.status == "PENDING")) or 0)
        refunds = int(await db.scalar(select(func.count(Payment.id)).join(Booking, Booking.id == Payment.booking_id).where(Booking.showtime_id.in_(ids), Payment.status == "REFUND_PENDING")) or 0)
        ticket_rows = await db.execute(
            select(Movie.id, Movie.title, Movie.poster_url, func.count(BookingSeat.id))
            .join(Showtime, Showtime.movie_id == Movie.id).join(Booking, Booking.showtime_id == Showtime.id).join(BookingSeat, BookingSeat.booking_id == Booking.id)
            .where(Showtime.id.in_(ids), Booking.status == "CONFIRMED").group_by(Movie.id, Movie.title, Movie.poster_url)
        )
        movie_revenue_rows = await db.execute(
            select(Movie.id, func.coalesce(func.sum(Payment.amount), 0)).join(Showtime, Showtime.movie_id == Movie.id)
            .join(Booking, Booking.showtime_id == Showtime.id).join(Payment, Payment.booking_id == Booking.id)
            .where(Showtime.id.in_(ids), Payment.status == "SUCCESS").group_by(Movie.id)
        )
        movie_revenue = {row[0]: int(row[1] or 0) for row in movie_revenue_rows.all()}
        ranked = sorted(ticket_rows.all(), key=lambda row: (movie_revenue.get(row[0], 0), int(row[3] or 0)), reverse=True)[:3]
        top_movies = [BranchAdminTopMovie(movie_id=row[0], title=row[1], poster_url=row[2], tickets_sold=int(row[3] or 0), revenue=movie_revenue.get(row[0], 0)) for row in ranked]

    tickets = sum(sold_by_showtime.values())
    revenue = sum(revenue_by_showtime.values())
    capacity = sum(item.auditorium.total_seats for item in valid if item.auditorium)
    today_items = [item for item in showtimes if item.starts_at.astimezone(vn_tz).date() == today]
    showing = sum(1 for item in today_items if item.status == "OPEN" and item.starts_at <= now < item.ends_at)
    upcoming = sum(1 for item in today_items if item.status == "OPEN" and item.starts_at > now)
    cancelled = sum(1 for item in showtimes if item.status == "CANCELLED")
    drafts = sum(1 for item in today_items if item.status == "DRAFT" and item.starts_at > now)
    points: list[BranchAdminSalesPoint] = []
    cursor = start_date
    while cursor <= today:
        daily = [item for item in showtimes if item.starts_at.astimezone(vn_tz).date() == cursor]
        points.append(BranchAdminSalesPoint(label=cursor.isoformat(), tickets=sum(sold_by_showtime.get(item.id, 0) for item in daily), revenue=sum(revenue_by_showtime.get(item.id, 0) for item in daily)))
        cursor += timedelta(days=1)

    return BranchAdminStatsResponse(
        branch_id=branch.id, branch_name=branch.name, ticketsSold=tickets, activeShowtimes=showing + upcoming,
        activePromos=0, branchRevenue=revenue, orders=orders, seatsSold=tickets,
        occupancyRate=round(tickets * 100 / capacity, 2) if capacity else 0,
        movieCount=len({item.movie_id for item in valid}), showtimeCount=len(valid), todayShowtimes=len(today_items),
        showingNow=showing, upcomingToday=upcoming, attentionCount=cancelled + drafts + pending + refunds,
        pendingPayments=pending, refundPending=refunds, period=period, generatedAt=now,
        salesChartData=points, topMovies=top_movies,
        showtimesList=[{"id": item.id, "movie_id": item.movie_id, "movie_title": item.movie.title if item.movie else "", "auditorium_id": item.auditorium_id, "auditorium_name": item.auditorium.name if item.auditorium else "", "branch_name": branch.name, "starts_at": item.starts_at, "ends_at": item.ends_at, "status": item.status, "base_price": float(item.base_price)} for item in today_items],
        promotionsList=[],
    )


@router.get("/stats-legacy", response_model=BranchAdminStatsResponse, include_in_schema=False)
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
