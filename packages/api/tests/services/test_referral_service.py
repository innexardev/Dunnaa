"""Referral service unit tests."""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.user import User
from app.services.referral_service import ReferralService


@pytest.mark.asyncio
async def test_create_and_claim_referral(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        referrer = User(phone="+5511888000001", referral_code="REFAAA01")
        referred = User(phone="+5511888000002", referral_code="REFBBB02")
        session.add_all([referrer, referred])
        await session.commit()
        await session.refresh(referrer)
        await session.refresh(referred)

        service = ReferralService(session)
        referral = await service.create_referral(referrer.id, referred.id)
        assert referral.reward_claimed is False

        stats = await service.get_stats(referrer.id)
        assert stats["total_referrals"] == 1
        assert stats["pending_rewards"] == 1

        claimed = await service.claim_reward(referral.id, referrer.id)
        assert claimed.reward_claimed is True

        with pytest.raises(ValueError, match="já resgatada"):
            await service.claim_reward(referral.id, referrer.id)


@pytest.mark.asyncio
async def test_claim_reward_not_found(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        referrer = User(phone="+5511888000003", referral_code="REFCCC03")
        session.add(referrer)
        await session.commit()
        await session.refresh(referrer)

        service = ReferralService(session)
        with pytest.raises(ValueError, match="não encontrada"):
            await service.claim_reward(uuid4(), referrer.id)
