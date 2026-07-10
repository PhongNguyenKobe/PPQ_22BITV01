from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.movie import get_movie, list_movie_showtimes, list_movies, recommended_movies, search_movies
from app.db.session import get_db
from app.models.catalog import Showtime
from app.schemas.movie import MovieRead, ShowtimeRead

router = APIRouter()


def _movie_to_read(movie) -> MovieRead:
    return MovieRead.model_validate(movie)


def _showtime_to_read(showtime: Showtime) -> ShowtimeRead:
    branch_name = showtime.auditorium.branch.name if showtime.auditorium and showtime.auditorium.branch else ""
    screen_name = showtime.auditorium.name if showtime.auditorium else ""
    return ShowtimeRead(
        id=showtime.id,
        movie_id=showtime.movie_id,
        auditorium_id=showtime.auditorium_id,
        starts_at=showtime.starts_at,
        ends_at=showtime.ends_at,
        status=showtime.status,
        base_price=showtime.base_price,
        branch_name=branch_name,
        screen_name=screen_name,
    )


@router.get("", response_model=list[MovieRead])
async def read_movies(db: AsyncSession = Depends(get_db)) -> list[MovieRead]:
    movies = await list_movies(db)
    return [_movie_to_read(movie) for movie in movies]


@router.get("/recommendations", response_model=list[MovieRead])
async def read_recommendations(db: AsyncSession = Depends(get_db)) -> list[MovieRead]:
    movies = await recommended_movies(db)
    return [_movie_to_read(movie) for movie in movies]


@router.post("/semantic-search", response_model=list[MovieRead])
async def semantic_search(payload: dict, db: AsyncSession = Depends(get_db)) -> list[MovieRead]:
    query_text = str(payload.get("query", "")).strip()
    if not query_text:
        return []
    movies = await search_movies(db, query_text)
    return [_movie_to_read(movie) for movie in movies]


@router.get("/{movie_id}", response_model=MovieRead)
async def read_movie(movie_id: UUID, db: AsyncSession = Depends(get_db)) -> MovieRead:
    movie = await get_movie(db, movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return _movie_to_read(movie)


@router.get("/{movie_id}/showtimes", response_model=list[ShowtimeRead])
async def read_movie_showtimes(movie_id: UUID, db: AsyncSession = Depends(get_db)) -> list[ShowtimeRead]:
    showtimes = await list_movie_showtimes(db, movie_id)
    return [_showtime_to_read(showtime) for showtime in showtimes]
