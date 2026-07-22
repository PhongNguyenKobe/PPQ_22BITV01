from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.crud.admin import approve_movie_request, create_movie_request, get_movie_request_by_id, list_movie_requests, reject_movie_request
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import MovieRequestCreate, MovieRequestRead, MovieRequestReview

router = APIRouter()


@router.post("", response_model=MovieRequestRead, status_code=status.HTTP_201_CREATED)
async def submit_movie_request(
    payload: MovieRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN", "STAFF")),
) -> MovieRequestRead:
    created = await create_movie_request(db, current_user, payload)
    return MovieRequestRead.model_validate(created)


@router.get("/mine", response_model=list[MovieRequestRead])
async def read_my_movie_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BRANCH_ADMIN", "STAFF")),
) -> list[MovieRequestRead]:
    requests = await list_movie_requests(db, requested_by_id=current_user.id)
    return [MovieRequestRead.model_validate(item) for item in requests]


@router.get("/admin", response_model=list[MovieRequestRead])
async def read_pending_movie_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> list[MovieRequestRead]:
    requests = await list_movie_requests(db)
    return [MovieRequestRead.model_validate(item) for item in requests]


@router.post("/admin/{request_id}/approve", response_model=MovieRequestRead)
async def approve_request(
    request_id: UUID,
    payload: MovieRequestReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> MovieRequestRead:
    request = await get_movie_request_by_id(db, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie request not found")
    updated = await approve_movie_request(db, request, current_user, payload.review_note)
    return MovieRequestRead.model_validate(updated)


@router.post("/admin/{request_id}/reject", response_model=MovieRequestRead)
async def reject_request(
    request_id: UUID,
    payload: MovieRequestReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> MovieRequestRead:
    request = await get_movie_request_by_id(db, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie request not found")
    updated = await reject_movie_request(db, request, current_user, payload.review_note)
    return MovieRequestRead.model_validate(updated)