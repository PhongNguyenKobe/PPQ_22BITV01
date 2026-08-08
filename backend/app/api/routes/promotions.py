from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.permissions import require_admin
from app.db.session import get_db
from app.models.catalog import Auditorium, Showtime
from app.models.commerce import AuditEvent, Promotion, PromotionRedemption
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


async def ensure_context_usable(
    db: AsyncSession,
    promotion: Promotion,
    *,
    user_id: UUID,
    showtime: Showtime,
    payment_method: str,
    discount: Decimal,
) -> None:
    branch_id = await db.scalar(select(Auditorium.branch_id).where(Auditorium.id == showtime.auditorium_id))
    method = "VNPAY" if payment_method.upper() in {"VNPAY", "VÍ VNPAY"} else payment_method.upper()
    if promotion.branch_ids and str(branch_id) not in promotion.branch_ids:
        raise HTTPException(status_code=409, detail="Promotion is not valid at this branch")
    if promotion.movie_ids and str(showtime.movie_id) not in promotion.movie_ids:
        raise HTTPException(status_code=409, detail="Promotion is not valid for this movie")
    if promotion.payment_methods and method not in [str(item).upper() for item in promotion.payment_methods]:
        raise HTTPException(status_code=409, detail="Promotion is not valid for this payment method")
    if showtime.starts_at.date().isoformat() in promotion.excluded_dates:
        raise HTTPException(status_code=409, detail="Promotion is excluded on this date")
    reserved_total = int(await db.scalar(select(func.count(PromotionRedemption.id)).where(
        PromotionRedemption.promotion_id == promotion.id,
        PromotionRedemption.status.in_(["RESERVED", "USED"]),
    )) or 0)
    if promotion.usage_limit is not None and reserved_total >= promotion.usage_limit:
        raise HTTPException(status_code=409, detail="Promotion usage limit has been reached")
    if promotion.per_user_limit is not None:
        user_total = int(await db.scalar(select(func.count(PromotionRedemption.id)).where(
            PromotionRedemption.promotion_id == promotion.id,
            PromotionRedemption.user_id == user_id,
            PromotionRedemption.status.in_(["RESERVED", "USED"]),
        )) or 0)
        if user_total >= promotion.per_user_limit:
            raise HTTPException(status_code=409, detail="Your promotion usage limit has been reached")
    if promotion.budget_amount is not None:
        committed = Decimal(str(await db.scalar(select(func.coalesce(func.sum(PromotionRedemption.discount_amount), 0)).where(
            PromotionRedemption.promotion_id == promotion.id,
            PromotionRedemption.status.in_(["RESERVED", "USED"]),
        )) or 0))
        if committed + discount > promotion.budget_amount:
            raise HTTPException(status_code=409, detail="Promotion budget has been exhausted")


@router.get("", response_model=list[PromotionRead], dependencies=[Depends(require_admin)])
async def list_promotions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Promotion).order_by(Promotion.created_at.desc()))
    return list(result.scalars().all())


@router.get("/public", response_model=list[PromotionRead])
async def list_public_promotions(db: AsyncSession = Depends(get_db)):
    """Customer-facing promotions backed by the admin-managed promotion table."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Promotion)
        .where(
            Promotion.is_active.is_(True),
            Promotion.starts_at <= now,
            Promotion.ends_at >= now,
            or_(Promotion.usage_limit.is_(None), Promotion.used_count < Promotion.usage_limit),
        )
        .order_by(Promotion.starts_at.asc(), Promotion.created_at.desc())
    )
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
        await db.flush()
        db.add(AuditEvent(
            entity_type="PROMOTION", entity_id=str(promotion.id), action="CREATE_PROMOTION",
            old_data=None,
            new_data={**payload.model_dump(mode="json"), "performed_by": str(admin.id)},
        ))
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
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    promotion = await db.get(Promotion, promotion_id)
    if promotion is None:
        raise HTTPException(status_code=404, detail="Promotion not found")
    changes = payload.model_dump(exclude_unset=True)
    candidate = PromotionCreate.model_validate({
        "code": promotion.code,
        "name": promotion.name,
        "discount_type": promotion.discount_type,
        "discount_value": promotion.discount_value,
        "max_discount": promotion.max_discount,
        "min_order_amount": promotion.min_order_amount,
        "starts_at": promotion.starts_at,
        "ends_at": promotion.ends_at,
        "usage_limit": promotion.usage_limit,
        "per_user_limit": promotion.per_user_limit,
        "budget_amount": promotion.budget_amount,
        "branch_ids": promotion.branch_ids,
        "movie_ids": promotion.movie_ids,
        "payment_methods": promotion.payment_methods,
        "excluded_dates": promotion.excluded_dates,
        "is_active": promotion.is_active,
        **changes,
    })
    if promotion.used_count > 0 and any(field in changes for field in ("discount_type", "discount_value")):
        raise HTTPException(status_code=409, detail="USED_PROMOTION_DISCOUNT_IMMUTABLE")
    old_data = {field: jsonable_encoder(getattr(promotion, field)) for field in changes}
    for field, value in candidate.model_dump().items():
        if field in changes:
            setattr(promotion, field, value)
    if promotion.ends_at <= promotion.starts_at:
        raise HTTPException(status_code=422, detail="ends_at must be after starts_at")
    if promotion.discount_type not in {"PERCENT", "FIXED"}:
        raise HTTPException(status_code=422, detail="discount_type must be PERCENT or FIXED")
    db.add(AuditEvent(
        entity_type="PROMOTION", entity_id=str(promotion.id), action="UPDATE_PROMOTION",
        old_data=old_data,
        new_data={**jsonable_encoder(changes), "performed_by": str(admin.id)},
    ))
    await db.commit()
    await db.refresh(promotion)
    return promotion


@router.delete("/{promotion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promotion(
    promotion_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    promotion = await db.get(Promotion, promotion_id)
    if promotion is None:
        raise HTTPException(status_code=404, detail="Promotion not found")
    old_active = promotion.is_active
    promotion.is_active = False
    db.add(AuditEvent(
        entity_type="PROMOTION", entity_id=str(promotion.id), action="DISABLE_PROMOTION",
        old_data={"is_active": old_active},
        new_data={"is_active": False, "performed_by": str(admin.id)},
    ))
    await db.commit()


@router.post("/validate", response_model=PromotionQuote)
async def validate_promotion(
    payload: PromotionValidation,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Promotion).where(Promotion.code == payload.code.strip().upper()))
    promotion = ensure_usable(result.scalar_one_or_none(), payload.subtotal)
    discount = promotion_discount(promotion, payload.subtotal)
    showtime = await db.get(Showtime, payload.showtime_id)
    if showtime is None:
        raise HTTPException(status_code=404, detail="Showtime not found")
    await ensure_context_usable(
        db, promotion, user_id=user.id, showtime=showtime,
        payment_method=payload.payment_method, discount=discount,
    )
    return PromotionQuote(
        promotion_id=promotion.id,
        code=promotion.code,
        subtotal=payload.subtotal,
        discount_amount=discount,
        total_amount=payload.subtotal - discount,
        message=f"Applied {promotion.code}",
    )
