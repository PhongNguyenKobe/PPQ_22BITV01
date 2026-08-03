from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.commerce import Combo
from app.models.user import User
from app.schemas.combo import ComboRead, ComboWrite

router = APIRouter()


def _super(user: User) -> bool:
    return any(role.code == "SUPER_ADMIN" for role in user.roles)


async def _branch(db: AsyncSession, user: User) -> UUID | None:
    if _super(user):
        return None
    value = await db.scalar(text("SELECT branch_id FROM branch_staff WHERE user_id=:uid AND is_active=TRUE LIMIT 1"), {"uid": str(user.id)})
    if not value:
        raise HTTPException(403, "Tài khoản chưa được phân công chi nhánh")
    return value


@router.get("", response_model=list[ComboRead])
async def public_combos(branch_id: UUID, db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(Combo).where(Combo.branch_id == branch_id, Combo.is_active.is_(True)).order_by(Combo.name))
    return list(rows.scalars().all())


@router.get("/manage", response_model=list[ComboRead])
async def manage_combos(current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")), db: AsyncSession = Depends(get_db)):
    assigned = await _branch(db, current_user)
    query = select(Combo).order_by(Combo.created_at.desc())
    if assigned is not None:
        query = query.where(Combo.branch_id == assigned)
    return list((await db.execute(query)).scalars().all())


@router.post("/manage", response_model=ComboRead, status_code=201)
async def create_combo(payload: ComboWrite, current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")), db: AsyncSession = Depends(get_db)):
    assigned = await _branch(db, current_user)
    if assigned is not None and payload.branch_id != assigned:
        raise HTTPException(403, "Không thể tạo combo cho chi nhánh khác")
    combo = Combo(**payload.model_dump(), created_by=current_user.id)
    db.add(combo)
    await db.commit(); await db.refresh(combo)
    return combo


@router.post("/manage/import-starter", response_model=list[ComboRead])
async def import_starter_combos(current_user: User = Depends(require_roles("BRANCH_ADMIN")), db: AsyncSession = Depends(get_db)):
    branch_id = await _branch(db, current_user)
    starters = [
        ("Combo Solo", "01 bắp rang cỡ vừa + 01 nước ngọt cỡ vừa", 79000),
        ("Combo Couple", "01 bắp rang cỡ lớn + 02 nước ngọt cỡ vừa", 129000),
        ("Combo Family", "02 bắp rang cỡ lớn + 04 nước ngọt cỡ vừa", 239000),
        ("Combo Kids", "01 bắp rang cỡ nhỏ + 01 nước ngọt cỡ nhỏ", 59000),
    ]
    existing = set((await db.execute(select(Combo.name).where(Combo.branch_id == branch_id))).scalars().all())
    for name, description, price in starters:
        if name not in existing:
            db.add(Combo(branch_id=branch_id, name=name, description=description, price=price, stock_quantity=None, is_active=True, created_by=current_user.id))
    await db.commit()
    return list((await db.execute(select(Combo).where(Combo.branch_id == branch_id).order_by(Combo.name))).scalars().all())


@router.patch("/manage/{combo_id}", response_model=ComboRead)
async def update_combo(combo_id: UUID, payload: ComboWrite, current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")), db: AsyncSession = Depends(get_db)):
    combo = await db.get(Combo, combo_id)
    if not combo:
        raise HTTPException(404, "Không tìm thấy combo")
    assigned = await _branch(db, current_user)
    if assigned is not None and (combo.branch_id != assigned or payload.branch_id != assigned):
        raise HTTPException(403, "Không thể quản lý combo của chi nhánh khác")
    for key, value in payload.model_dump().items(): setattr(combo, key, value)
    await db.commit(); await db.refresh(combo)
    return combo


@router.delete("/manage/{combo_id}", status_code=204)
async def delete_combo(combo_id: UUID, current_user: User = Depends(require_roles("SUPER_ADMIN", "BRANCH_ADMIN")), db: AsyncSession = Depends(get_db)):
    combo = await db.get(Combo, combo_id)
    if not combo:
        raise HTTPException(404, "Không tìm thấy combo")
    assigned = await _branch(db, current_user)
    if assigned is not None and combo.branch_id != assigned:
        raise HTTPException(403, "Không thể quản lý combo của chi nhánh khác")
    await db.delete(combo)
    await db.commit()
