from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.user import update_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_my_profile(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead)
async def update_my_profile(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    try:
        updated_user = await update_user(db, current_user, payload)
    except ValueError as exc:
        if str(exc) == "PHONE_EXISTS":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already exists") from None
        raise
    return UserRead.model_validate(updated_user)
