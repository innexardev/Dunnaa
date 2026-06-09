"""Promotion endpoints."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, DBSession, verify_establishment_owner
from app.services.promotion_service import PromotionService

router = APIRouter(prefix="/establishments/{establishment_id}/promotions", tags=["Promotions"])


class PromotionCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: str | None = None
    discount_type: str | None = Field(None, pattern="^(percent|fixed)$")
    discount_value: float | None = Field(None, gt=0)
    service_id: UUID | None = None
    bundle_id: UUID | None = None
    start_date: date | None = None
    end_date: date | None = None


class PromotionUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str | None = None
    discount_type: str | None = Field(None, pattern="^(percent|fixed)$")
    discount_value: float | None = Field(None, gt=0)
    service_id: UUID | None = None
    bundle_id: UUID | None = None
    start_date: date | None = None
    end_date: date | None = None
    active: bool | None = None


class PromotionResponse(BaseModel):
    id: str
    establishment_id: str
    title: str
    description: str | None
    discount_type: str | None
    discount_value: float | None
    service_id: str | None
    bundle_id: str | None
    start_date: date | None
    end_date: date | None
    active: bool

    model_config = {"from_attributes": True}


def _to_response(p) -> PromotionResponse:
    return PromotionResponse(
        id=str(p.id),
        establishment_id=str(p.establishment_id),
        title=p.title,
        description=p.description,
        discount_type=p.discount_type,
        discount_value=float(p.discount_value) if p.discount_value else None,
        service_id=str(p.service_id) if p.service_id else None,
        bundle_id=str(p.bundle_id) if p.bundle_id else None,
        start_date=p.start_date,
        end_date=p.end_date,
        active=p.active,
    )


@router.get("", response_model=list[PromotionResponse])
async def list_promotions(
    establishment_id: UUID,
    db: DBSession,
    active_only: bool = True,
) -> list[PromotionResponse]:
    """List active promotions (public)."""
    service = PromotionService(db)
    promotions = await service.list_for_establishment(establishment_id, active_only=active_only)
    return [_to_response(p) for p in promotions]


@router.post("", response_model=PromotionResponse, status_code=status.HTTP_201_CREATED)
async def create_promotion(
    establishment_id: UUID,
    data: PromotionCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> PromotionResponse:
    """Create promotion (owner only)."""
    await verify_establishment_owner(db, establishment_id, current_user)
    service = PromotionService(db)
    promotion = await service.create(
        establishment_id,
        title=data.title,
        description=data.description,
        discount_type=data.discount_type,
        discount_value=data.discount_value,
        service_id=data.service_id,
        bundle_id=data.bundle_id,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    return _to_response(promotion)


@router.patch("/{promotion_id}", response_model=PromotionResponse)
async def update_promotion(
    establishment_id: UUID,
    promotion_id: UUID,
    data: PromotionUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> PromotionResponse:
    """Update promotion (owner only)."""
    await verify_establishment_owner(db, establishment_id, current_user)
    service = PromotionService(db)
    promotion = await service.get(establishment_id, promotion_id)
    if not promotion:
        raise HTTPException(status_code=404, detail="Promoção não encontrada")

    updated = await service.update(promotion, **data.model_dump(exclude_unset=True))
    return _to_response(updated)


@router.delete("/{promotion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promotion(
    establishment_id: UUID,
    promotion_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> None:
    """Deactivate promotion (owner only)."""
    await verify_establishment_owner(db, establishment_id, current_user)
    service = PromotionService(db)
    promotion = await service.get(establishment_id, promotion_id)
    if not promotion:
        raise HTTPException(status_code=404, detail="Promoção não encontrada")
    await service.deactivate(promotion)
