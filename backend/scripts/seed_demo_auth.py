from __future__ import annotations

import asyncio
from pathlib import Path
import sys

from sqlalchemy import select
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
]


async def upsert_roles(session: AsyncSession) -> None:
    """Bổ sung role demo còn thiếu mà không xóa role đang được sử dụng."""
    for code, name in [
        ("CUSTOMER", "Khách hàng"),
        ("SUPER_ADMIN", "Quản trị viên"),
    ]:
        result = await session.execute(select(Role).where(Role.code == code))
        if result.scalar_one_or_none() is None:
            session.add(Role(id=1 if code == "CUSTOMER" else 2, code=code, name=name))
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
        user.roles = [role]

    await session.commit()


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await upsert_roles(session)
        await upsert_demo_users(session)
        print("Seed hoàn tất. Tài khoản demo:")
        print("   - Khách hàng: customer@gmail.com / customer123")
        print("   - Quản trị viên: admin@cineai.vn / admin123")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
