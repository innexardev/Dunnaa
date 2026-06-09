"""Plugin and ad campaign service unit tests."""

from datetime import date, timedelta
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.ad_campaign_service import AdCampaignService
from app.services.plugin_service import PluginService


@pytest.mark.asyncio
async def test_plugin_install(db_engine, establishment_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    est_id = UUID(str(establishment_id))
    async with Session() as session:
        service = PluginService(session)
        plugin = await service.install(est_id, "marketing", {"enabled": True})
        assert plugin.active is True
        assert await service.has_active(est_id, "marketing") is True


@pytest.mark.asyncio
async def test_ad_campaign_boost(db_engine, establishment_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    est_id = UUID(str(establishment_id))
    today = date.today()
    async with Session() as session:
        service = AdCampaignService(session)
        campaign = await service.create(
            est_id,
            name="Test",
            budget_daily=20.0,
            start_date=today,
            end_date=today + timedelta(days=7),
        )
        await service.record_impression(campaign.id)
        boosted = await service.get_boosted_establishment_ids()
        assert est_id in boosted
