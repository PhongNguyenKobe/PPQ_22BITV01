from __future__ import annotations

import asyncio
from pathlib import Path
import sys

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import Role, User


DEMO_USERS = [
    {
        "email": "customer@gmail.com",
        "phone": "0900000004",
        "full_name": "Nguyễn Văn Khách",
        "password": "customer123",
        "role": "CUSTOMER",
    },
    {
        "email": "admin@cineai.vn",
        "phone": "0900000002",
        "full_name": "Quản Trị Viên CineAI",
        "password": "admin123",
        "role": "SUPER_ADMIN",
    },
    {
        "email": "admin1@cineai.vn",
        "phone": "0900000003",
        "full_name": "Quản trị viên chi nhánh CineAI",
        "password": "admin321",
        "role": "BRANCH_ADMIN",
    },
]


async def upsert_roles(session: AsyncSession) -> None:
    """Bổ sung role demo còn thiếu mà không xóa role đang được sử dụng."""
    for code, name in [
        ("CUSTOMER", "Khách hàng"),
        ("SUPER_ADMIN", "Quản trị viên"),
        ("BRANCH_ADMIN", "Quản trị chi nhánh"),
    ]:
        result = await session.execute(select(Role).where(Role.code == code))
        if result.scalar_one_or_none() is None:
            role_ids = {"CUSTOMER": 1, "SUPER_ADMIN": 2, "BRANCH_ADMIN": 3}
            session.add(Role(id=role_ids[code], code=code, name=name))
    await session.commit()


async def upsert_demo_users(session: AsyncSession) -> None:
    """Cập nhật tại chỗ để giữ user_id được bookings và dữ liệu khác tham chiếu."""
    for payload in DEMO_USERS:
        role_result = await session.execute(
            select(Role).where(Role.code == payload["role"])
        )
        role = role_result.scalar_one_or_none()
        if role is None:
            continue

        user_result = await session.execute(
            select(User).where(User.email == payload["email"])
        )
        user = user_result.scalar_one_or_none()
        if user is None:
            user = User(email=payload["email"])
            session.add(user)

        user.phone = payload["phone"]
        user.password_hash = get_password_hash(payload["password"])
        user.full_name = payload["full_name"]
        user.is_active = True
        user.is_verified = True
        user.roles = [role]

    await session.commit()


async def migrate_legacy_branch_admin(session: AsyncSession) -> None:
    """Đổi tài khoản demo cũ sang thông tin đăng nhập mới và giữ nguyên liên kết chi nhánh."""
    legacy = await session.scalar(select(User).where(User.email == "branchadmin@cineai.vn"))
    current = await session.scalar(select(User).where(User.email == "admin1@cineai.vn"))
    if legacy is not None and current is None:
        legacy.email = "admin1@cineai.vn"
        await session.commit()
    elif legacy is not None and current is not None:
        await session.execute(text("DELETE FROM branch_staff WHERE user_id = :user_id"), {"user_id": legacy.id})
        legacy.phone = None
        legacy.is_active = False
        await session.commit()


async def assign_demo_branch_admin(session: AsyncSession) -> None:
    """Gán tài khoản branch admin demo vào chi nhánh đầu tiên nếu dữ liệu mẫu có chi nhánh."""
    user_id = await session.scalar(select(User.id).where(User.email == "admin1@cineai.vn"))
    branch_id = await session.scalar(text("SELECT id FROM branches WHERE is_active = TRUE ORDER BY created_at LIMIT 1"))
    if user_id is None or branch_id is None:
        return
    await session.execute(
        text("""
            INSERT INTO branch_staff (branch_id, user_id, staff_role, is_active)
            VALUES (:branch_id, :user_id, 'BRANCH_ADMIN', TRUE)
            ON CONFLICT (branch_id, user_id)
            DO UPDATE SET staff_role = EXCLUDED.staff_role, is_active = TRUE
        """),
        {"branch_id": branch_id, "user_id": user_id},
    )
    await session.commit()


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await upsert_roles(session)
        await migrate_legacy_branch_admin(session)
        await upsert_demo_users(session)
        await assign_demo_branch_admin(session)
        print("Seed hoàn tất. Tài khoản demo:")
        print("   - Khách hàng: customer@gmail.com / customer123")
        print("   - Quản trị viên: admin@cineai.vn / admin123")
        print("   - Quản trị chi nhánh: admin1@cineai.vn / admin321")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
