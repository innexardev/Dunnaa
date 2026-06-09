"""Promotion service unit tests."""

from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.promotion_service import PromotionService


@pytest.mark.asyncio
async def test_promotion_crud(db_engine, establishment_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    est_id = UUID(str(establishment_id))
    async with Session() as session:
        service = PromotionService(session)
        promo = await service.create(
            est_id,
            title="Test Promo",
            discount_type="percent",
            discount_value=15,
        )
        assert promo.active is True

        listed = await service.list_for_establishment(est_id)
        assert len(listed) == 1

        await service.deactivate(promo)
        active = await service.list_for_establishment(est_id, active_only=True)
        assert len(active) == 0
