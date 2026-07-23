from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import Role, User, user_roles_table
from app.schemas.admin import BranchRead, UserRoleUpdate


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

