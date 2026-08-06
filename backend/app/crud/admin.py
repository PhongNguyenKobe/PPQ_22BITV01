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


async def get_live_admin_stats(db: AsyncSession) -> dict:
    total_branches = (await db.execute(text("SELECT COUNT(*) FROM branches"))).scalar() or 0
    total_movies = (await db.execute(select(func.count(Movie.id)))).scalar() or 0
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_revenue = (
        await db.execute(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == "SUCCESS"))
    ).scalar() or 0
    today_revenue = (
        await db.execute(
            text(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM payments
                WHERE status = 'SUCCESS'
                  AND (COALESCE(paid_at, created_at) AT TIME ZONE 'Asia/Ho_Chi_Minh')::date
                      = (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::date
                """
            )
        )
    ).scalar() or 0
    month_revenue = (
        await db.execute(
            text(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM payments
                WHERE status = 'SUCCESS'
                  AND date_trunc('month', COALESCE(paid_at, created_at) AT TIME ZONE 'Asia/Ho_Chi_Minh')
                      = date_trunc('month', now() AT TIME ZONE 'Asia/Ho_Chi_Minh')
                """
            )
        )
    ).scalar() or 0
    booking_counts = {
        row.status: int(row.count)
        for row in (
            await db.execute(text("SELECT status, COUNT(*) AS count FROM bookings GROUP BY status"))
        ).all()
    }
    tickets_sold = (
        await db.execute(
            text(
                """
                SELECT COUNT(bs.id)
                FROM booking_seats bs
                JOIN bookings b ON b.id = bs.booking_id
                WHERE b.status = 'CONFIRMED'
                  AND EXISTS (
                    SELECT 1 FROM payments p
                    WHERE p.booking_id = b.id AND p.status = 'SUCCESS'
                  )
                """
            )
        )
    ).scalar() or 0
    revenue_rows = (
        await db.execute(
            text(
                """
                WITH days AS (
                    SELECT generate_series(
                        (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::date - 6,
                        (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::date,
                        interval '1 day'
                    )::date AS day
                )
                SELECT to_char(days.day, 'DD/MM') AS label, COALESCE(SUM(p.amount), 0) AS value
                FROM days
                LEFT JOIN payments p
                  ON (COALESCE(p.paid_at, p.created_at) AT TIME ZONE 'Asia/Ho_Chi_Minh')::date = days.day
                 AND p.status = 'SUCCESS'
                GROUP BY days.day
                ORDER BY days.day
                """
            )
        )
    ).all()
    branch_rows = (
        await db.execute(
            text(
                """
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
                GROUP BY br.id, br.name
                ORDER BY revenue DESC, br.name
                """
            )
        )
    ).all()
    movie_rows = (
        await db.execute(
            text(
                """
                WITH booking_facts AS (
                    SELECT b.id, b.showtime_id, b.status,
                           (SELECT COUNT(*) FROM booking_seats x WHERE x.booking_id = b.id) AS seats,
                           COALESCE((
                               SELECT SUM(p.amount) FROM payments p
                               WHERE p.booking_id = b.id AND p.status = 'SUCCESS'
                           ), 0) AS revenue
                    FROM bookings b
                )
                SELECT m.title AS label,
                       m.poster_url AS poster_url,
                       COALESCE(SUM(bf.revenue), 0) AS revenue,
                       COALESCE(SUM(bf.seats) FILTER (WHERE bf.status = 'CONFIRMED'), 0) AS tickets
                FROM movies m
                JOIN showtimes s ON s.movie_id = m.id
                JOIN booking_facts bf ON bf.showtime_id = s.id
                GROUP BY m.id, m.title, m.poster_url
                ORDER BY revenue DESC, tickets DESC
                LIMIT 5
                """
            )
        )
    ).all()
    return {
        "totalBranches": total_branches,
        "totalMovies": total_movies,
        "totalUsers": total_users,
        "totalRevenue": int(total_revenue),
        "todayRevenue": int(today_revenue),
        "monthRevenue": int(month_revenue),
        "ticketsSold": int(tickets_sold),
        "successfulBookings": booking_counts.get("CONFIRMED", 0),
        "cancelledBookings": booking_counts.get("CANCELLED", 0),
        "pendingBookings": booking_counts.get("PENDING", 0),
        "revenueChartData": [{"label": row.label, "value": int(row.value)} for row in revenue_rows],
        "branchPerformance": [
            {"label": row.label, "revenue": int(row.revenue), "tickets": int(row.tickets)}
            for row in branch_rows
        ],
        "topMovies": [
            {"label": row.label, "poster_url": row.poster_url, "revenue": int(row.revenue), "tickets": int(row.tickets)}
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

    if payload.role_code in {"BRANCH_ADMIN", "STAFF"}:
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
    else:
        await db.execute(text("DELETE FROM branch_staff WHERE user_id = :user_id"), {"user_id": str(user.id)})

    db.add(user)
    await db.commit()

    refreshed = await db.execute(select(User).options(selectinload(User.roles)).where(User.id == user.id))
    updated_user = refreshed.scalar_one_or_none()
    if updated_user is None:
        raise RuntimeError("User role update failed")
    return updated_user
