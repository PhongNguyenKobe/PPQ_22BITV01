from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.catalog import Movie, MovieChangeRequest, MovieGenre
from app.models.user import Role, User, user_roles_table
from app.schemas.admin import BranchRead, MovieDraftPayload, MovieRequestCreate, UserRoleUpdate


async def list_users_with_branch_id(db: AsyncSession) -> list[tuple[User, UUID | None]]:
    users_result = await db.execute(select(User).options(selectinload(User.roles)).order_by(User.created_at.desc()))
    users = list(users_result.scalars().all())

    branch_rows = await db.execute(text("SELECT user_id, branch_id FROM branch_staff WHERE is_active = TRUE"))
    branch_map = {row.user_id: row.branch_id for row in branch_rows}

    return [(user, branch_map.get(user.id)) for user in users]


async def list_branches(db: AsyncSession) -> list[BranchRead]:
    result = await db.execute(text("SELECT id, code, name, city FROM branches ORDER BY name ASC"))
    return [BranchRead(id=row.id, code=row.code, name=row.name, city=row.city) for row in result]


async def set_user_role(db: AsyncSession, user: User, payload: UserRoleUpdate) -> User:
    role_result = await db.execute(select(Role).where(Role.code == payload.role_code))
    role = role_result.scalar_one_or_none()
    if role is None:
        raise ValueError("ROLE_NOT_FOUND")

    await db.execute(delete(user_roles_table).where(user_roles_table.c.user_id == user.id))
    await db.execute(user_roles_table.insert().values(user_id=user.id, role_id=role.id))

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


async def create_movie_request(db: AsyncSession, requested_by: User, payload: MovieRequestCreate) -> MovieChangeRequest:
    request = MovieChangeRequest(
        requested_by_id=requested_by.id,
        target_movie_id=payload.target_movie_id,
        request_type=payload.request_type,
        status="PENDING",
        payload=payload.payload.model_dump(mode="json"),
    )
    db.add(request)
    await db.commit()

    result = await db.execute(
        select(MovieChangeRequest)
        .options(selectinload(MovieChangeRequest.requested_by))
        .where(MovieChangeRequest.id == request.id)
    )
    created = result.scalar_one_or_none()
    if created is None:
        raise RuntimeError("Movie request creation failed")
    return created


async def list_movie_requests(db: AsyncSession, status_filter: str | None = None, requested_by_id: UUID | None = None) -> list[MovieChangeRequest]:
    query = select(MovieChangeRequest).options(selectinload(MovieChangeRequest.requested_by)).order_by(MovieChangeRequest.created_at.desc())
    if status_filter:
        query = query.where(MovieChangeRequest.status == status_filter)
    if requested_by_id:
        query = query.where(MovieChangeRequest.requested_by_id == requested_by_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_movie_request_by_id(db: AsyncSession, request_id: UUID) -> MovieChangeRequest | None:
    result = await db.execute(
        select(MovieChangeRequest)
        .options(selectinload(MovieChangeRequest.requested_by))
        .where(MovieChangeRequest.id == request_id)
    )
    return result.scalar_one_or_none()


async def _apply_movie_payload(movie: Movie, payload: MovieDraftPayload) -> Movie:
    movie.title = payload.title
    movie.original_title = payload.original_title
    movie.description = payload.description
    movie.duration_min = payload.duration_min
    movie.release_date = payload.release_date
    movie.age_rating = payload.age_rating
    movie.language = payload.language
    movie.trailer_url = payload.trailer_url
    movie.poster_url = payload.poster_url
    movie.status = payload.status
    return movie


async def _sync_movie_genres(db: AsyncSession, movie: Movie, genres: list[str]) -> None:
    genre_result = await db.execute(select(MovieGenre).where(MovieGenre.code.in_(genres)))
    genre_records = list(genre_result.scalars().all())
    movie.genres = genre_records


async def approve_movie_request(db: AsyncSession, request: MovieChangeRequest, reviewer: User, review_note: str | None = None) -> MovieChangeRequest:
    payload = MovieDraftPayload.model_validate(request.payload)
    if request.request_type == "CREATE":
        movie = Movie()
        movie = await _apply_movie_payload(movie, payload)
        db.add(movie)
        await db.flush()
        await _sync_movie_genres(db, movie, payload.genres)
    elif request.request_type == "UPDATE":
        if request.target_movie_id is None:
            raise ValueError("TARGET_MOVIE_REQUIRED")
        movie_result = await db.execute(select(Movie).options(selectinload(Movie.genres)).where(Movie.id == request.target_movie_id))
        movie = movie_result.scalar_one_or_none()
        if movie is None:
            raise ValueError("MOVIE_NOT_FOUND")
        movie = await _apply_movie_payload(movie, payload)
        await _sync_movie_genres(db, movie, payload.genres)
    elif request.request_type == "DELETE":
        if request.target_movie_id is None:
            raise ValueError("TARGET_MOVIE_REQUIRED")
        movie_result = await db.execute(select(Movie).where(Movie.id == request.target_movie_id))
        movie = movie_result.scalar_one_or_none()
        if movie is None:
            raise ValueError("MOVIE_NOT_FOUND")
        await db.delete(movie)
    else:
        raise ValueError("INVALID_REQUEST_TYPE")

    request.status = "APPROVED"
    request.reviewed_by_id = reviewer.id
    request.review_note = review_note
    request.reviewed_at = datetime.now(timezone.utc)
    db.add(request)
    await db.commit()

    refreshed = await db.execute(
        select(MovieChangeRequest)
        .options(selectinload(MovieChangeRequest.requested_by))
        .where(MovieChangeRequest.id == request.id)
    )
    updated_request = refreshed.scalar_one_or_none()
    if updated_request is None:
        raise RuntimeError("Movie request approval failed")
    return updated_request


async def reject_movie_request(db: AsyncSession, request: MovieChangeRequest, reviewer: User, review_note: str | None = None) -> MovieChangeRequest:
    request.status = "REJECTED"
    request.reviewed_by_id = reviewer.id
    request.review_note = review_note
    request.reviewed_at = datetime.now(timezone.utc)
    db.add(request)
    await db.commit()

    refreshed = await db.execute(
        select(MovieChangeRequest)
        .options(selectinload(MovieChangeRequest.requested_by))
        .where(MovieChangeRequest.id == request.id)
    )
    updated_request = refreshed.scalar_one_or_none()
    if updated_request is None:
        raise RuntimeError("Movie request rejection failed")
    return updated_request