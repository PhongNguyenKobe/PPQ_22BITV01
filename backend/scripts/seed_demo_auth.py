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
    {"email": "customer@gmail.com", "phone": "0900000004", "full_name": "Nguyễn Đăng Khách", "password": "customer123", "role": "CUSTOMER"},
    {"email": "admin@cineai.vn", "phone": "0900000002", "full_name": "Admin CineAI", "password": "admin123", "role": "SUPER_ADMIN"},
    {"email": "branch@cineai.vn", "phone": "0900000003", "full_name": "Branch Admin", "password": "branch123", "role": "BRANCH_ADMIN"},
]


async def upsert_demo_users(session: AsyncSession) -> None:
    for payload in DEMO_USERS:
        with session.no_autoflush:
            role_result = await session.execute(select(Role).where(Role.code == payload["role"]))
            role = role_result.scalar_one_or_none()
            if role is None:
                continue

            user_result = await session.execute(
                select(User).where((User.email == payload["email"]) | (User.phone == payload["phone"]))
            )
            user = user_result.scalar_one_or_none()

        if user is None:
            user = User(
                email=payload["email"],
                phone=payload["phone"],
                password_hash=get_password_hash(payload["password"]),
                full_name=payload["full_name"],
                roles=[role],
            )
            session.add(user)
        else:
            user.email = payload["email"]
            user.phone = payload["phone"]
            user.password_hash = get_password_hash(payload["password"])
            user.full_name = payload["full_name"]
            if role not in user.roles:
                user.roles.append(role)

    await session.commit()


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await upsert_demo_users(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
