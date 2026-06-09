"""Customer subscription business logic."""

from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.establishment import Establishment, EstablishmentStatus
from app.models.subscription import (
    Subscription,
    SubscriptionPlan,
    SubscriptionPlanItem,
    SubscriptionStatus,
    SubscriptionUsage,
)
from app.schemas.subscription import (
    SubscriptionPlanItemUsage,
    SubscriptionUsageSummary,
)


class SubscriptionService:
    """Manage customer subscriptions and usage."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_user(self, user_id: UUID) -> list[Subscription]:
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .options(selectinload(Subscription.plan))
            .order_by(Subscription.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_for_user(self, subscription_id: UUID, user_id: UUID) -> Subscription | None:
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.id == subscription_id, Subscription.user_id == user_id)
            .options(
                selectinload(Subscription.plan).selectinload(SubscriptionPlan.items),
                selectinload(Subscription.usage),
            )
        )
        return result.scalar_one_or_none()

    async def list_for_establishment(self, establishment_id: UUID) -> list[Subscription]:
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.establishment_id == establishment_id)
            .options(selectinload(Subscription.plan))
            .order_by(Subscription.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, user_id: UUID, plan_id: UUID) -> Subscription:
        plan_result = await self.db.execute(
            select(SubscriptionPlan)
            .where(SubscriptionPlan.id == plan_id, SubscriptionPlan.active == True)
            .options(selectinload(SubscriptionPlan.items))
        )
        plan = plan_result.scalar_one_or_none()
        if not plan:
            raise ValueError("Plano não encontrado ou inativo")

        est_result = await self.db.execute(
            select(Establishment).where(Establishment.id == plan.establishment_id)
        )
        establishment = est_result.scalar_one_or_none()
        if not establishment or establishment.status != EstablishmentStatus.active:
            raise ValueError("Estabelecimento indisponível para assinatura")

        existing = await self.db.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.plan_id == plan_id,
                Subscription.status == SubscriptionStatus.active,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Você já possui uma assinatura ativa neste plano")

        now = datetime.now(UTC)
        period_end = now + timedelta(days=30)

        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            establishment_id=plan.establishment_id,
            status=SubscriptionStatus.active,
            current_period_start=now,
            current_period_end=period_end,
        )
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)

        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.id == subscription.id)
            .options(selectinload(Subscription.plan))
        )
        return result.scalar_one()

    async def cancel(self, subscription_id: UUID, user_id: UUID) -> Subscription:
        sub = await self.get_for_user(subscription_id, user_id)
        if not sub:
            raise ValueError("Assinatura não encontrada")
        if sub.status != SubscriptionStatus.active:
            raise ValueError("Assinatura já está cancelada ou expirada")

        sub.status = SubscriptionStatus.cancelled
        sub.cancelled_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(sub)
        return sub

    def _month_start(self, dt: datetime) -> date:
        return date(dt.year, dt.month, 1)

    async def build_usage_summary(self, subscription: Subscription) -> SubscriptionUsageSummary:
        plan_result = await self.db.execute(
            select(SubscriptionPlan)
            .where(SubscriptionPlan.id == subscription.plan_id)
            .options(selectinload(SubscriptionPlan.items))
        )
        plan = plan_result.scalar_one()
        month_start = self._month_start(subscription.current_period_start)

        usage_result = await self.db.execute(
            select(SubscriptionUsage).where(
                SubscriptionUsage.subscription_id == subscription.id,
                SubscriptionUsage.month_start == month_start,
            )
        )
        usage_rows = {u.plan_item_id: u for u in usage_result.scalars().all()}

        items: list[SubscriptionPlanItemUsage] = []
        for item in plan.items:
            row = usage_rows.get(item.id)
            used = row.uses_this_month if row else 0
            items.append(
                SubscriptionPlanItemUsage(
                    plan_item_id=item.id,
                    service_id=item.service_id,
                    bundle_id=item.bundle_id,
                    quantity_per_month=item.quantity_per_month,
                    uses_this_month=used,
                    remaining=max(0, item.quantity_per_month - used),
                )
            )

        return SubscriptionUsageSummary(
            items=items,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
        )

    async def find_active_for_establishment(
        self, user_id: UUID, establishment_id: UUID
    ) -> Subscription | None:
        result = await self.db.execute(
            select(Subscription)
            .where(
                Subscription.user_id == user_id,
                Subscription.establishment_id == establishment_id,
                Subscription.status == SubscriptionStatus.active,
                Subscription.current_period_end > datetime.now(UTC),
            )
            .options(
                selectinload(Subscription.plan).selectinload(SubscriptionPlan.items),
            )
        )
        return result.scalar_one_or_none()

    async def consume_credit(
        self,
        subscription: Subscription,
        service_id: UUID | None = None,
    ) -> tuple[SubscriptionPlanItem, SubscriptionUsage]:
        """Consume one monthly credit. Raises ValueError if limit reached."""
        plan = subscription.plan
        if not plan:
            plan_result = await self.db.execute(
                select(SubscriptionPlan)
                .where(SubscriptionPlan.id == subscription.plan_id)
                .options(selectinload(SubscriptionPlan.items))
            )
            plan = plan_result.scalar_one()

        matching_item: SubscriptionPlanItem | None = None
        for item in plan.items:
            if service_id and item.service_id == service_id:
                matching_item = item
                break
        if not matching_item and plan.items:
            matching_item = plan.items[0]

        if not matching_item:
            raise ValueError("Plano de assinatura sem itens configurados")

        month_start = self._month_start(datetime.now(UTC))
        usage_result = await self.db.execute(
            select(SubscriptionUsage).where(
                SubscriptionUsage.subscription_id == subscription.id,
                SubscriptionUsage.plan_item_id == matching_item.id,
                SubscriptionUsage.month_start == month_start,
            )
        )
        usage = usage_result.scalar_one_or_none()

        if usage and usage.uses_this_month >= matching_item.quantity_per_month:
            raise ValueError("Limite mensal da assinatura atingido")

        if usage and usage.last_use_date == date.today():
            raise ValueError("Limite diário de check-in atingido (1 por dia)")

        if not usage:
            usage = SubscriptionUsage(
                subscription_id=subscription.id,
                plan_item_id=matching_item.id,
                month_start=month_start,
                uses_this_month=0,
            )
            self.db.add(usage)

        usage.uses_this_month += 1
        usage.last_use_date = date.today()
        await self.db.flush()
        return matching_item, usage
