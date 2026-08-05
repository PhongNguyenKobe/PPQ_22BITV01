from __future__ import annotations

from uuid import UUID

from sqlalchemy import or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash
from app.models.user import Role, User
from app.schemas.user import UserCreate, UserUpdate


async def populate_user_branch_id(db: AsyncSession, user: User) -> None:
    user.branch_id = None
    user_roles = [role.code for role in user.roles]
    if "BRANCH_ADMIN" in user_roles or "STAFF" in user_roles:
        row = (await db.execute(
            text("SELECT branch_id FROM branch_staff WHERE user_id = :user_id AND is_active = TRUE LIMIT 1"),
            {"user_id": user.id}
        )).first()
        if row:
            user.branch_id = row.branch_id


async def get_role_by_code(db: AsyncSession, code: str) -> Role | None:
    result = await db.execute(select(Role).where(Role.code == code))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).options(selectinload(User.roles)).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        await populate_user_branch_id(db, user)
    return user


async def get_user_by_phone(db: AsyncSession, phone: str) -> User | None:
    result = await db.execute(select(User).options(selectinload(User.roles)).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if user:
        await populate_user_branch_id(db, user)
    return user


async def get_user_by_identifier(db: AsyncSession, identifier: str) -> User | None:
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(or_(User.email == identifier, User.phone == identifier))
    )
    user = result.scalar_one_or_none()
    if user:
        await populate_user_branch_id(db, user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    result = await db.execute(select(User).options(selectinload(User.roles)).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        await populate_user_branch_id(db, user)
    return user
    
async def list_users(db: AsyncSession, skip: int = 0, limit: int = 20) -> list[User]:
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())

async def create_user(db: AsyncSession, user_in: UserCreate, default_role_code: str = "CUSTOMER") -> User:
    if await get_user_by_email(db, user_in.email):
        raise ValueError("EMAIL_EXISTS")
    if user_in.phone and await get_user_by_phone(db, user_in.phone):
        raise ValueError("PHONE_EXISTS")

    role = await get_role_by_code(db, default_role_code)
    if role is None:
        raise ValueError("ROLE_NOT_FOUND")

    user = User(
        email=user_in.email,
        phone=user_in.phone,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        date_of_birth=user_in.date_of_birth,
        gender=user_in.gender,
        address=user_in.address,
        receive_marketing_emails=user_in.receive_marketing_emails,
        is_verified=False,
        roles=[role],
    )
    db.add(user)
    await db.commit()

    fresh_user = await get_user_by_id(db, user.id)
    if fresh_user is None:
        raise RuntimeError("User creation failed")
    return fresh_user


async def update_user(db: AsyncSession, user: User, user_in: UserUpdate) -> User:
    data = user_in.model_dump(exclude_unset=True)

    if "phone" in data and data["phone"]:
        existing_user = await get_user_by_phone(db, data["phone"])
        if existing_user and existing_user.id != user.id:
            raise ValueError("PHONE_EXISTS")

    for field, value in data.items():
        setattr(user, field, value)

    db.add(user)
    await db.commit()

    fresh_user = await get_user_by_id(db, user.id)
    if fresh_user is None:
        raise RuntimeError("User update failed")
    return fresh_user
