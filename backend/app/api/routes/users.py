from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.crud.booking import booking_to_dict, list_user_booking_rows
from app.crud.user import get_user_by_id, list_users, update_user
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.schemas.user import PasswordChange, UserRead, UserUpdate
from app.schemas.booking import BookingRead

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


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_password(
    payload: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không chính xác",
        )
    if verify_password(payload.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới phải khác mật khẩu hiện tại",
        )
    current_user.password_hash = get_password_hash(payload.new_password)
    db.add(current_user)
    await db.commit()


@router.get("/me/tickets", response_model=list[BookingRead])
async def read_my_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BookingRead]:
    _, rows = await list_user_booking_rows(db, current_user.id, 0, 100)
    return [BookingRead(**booking_to_dict(item)) for item in rows]


@router.get("", response_model=list[UserRead])
async def read_users(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> list[UserRead]:
    users = await list_users(db, skip=skip, limit=limit)
    return [UserRead.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> UserRead:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserRead.model_validate(user)
