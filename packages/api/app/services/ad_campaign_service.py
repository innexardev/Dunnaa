"""Ad campaign service."""

from datetime import date
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plugin import AdCampaign


class AdCampaignService:
    """Manage ad campaigns and search boost."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_establishment(self, establishment_id: UUID) -> list[AdCampaign]:
        result = await self.db.execute(
            select(AdCampaign)
            .where(AdCampaign.establishment_id == establishment_id)
            .order_by(AdCampaign.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, establishment_id: UUID, campaign_id: UUID) -> AdCampaign | None:
        result = await self.db.execute(
            select(AdCampaign).where(
                AdCampaign.id == campaign_id,
                AdCampaign.establishment_id == establishment_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        establishment_id: UUID,
        *,
        name: str | None,
        budget_daily: float,
        start_date: date,
        end_date: date | None = None,
    ) -> AdCampaign:
        campaign = AdCampaign(
            establishment_id=establishment_id,
            name=name,
            budget_daily=budget_daily,
            start_date=start_date,
            end_date=end_date,
            active=True,
        )
        self.db.add(campaign)
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def update(self, campaign: AdCampaign, **fields) -> AdCampaign:
        for key, value in fields.items():
            if value is not None and hasattr(campaign, key):
                setattr(campaign, key, value)
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def deactivate(self, campaign: AdCampaign) -> None:
        campaign.active = False
        await self.db.commit()

    async def record_impression(self, campaign_id: UUID) -> None:
        campaign = await self.db.get(AdCampaign, campaign_id)
        if not campaign or not campaign.active:
            return
        campaign.impressions += 1
        await self.db.commit()

    async def get_boosted_establishment_ids(self, on_date: date | None = None) -> set[UUID]:
        """Establishment IDs with active ad campaigns (for search ranking)."""
        ref = on_date or date.today()
        result = await self.db.execute(
            select(AdCampaign.establishment_id).where(
                and_(
                    AdCampaign.active == True,
                    AdCampaign.start_date <= ref,
                    (AdCampaign.end_date.is_(None)) | (AdCampaign.end_date >= ref),
                )
            )
        )
        return set(result.scalars().all())
