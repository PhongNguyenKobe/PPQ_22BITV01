from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, func, select, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.catalog import Movie
from app.models.commerce import Payment
from app.models.user import Role, User, user_roles_table
from app.schemas.admin import BranchRead, RevenueDataPoint, UserRoleUpdate


async def _ensure_branch_staff_table(db: AsyncSession) -> None:
    await db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS branch_staff (
                branch_id UUID NOT NULL,
                user_id UUID NOT NULL,
                staff_role VARCHAR(30) NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                PRIMARY KEY (branch_id, user_id)
            )
            """
        )
    )
    await db.commit()


async def list_users_with_branch_id(db: AsyncSession) -> list[tuple[User, UUID | None]]:
    users_result = await db.execute(select(User).options(selectinload(User.roles)).order_by(User.created_at.desc()))
    users = list(users_result.scalars().all())

    try:
        branch_rows = await db.execute(text("SELECT user_id, branch_id FROM branch_staff WHERE is_active = TRUE"))
        branch_map = {row.user_id: row.branch_id for row in branch_rows}
    except ProgrammingError:
        await db.rollback()
        await _ensure_branch_staff_table(db)
        branch_map = {}

    return [(user, branch_map.get(user.id)) for user in users]


async def list_branches(db: AsyncSession) -> list[BranchRead]:
    result = await db.execute(text("SELECT id, code, name, city FROM branches ORDER BY name ASC"))
    return [BranchRead(id=row.id, code=row.code, name=row.name, city=row.city) for row in result]


async def get_admin_stats(db: AsyncSession) -> dict:
    # Count branches
    branch_result = await db.execute(text("SELECT COUNT(*) FROM branches"))
    total_branches = branch_result.scalar() or 0

    # Count movies
    movie_result = await db.execute(select(Movie))
    total_movies = len(movie_result.scalars().all())

    # Count users (exclude admins)
    user_result = await db.execute(select(User))
    all_users = user_result.scalars().all()
    total_users = len([u for u in all_users if not any(r.code == "SUPER_ADMIN" for r in u.roles)])

    # Dummy revenue data since we don't have orders/tickets yet
    total_revenue = 0
    revenue_chart_data = [
        RevenueDataPoint(label=label, value=value)
        for label, value in [
            ("T12", 45000000), ("T01", 68000000), ("T02", 92000000),
            ("T03", 75000000), ("T04", 55000000), ("T05", 89000000),
            ("T06 (Dự kiến)", 120000000)
        ]
    ]

    return {
        "totalBranches": total_branches,
        "totalMovies": total_movies,
        "totalUsers": total_users,
        "totalRevenue": total_revenue,
        "revenueChartData": revenue_chart_data,
    }


async def get_live_admin_stats(db: AsyncSession, branch_id: UUID | None = None, period: str = "7d") -> dict:
    params = {"branch_id": branch_id}
    branch_filter = "AND a.branch_id = :branch_id" if branch_id else ""
    branch_where = "WHERE br.id = :branch_id" if branch_id else ""

    scope_row = (
        await db.execute(
            text(
                "SELECT name, is_active FROM branches WHERE id = :branch_id"
                if branch_id else
                "SELECT 'Toàn hệ thống' AS name, TRUE AS is_active"
            ),
            params,
        )
    ).first()
    if scope_row is None:
        raise ValueError("BRANCH_NOT_FOUND")

    total_branches = (await db.execute(text(
        "SELECT COUNT(*) FROM branches WHERE id = :branch_id" if branch_id else "SELECT COUNT(*) FROM branches"
    ), params)).scalar() or 0
    active_branches = (await db.execute(text(
        "SELECT COUNT(*) FROM branches WHERE id = :branch_id AND is_active = TRUE"
        if branch_id else "SELECT COUNT(*) FROM branches WHERE is_active = TRUE"
    ), params)).scalar() or 0
    total_auditoriums = (await db.execute(text(
        "SELECT COUNT(*) FROM auditoriums WHERE branch_id = :branch_id"
        if branch_id else "SELECT COUNT(*) FROM auditoriums"
    ), params)).scalar() or 0
    total_movies = (await db.execute(text(f"""
        SELECT COUNT(DISTINCT m.id)
        FROM movies m
        {"JOIN showtimes s ON s.movie_id = m.id JOIN auditoriums a ON a.id = s.auditorium_id WHERE a.branch_id = :branch_id" if branch_id else ""}
    """), params)).scalar() or 0
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_revenue = (
        await db.execute(text(f"""
            SELECT COALESCE(SUM(p.amount), 0)
            FROM payments p
            JOIN bookings b ON b.id = p.booking_id
            JOIN showtimes s ON s.id = b.showtime_id
            JOIN auditoriums a ON a.id = s.auditorium_id
            WHERE p.status = 'SUCCESS' {branch_filter}
        """), params)
    ).scalar() or 0
    refunded_revenue = (await db.execute(text(f"""
        SELECT COALESCE(SUM(p.amount), 0)
        FROM payments p
        JOIN bookings b ON b.id = p.booking_id
        JOIN showtimes s ON s.id = b.showtime_id
        JOIN auditoriums a ON a.id = s.auditorium_id
        WHERE p.status = 'REFUNDED' {branch_filter}
    """), params)).scalar() or 0
    today_revenue = (
        await db.execute(
            text(
                f"""
                SELECT COALESCE(SUM(p.amount), 0)
                FROM payments p
                JOIN bookings b ON b.id = p.booking_id
                JOIN showtimes s ON s.id = b.showtime_id
                JOIN auditoriums a ON a.id = s.auditorium_id
                WHERE p.status = 'SUCCESS'
                  {branch_filter}
                  AND (COALESCE(p.paid_at, p.created_at) AT TIME ZONE 'Asia/Ho_Chi_Minh')::date
                      = (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::date
                """
            ), params
        )
    ).scalar() or 0
    month_revenue = (
        await db.execute(
            text(
                f"""
                SELECT COALESCE(SUM(p.amount), 0)
                FROM payments p
                JOIN bookings b ON b.id = p.booking_id
                JOIN showtimes s ON s.id = b.showtime_id
                JOIN auditoriums a ON a.id = s.auditorium_id
                WHERE p.status = 'SUCCESS'
                  {branch_filter}
                  AND date_trunc('month', COALESCE(p.paid_at, p.created_at) AT TIME ZONE 'Asia/Ho_Chi_Minh')
                      = date_trunc('month', now() AT TIME ZONE 'Asia/Ho_Chi_Minh')
                """
            ), params
        )
    ).scalar() or 0
    booking_counts = {
        row.status: int(row.count)
        for row in (
            await db.execute(text(f"""
                SELECT b.status, COUNT(*) AS count
                FROM bookings b
                JOIN showtimes s ON s.id = b.showtime_id
                JOIN auditoriums a ON a.id = s.auditorium_id
                WHERE TRUE {branch_filter}
                GROUP BY b.status
            """), params)
        ).all()
    }
    tickets_sold = (
        await db.execute(
            text(
                f"""
                SELECT COUNT(bs.id)
                FROM booking_seats bs
                JOIN bookings b ON b.id = bs.booking_id
                JOIN showtimes s ON s.id = b.showtime_id
                JOIN auditoriums a ON a.id = s.auditorium_id
                WHERE b.status = 'CONFIRMED'
                  {branch_filter}
                  AND EXISTS (
                    SELECT 1 FROM payments p
                    WHERE p.booking_id = b.id AND p.status = 'SUCCESS'
                  )
                """
            ), params
        )
    ).scalar() or 0
    if period == "today":
        revenue_query = f"""
            WITH hours AS (
                SELECT generate_series(
                    date_trunc('day', now() AT TIME ZONE 'Asia/Ho_Chi_Minh'),
                    date_trunc('day', now() AT TIME ZONE 'Asia/Ho_Chi_Minh') + interval '23 hours',
                    interval '1 hour'
                ) AS hour
            ), payment_facts AS (
                SELECT p.amount, COALESCE(p.paid_at, p.created_at) AS paid_time
                FROM payments p
                JOIN bookings b ON b.id = p.booking_id
                JOIN showtimes s ON s.id = b.showtime_id
                JOIN auditoriums a ON a.id = s.auditorium_id
                WHERE p.status = 'SUCCESS' {branch_filter}
            )
            SELECT to_char(hours.hour, 'HH24') || 'h' AS label, COALESCE(SUM(p.amount), 0) AS value
            FROM hours
            LEFT JOIN payment_facts p
              ON date_trunc('hour', p.paid_time AT TIME ZONE 'Asia/Ho_Chi_Minh') = hours.hour
            GROUP BY hours.hour
            ORDER BY hours.hour
        """
    elif period in ("month", "30d"):
        revenue_query = f"""
            WITH days AS (
                SELECT generate_series(
                    (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::date - 29,
                    (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::date,
                    interval '1 day'
                )::date AS day
            ), payment_facts AS (
                SELECT p.amount, COALESCE(p.paid_at, p.created_at) AS paid_time
                FROM payments p
                JOIN bookings b ON b.id = p.booking_id
                JOIN showtimes s ON s.id = b.showtime_id
                JOIN auditoriums a ON a.id = s.auditorium_id
                WHERE p.status = 'SUCCESS' {branch_filter}
            )
            SELECT to_char(days.day, 'DD/MM') AS label, COALESCE(SUM(p.amount), 0) AS value
            FROM days
            LEFT JOIN payment_facts p
              ON (p.paid_time AT TIME ZONE 'Asia/Ho_Chi_Minh')::date = days.day
            GROUP BY days.day
            ORDER BY days.day
        """
    else:
        revenue_query = f"""
            WITH days AS (
                SELECT generate_series(
                    (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::date - 6,
                    (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::date,
                    interval '1 day'
                )::date AS day
            ), payment_facts AS (
                SELECT p.amount, COALESCE(p.paid_at, p.created_at) AS paid_time
                FROM payments p
                JOIN bookings b ON b.id = p.booking_id
                JOIN showtimes s ON s.id = b.showtime_id
                JOIN auditoriums a ON a.id = s.auditorium_id
                WHERE p.status = 'SUCCESS' {branch_filter}
            )
            SELECT to_char(days.day, 'DD/MM') AS label, COALESCE(SUM(p.amount), 0) AS value
            FROM days
            LEFT JOIN payment_facts p
              ON (p.paid_time AT TIME ZONE 'Asia/Ho_Chi_Minh')::date = days.day
            GROUP BY days.day
            ORDER BY days.day
        """
    
    revenue_rows = (await db.execute(text(revenue_query), params)).all()
    branch_rows = (
        await db.execute(
            text(
                f"""
                WITH booking_facts AS (
                    SELECT bo.id, bo.showtime_id, bo.status,
                           (SELECT COUNT(*) FROM booking_seats x WHERE x.booking_id = bo.id) AS seats,
                           COALESCE((
                               SELECT SUM(p.amount) FROM payments p
                               WHERE p.booking_id = bo.id AND p.status = 'SUCCESS'
                           ), 0) AS revenue
                    FROM bookings bo
                )
                SELECT br.name AS label,
                       COALESCE(SUM(bf.revenue), 0) AS revenue,
                       COALESCE(SUM(bf.seats) FILTER (WHERE bf.status = 'CONFIRMED'), 0) AS tickets
                FROM branches br
                LEFT JOIN auditoriums a ON a.branch_id = br.id
                LEFT JOIN showtimes s ON s.auditorium_id = a.id
                LEFT JOIN booking_facts bf ON bf.showtime_id = s.id
                {branch_where}
                GROUP BY br.id, br.name
                ORDER BY revenue DESC, br.name
                """
            ), params
        )
    ).all()
    movie_rows = (
        await db.execute(
            text(
                f"""
                SELECT m.title AS label,
                       m.poster_url AS poster_url,
                       COALESCE(SUM(t.unit_price), 0) AS revenue,
                       COUNT(t.id) AS tickets
                FROM movies m
                JOIN showtimes s ON s.movie_id = m.id
                JOIN auditoriums a ON a.id = s.auditorium_id
                JOIN bookings b ON b.showtime_id = s.id AND b.status = 'CONFIRMED'
                JOIN payments p ON p.booking_id = b.id AND p.status = 'SUCCESS'
                JOIN tickets t ON t.booking_id = b.id AND t.status IN ('ISSUED', 'USED')
                WHERE TRUE {branch_filter}
                GROUP BY m.id, m.title, m.poster_url
                ORDER BY revenue DESC, tickets DESC
                LIMIT 5
                """
            ), params
        )
    ).all()
    occupancy_row = (await db.execute(text(f"""
        WITH scoped_showtimes AS (
            SELECT s.id, a.total_seats
            FROM showtimes s
            JOIN auditoriums a ON a.id = s.auditorium_id
        WHERE s.starts_at >= date_trunc('month', now() AT TIME ZONE 'Asia/Ho_Chi_Minh') AT TIME ZONE 'Asia/Ho_Chi_Minh'
          AND s.starts_at < (date_trunc('month', now() AT TIME ZONE 'Asia/Ho_Chi_Minh') + interval '1 month') AT TIME ZONE 'Asia/Ho_Chi_Minh'
          {branch_filter}
        ), sold AS (
            SELECT COUNT(t.id) AS count
            FROM scoped_showtimes ss
            JOIN bookings b ON b.showtime_id = ss.id AND b.status = 'CONFIRMED'
            JOIN tickets t ON t.booking_id = b.id AND t.status IN ('ISSUED', 'USED')
        )
        SELECT (SELECT count FROM sold) AS sold,
               COALESCE((SELECT SUM(total_seats) FROM scoped_showtimes), 0) AS offered
    """), params)).first()
    occupancy_rate = round((occupancy_row.sold * 100 / occupancy_row.offered), 1) if occupancy_row and occupancy_row.offered else 0
    return {
        "scopeName": scope_row.name,
        "totalBranches": total_branches,
        "activeBranches": active_branches,
        "totalAuditoriums": total_auditoriums,
        "totalMovies": total_movies,
        "totalUsers": total_users,
        "totalRevenue": int(total_revenue),
        "refundedRevenue": int(refunded_revenue),
        "todayRevenue": int(today_revenue),
        "monthRevenue": int(month_revenue),
        "ticketsSold": int(tickets_sold),
        "successfulBookings": booking_counts.get("CONFIRMED", 0),
        "cancelledBookings": booking_counts.get("CANCELLED", 0),
        "pendingBookings": booking_counts.get("PENDING", 0),
        "expiredBookings": booking_counts.get("EXPIRED", 0),
        "occupancyRate": occupancy_rate,
        "generatedAt": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        "revenueChartData": [{"label": row.label, "value": int(row.value)} for row in revenue_rows],
        "branchPerformance": [
            {"label": row.label, "revenue": int(row.revenue), "tickets": int(row.tickets)}
            for row in branch_rows
        ],
        "topMovies": [
            {"label": row.label, "revenue": int(row.revenue), "tickets": int(row.tickets), "poster_url": row.poster_url}
            for row in movie_rows
        ],
    }


async def set_user_role(db: AsyncSession, user: User, payload: UserRoleUpdate) -> User:
    role_result = await db.execute(select(Role).where(Role.code == payload.role_code))
    role = role_result.scalar_one_or_none()
    if role is None:
        raise ValueError("ROLE_NOT_FOUND")

    await db.execute(delete(user_roles_table).where(user_roles_table.c.user_id == user.id))
    await db.execute(user_roles_table.insert().values(user_id=user.id, role_id=role.id))

    await _ensure_branch_staff_table(db)

    # A branch administrator may only have one active assignment. Clear the
    # previous assignment before applying the new role/branch atomically.
    await db.execute(text("DELETE FROM branch_staff WHERE user_id = :user_id"), {"user_id": str(user.id)})

    if payload.role_code == "BRANCH_ADMIN":
        if payload.branch_id is None:
            raise ValueError("BRANCH_REQUIRED")
        await db.execute(
            text(
                """
                INSERT INTO branch_staff (branch_id, user_id, staff_role, is_active)
                VALUES (:branch_id, :user_id, :staff_role, TRUE)
                ON CONFLICT (branch_id, user_id)
                DO UPDATE SET staff_role = EXCLUDED.staff_role, is_active = EXCLUDED.is_active
                """
            ),
            {
                "branch_id": str(payload.branch_id),
                "user_id": str(user.id),
                "staff_role": payload.role_code,
            },
        )
    db.add(user)
    await db.commit()

    refreshed = await db.execute(select(User).options(selectinload(User.roles)).where(User.id == user.id))
    updated_user = refreshed.scalar_one_or_none()
    if updated_user is None:
        raise RuntimeError("User role update failed")
    return updated_user
