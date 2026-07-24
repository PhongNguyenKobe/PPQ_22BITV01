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

# Chỉ còn 2 role: CUSTOMER và SUPER_ADMIN
DEMO_USERS = [
    {"email": "customer@gmail.com", "phone": "0900000004", "full_name": "Nguyễn Văn Khách", "password": "customer123", "role": "CUSTOMER"},
    {"email": "admin@cineai.vn", "phone": "0900000002", "full_name": "Quản Trị Viên CineAI", "password": "admin123", "role": "SUPER_ADMIN"},
]


async def upsert_roles(session: AsyncSession) -> None:
    """Đảm bảo chỉ có 2 role: CUSTOMER và SUPER_ADMIN, xóa BRANCH_ADMIN và STAFF nếu có."""
    roles_to_keep = ["CUSTOMER", "SUPER_ADMIN"]
    # Xóa roles không dùng
    result = await session.execute(select(Role))
    all_roles = result.scalars().all()
    for role in all_roles:
        if role.code not in roles_to_keep:
            await session.delete(role)
    await session.commit()

    # Tạo lại nếu chưa có
    for code, name in [("CUSTOMER", "Khách hàng"), ("SUPER_ADMIN", "Quản trị viên")]:
        result = await session.execute(select(Role).where(Role.code == code))
        if result.scalar_one_or_none() is None:
            role = Role(id=1 if code == "CUSTOMER" else 2, code=code, name=name)
            session.add(role)
    await session.commit()


async def upsert_demo_users(session: AsyncSession) -> None:
    # Dùng raw SQL để xoá users cũ (tránh autoflush gây lỗi)
    demo_emails = [u["email"] for u in DEMO_USERS]
    demo_phones = [u["phone"] for u in DEMO_USERS if u["phone"]]

    # Xoá user_roles trước, sau đó xoá users
    for email in demo_emails:
        await session.execute(
            User.__table__.delete().where(User.email == email)
        )
    for phone in demo_phones:
        await session.execute(
            User.__table__.delete().where(
                User.phone == phone,
                User.email.notin_(demo_emails),
            )
        )
    await session.commit()

    # Tạo lại users demo với bcrypt hash đúng
    for payload in DEMO_USERS:
        role_result = await session.execute(
            select(Role).where(Role.code == payload["role"])
        )
        role = role_result.scalar_one_or_none()
        if role is None:
            continue

        user = User(
            email=payload["email"],
            phone=payload["phone"],
            password_hash=get_password_hash(payload["password"]),
            full_name=payload["full_name"],
            roles=[role],
        )
        session.add(user)

    await session.commit()


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await upsert_roles(session)
        await upsert_demo_users(session)
        print("✅ Seed hoàn tất! Tài khoản demo:")
        print("   - Khách hàng: customer@gmail.com / customer123")
        print("   - Quản trị viên: admin@cineai.vn / admin123")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

