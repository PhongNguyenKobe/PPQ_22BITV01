from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.catalog import Auditorium, Movie, MovieGenre, Seat, Showtime

async def list_movies(
    db: AsyncSession,
    genre_code: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Movie]:
    query = select(Movie).options(selectinload(Movie.genres)).order_by(Movie.created_at.desc())

    if status:
        query = query.where(Movie.status == status)

    if genre_code:
        query = query.where(Movie.genres.any(MovieGenre.code == genre_code))

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())

async def get_movie(db: AsyncSession, movie_id: UUID) -> Movie | None:
    result = await db.execute(
        select(Movie).options(selectinload(Movie.genres)).where(Movie.id == movie_id)
    )
    return result.scalar_one_or_none()


async def list_movie_showtimes(db: AsyncSession, movie_id: UUID) -> list[Showtime]:
    result = await db.execute(
        select(Showtime)
        .options(selectinload(Showtime.auditorium).selectinload(Auditorium.branch))
        .where(Showtime.movie_id == movie_id)
        .order_by(Showtime.starts_at.asc())
    )
    return list(result.scalars().all())


async def list_showtime_seats(db: AsyncSession, showtime_id: UUID) -> list[Seat]:
    result = await db.execute(
        select(Seat)
        .options(selectinload(Seat.seat_type), selectinload(Seat.auditorium))
        .join(Auditorium, Auditorium.id == Seat.auditorium_id)
        .join(Showtime, Showtime.auditorium_id == Auditorium.id)
        .where(Showtime.id == showtime_id)
        .order_by(Seat.seat_row.asc(), Seat.seat_number.asc())
    )
    return list(result.scalars().all())


async def search_movies(db: AsyncSession, query_text: str) -> list[Movie]:
    like_query = f"%{query_text.strip()}%"
    result = await db.execute(
        select(Movie)
        .options(selectinload(Movie.genres))
        .where(
            Movie.title.ilike(like_query)
            | Movie.original_title.ilike(like_query)
            | Movie.description.ilike(like_query)
        )
        .order_by(Movie.created_at.desc())
    )
    return list(result.scalars().all())


async def recommended_movies(db: AsyncSession, limit: int = 6) -> list[Movie]:
    result = await db.execute(
        select(Movie)
        .options(selectinload(Movie.genres))
        .where(Movie.status.in_(["NOW_SHOWING", "UPCOMING"]))
        .order_by(Movie.status.asc(), Movie.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
