from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_roles
from app.crud.admin import list_branches, list_users_with_branch_id, set_user_role
from app.crud.user import get_user_by_id
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import AdminUserRead, BranchRead, UserRoleUpdate

router = APIRouter()


@router.get("/branches", response_model=list[BranchRead])
async def read_admin_branches(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> list[BranchRead]:
    return await list_branches(db)


@router.get("/users", response_model=list[AdminUserRead])
async def read_admin_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> list[AdminUserRead]:
    rows = await list_users_with_branch_id(db)
    result: list[AdminUserRead] = []
    for user, branch_id in rows:
        user_read = AdminUserRead.model_validate(user)
        result.append(user_read.model_copy(update={"branch_id": branch_id}))
    return result


@router.patch("/users/{user_id}/role", response_model=AdminUserRead)
async def update_admin_user_role(
    user_id: UUID,
    payload: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
) -> AdminUserRead:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        updated_user = await set_user_role(db, user, payload)
    except ValueError as exc:
        message = str(exc)
        if message == "ROLE_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found") from None
        if message == "BRANCH_REQUIRED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Branch is required for branch-admin/staff") from None
        raise

    branch_rows = await list_users_with_branch_id(db)
    branch_id = next((item_branch for item_user, item_branch in branch_rows if item_user.id == updated_user.id), None)
    return AdminUserRead.model_validate(updated_user).model_copy(update={"branch_id": branch_id})
