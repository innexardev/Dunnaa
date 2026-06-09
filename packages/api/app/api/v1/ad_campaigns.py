"""Ad campaign endpoints."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, DBSession, verify_establishment_owner
from app.services.ad_campaign_service import AdCampaignService

router = APIRouter(
    prefix="/establishments/{establishment_id}/ad-campaigns",
    tags=["Ad Campaigns"],
)


class AdCampaignCreate(BaseModel):
    name: str | None = Field(None, max_length=200)
    budget_daily: float = Field(..., gt=0)
    start_date: date
    end_date: date | None = None


class AdCampaignUpdate(BaseModel):
    name: str | None = None
    budget_daily: float | None = Field(None, gt=0)
    start_date: date | None = None
    end_date: date | None = None
    active: bool | None = None


class AdCampaignResponse(BaseModel):
    id: str
    establishment_id: str
    name: str | None
    budget_daily: float
    spent_today: float
    total_spent: float
    impressions: int
    clicks: int
    start_date: date
    end_date: date | None
    active: bool

    model_config = {"from_attributes": True}


def _to_response(c) -> AdCampaignResponse:
    return AdCampaignResponse(
        id=str(c.id),
        establishment_id=str(c.establishment_id),
        name=c.name,
        budget_daily=float(c.budget_daily),
        spent_today=float(c.spent_today),
        total_spent=float(c.total_spent),
        impressions=c.impressions,
        clicks=c.clicks,
        start_date=c.start_date,
        end_date=c.end_date,
        active=c.active,
    )


@router.get("", response_model=list[AdCampaignResponse])
async def list_campaigns(establishment_id: UUID, db: DBSession, current_user: CurrentUser):
    """List ad campaigns (owner)."""
    await verify_establishment_owner(db, establishment_id, current_user)
    service = AdCampaignService(db)
    return [_to_response(c) for c in await service.list_for_establishment(establishment_id)]


@router.post("", response_model=AdCampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    establishment_id: UUID,
    data: AdCampaignCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Create ad campaign (owner)."""
    await verify_establishment_owner(db, establishment_id, current_user)
    service = AdCampaignService(db)
    campaign = await service.create(
        establishment_id,
        name=data.name,
        budget_daily=data.budget_daily,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    return _to_response(campaign)


@router.patch("/{campaign_id}", response_model=AdCampaignResponse)
async def update_campaign(
    establishment_id: UUID,
    campaign_id: UUID,
    data: AdCampaignUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Update ad campaign (owner)."""
    await verify_establishment_owner(db, establishment_id, current_user)
    service = AdCampaignService(db)
    campaign = await service.get(establishment_id, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    updated = await service.update(campaign, **data.model_dump(exclude_unset=True))
    return _to_response(updated)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_campaign(
    establishment_id: UUID,
    campaign_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Deactivate ad campaign (owner)."""
    await verify_establishment_owner(db, establishment_id, current_user)
    service = AdCampaignService(db)
    campaign = await service.get(establishment_id, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    await service.deactivate(campaign)


@router.post("/{campaign_id}/impressions", status_code=status.HTTP_204_NO_CONTENT)
async def record_impression(establishment_id: UUID, campaign_id: UUID, db: DBSession):
    """Record ad impression (public tracking)."""
    service = AdCampaignService(db)
    campaign = await service.get(establishment_id, campaign_id)
    if not campaign or not campaign.active:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    await service.record_impression(campaign_id)
