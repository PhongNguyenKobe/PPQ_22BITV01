from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.crud.movie import get_movie, list_movie_showtimes, list_movies, recommended_movies, search_movies
from app.db.session import get_db
from app.models.catalog import Showtime
from app.models.commerce import Booking
from app.models.review import MovieReview
from app.models.user import User
from app.schemas.movie import MovieRead, ShowtimeRead
from app.schemas.review import MovieReviewRead, MovieReviewsResponse, MovieReviewSummary, MovieReviewWrite

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
        booking_closes_at=showtime.booking_closes_at,
        base_price=showtime.base_price,
        branch_name=branch_name,
        screen_name=screen_name,
    )


@router.get("", response_model=list[MovieRead])
async def read_movies(
    genre: str | None = None,
    status: str | None = None,
    public_only: bool = False,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> list[MovieRead]:
    movies = await list_movies(
        db,
        genre_code=genre,
        status=status,
        public_only=public_only,
        skip=skip,
        limit=limit,
    )
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


async def _verified_review_users(db: AsyncSession, movie_id: UUID, user_ids: list[UUID]) -> set[UUID]:
    if not user_ids:
        return set()
    result = await db.execute(
        select(Booking.user_id)
        .join(Showtime, Showtime.id == Booking.showtime_id)
        .where(
            Showtime.movie_id == movie_id,
            Booking.user_id.in_(user_ids),
            Booking.status == "CONFIRMED",
        )
        .distinct()
    )
    return set(result.scalars().all())


@router.get("/{movie_id}/reviews", response_model=MovieReviewsResponse)
async def read_movie_reviews(
    movie_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> MovieReviewsResponse:
    if await get_movie(db, movie_id) is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    result = await db.execute(
        select(MovieReview)
        .options(selectinload(MovieReview.user))
        .where(MovieReview.movie_id == movie_id, MovieReview.is_visible.is_(True))
        .order_by(MovieReview.updated_at.desc())
        .limit(limit)
    )
    reviews = list(result.scalars().all())
    verified_users = await _verified_review_users(db, movie_id, [review.user_id for review in reviews])
    counts_result = await db.execute(
        select(MovieReview.rating, func.count(MovieReview.id))
        .where(MovieReview.movie_id == movie_id, MovieReview.is_visible.is_(True))
        .group_by(MovieReview.rating)
    )
    distribution = {score: 0 for score in range(1, 6)}
    for score, count in counts_result.all():
        distribution[int(score)] = int(count)
    total = sum(distribution.values())
    average = round(sum(score * count for score, count in distribution.items()) / total, 1) if total else 0.0

    return MovieReviewsResponse(
        summary=MovieReviewSummary(total=total, average=average, distribution=distribution),
        reviews=[
            MovieReviewRead(
                id=review.id,
                user_id=review.user_id,
                user_name=review.user.full_name,
                rating=review.rating,
                content=review.content,
                verified_purchase=review.user_id in verified_users,
                created_at=review.created_at,
                updated_at=review.updated_at,
            )
            for review in reviews
        ],
    )


@router.post("/{movie_id}/reviews", response_model=MovieReviewRead, status_code=status.HTTP_201_CREATED)
async def create_movie_review(
    movie_id: UUID,
    payload: MovieReviewWrite,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MovieReviewRead:
    if await get_movie(db, movie_id) is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    review = MovieReview(movie_id=movie_id, user_id=current_user.id, rating=payload.rating, content=payload.content)
    db.add(review)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Bạn đã đánh giá phim này; hãy chỉnh sửa đánh giá hiện có") from None
    await db.refresh(review)
    verified = bool(await _verified_review_users(db, movie_id, [current_user.id]))
    return MovieReviewRead(id=review.id, user_id=current_user.id, user_name=current_user.full_name, rating=review.rating, content=review.content, verified_purchase=verified, created_at=review.created_at, updated_at=review.updated_at)


@router.patch("/{movie_id}/reviews/{review_id}", response_model=MovieReviewRead)
async def update_movie_review(
    movie_id: UUID,
    review_id: UUID,
    payload: MovieReviewWrite,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MovieReviewRead:
    result = await db.execute(select(MovieReview).where(MovieReview.id == review_id, MovieReview.movie_id == movie_id))
    review = result.scalar_one_or_none()
    if review is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đánh giá")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn chỉ có thể sửa đánh giá của mình")
    review.rating, review.content = payload.rating, payload.content
    await db.commit()
    await db.refresh(review)
    verified = bool(await _verified_review_users(db, movie_id, [current_user.id]))
    return MovieReviewRead(id=review.id, user_id=current_user.id, user_name=current_user.full_name, rating=review.rating, content=review.content, verified_purchase=verified, created_at=review.created_at, updated_at=review.updated_at)


@router.delete("/{movie_id}/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie_review(
    movie_id: UUID,
    review_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(MovieReview).where(MovieReview.id == review_id, MovieReview.movie_id == movie_id))
    review = result.scalar_one_or_none()
    if review is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đánh giá")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn chỉ có thể xóa đánh giá của mình")
    await db.delete(review)
    await db.commit()
