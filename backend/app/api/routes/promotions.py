from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.permissions import require_admin
from app.db.session import get_db
from app.models.commerce import Promotion
from app.models.user import User
from app.schemas.promotion import PromotionCreate, PromotionQuote, PromotionRead, PromotionUpdate, PromotionValidation

router = APIRouter()


def promotion_discount(promotion: Promotion, subtotal: Decimal) -> Decimal:
    if promotion.discount_type == "PERCENT":
        discount = subtotal * Decimal(promotion.discount_value) / Decimal("100")
        if promotion.max_discount is not None:
            discount = min(discount, Decimal(promotion.max_discount))
    else:
        discount = Decimal(promotion.discount_value)
    return min(subtotal, discount).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def ensure_usable(promotion: Promotion | None, subtotal: Decimal) -> Promotion:
    now = datetime.now(timezone.utc)
    if promotion is None or not promotion.is_active:
        raise HTTPException(status_code=404, detail="Promotion code is invalid")
    if promotion.starts_at > now or promotion.ends_at < now:
        raise HTTPException(status_code=409, detail="Promotion is not currently valid")
    if promotion.usage_limit is not None and promotion.used_count >= promotion.usage_limit:
        raise HTTPException(status_code=409, detail="Promotion usage limit has been reached")
    if subtotal < promotion.min_order_amount:
        raise HTTPException(status_code=409, detail=f"Minimum order amount is {promotion.min_order_amount}")
    return promotion


@router.get("", response_model=list[PromotionRead], dependencies=[Depends(require_admin)])
async def list_promotions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Promotion).order_by(Promotion.created_at.desc()))
    return list(result.scalars().all())


@router.post("", response_model=PromotionRead, status_code=status.HTTP_201_CREATED)
async def create_promotion(
    payload: PromotionCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    promotion = Promotion(**payload.model_dump(), created_by=admin.id)
    db.add(promotion)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Promotion code already exists") from None
    await db.refresh(promotion)
    return promotion


@router.patch("/{promotion_id}", response_model=PromotionRead)
async def update_promotion(
    promotion_id: UUID,
    payload: PromotionUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    promotion = await db.get(Promotion, promotion_id)
    if promotion is None:
        raise HTTPException(status_code=404, detail="Promotion not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(promotion, field, value)
    if promotion.ends_at <= promotion.starts_at:
        raise HTTPException(status_code=422, detail="ends_at must be after starts_at")
    if promotion.discount_type not in {"PERCENT", "FIXED"}:
        raise HTTPException(status_code=422, detail="discount_type must be PERCENT or FIXED")
    await db.commit()
    await db.refresh(promotion)
    return promotion


@router.delete("/{promotion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promotion(
    promotion_id: UUID,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    promotion = await db.get(Promotion, promotion_id)
    if promotion is None:
        raise HTTPException(status_code=404, detail="Promotion not found")
    promotion.is_active = False
    await db.commit()


@router.post("/validate", response_model=PromotionQuote)
async def validate_promotion(
    payload: PromotionValidation,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Promotion).where(Promotion.code == payload.code.strip().upper()))
    promotion = ensure_usable(result.scalar_one_or_none(), payload.subtotal)
    discount = promotion_discount(promotion, payload.subtotal)
    return PromotionQuote(
        promotion_id=promotion.id,
        code=promotion.code,
        subtotal=payload.subtotal,
        discount_amount=discount,
        total_amount=payload.subtotal - discount,
        message=f"Applied {promotion.code}",
    )
