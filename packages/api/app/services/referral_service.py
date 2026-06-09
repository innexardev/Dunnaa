"""Referral service."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.referral import Referral

DEFAULT_REWARD_AMOUNT = Decimal("10.00")


class ReferralService:
    """Referral rewards."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_referral(
        self,
        referrer_id: UUID,
        referred_id: UUID,
        reward_amount: Decimal | None = None,
    ) -> Referral:
        """Record a new referral when a user signs up with a code."""
        referral = Referral(
            referrer_id=referrer_id,
            referred_id=referred_id,
            reward_amount=reward_amount or DEFAULT_REWARD_AMOUNT,
            reward_claimed=False,
        )
        self.db.add(referral)
        await self.db.commit()
        await self.db.refresh(referral)
        return referral

    async def list_by_referrer(self, referrer_id: UUID) -> list[Referral]:
        """List referrals made by a user."""
        result = await self.db.execute(
            select(Referral)
            .where(Referral.referrer_id == referrer_id)
            .options(selectinload(Referral.referred))
            .order_by(Referral.created_at.desc())
        )
        return list(result.scalars().all())

    async def claim_reward(self, referral_id: UUID, referrer_id: UUID) -> Referral:
        """Mark referral reward as claimed."""
        result = await self.db.execute(
            select(Referral).where(
                Referral.id == referral_id,
                Referral.referrer_id == referrer_id,
            )
        )
        referral = result.scalar_one_or_none()
        if not referral:
            raise ValueError("Indicação não encontrada")
        if referral.reward_claimed:
            raise ValueError("Recompensa já resgatada")

        referral.reward_claimed = True
        await self.db.commit()
        await self.db.refresh(referral)
        return referral

    async def get_stats(self, referrer_id: UUID) -> dict:
        """Summary stats for referrer."""
        referrals = await self.list_by_referrer(referrer_id)
        pending = [r for r in referrals if not r.reward_claimed]
        claimed = [r for r in referrals if r.reward_claimed]
        return {
            "total_referrals": len(referrals),
            "pending_rewards": len(pending),
            "claimed_rewards": len(claimed),
            "pending_amount": float(sum(r.reward_amount or 0 for r in pending)),
            "claimed_amount": float(sum(r.reward_amount or 0 for r in claimed)),
        }
