from fastapi import APIRouter, Depends
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.admin import BranchRead

router = APIRouter()


@router.get("", response_model=list[BranchRead])
async def read_branches(db: AsyncSession = Depends(get_db)) -> list[BranchRead]:
    """Public endpoint để lấy danh sách rạp chiếu."""
    result = await db.execute(text("SELECT id, code, name, city FROM branches ORDER BY name ASC"))
    return [BranchRead(id=row.id, code=row.code, name=row.name, city=row.city) for row in result]

