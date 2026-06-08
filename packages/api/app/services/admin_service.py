"""Platform admin business logic."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.establishment import Establishment, EstablishmentStatus
from app.models.payment import Payment, PaymentStatus
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User, UserRole


class AdminService:
    """Admin dashboard and platform management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self) -> dict[str, Any]:
        """Platform-wide metrics for admin dashboard (A01-A05)."""
        now = datetime.now(UTC)
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)

        total_establishments = (
            await self.db.execute(select(func.count(Establishment.id)))
        ).scalar() or 0

        active_establishments = (
            await self.db.execute(
                select(func.count(Establishment.id)).where(
                    Establishment.status == EstablishmentStatus.active
                )
            )
        ).scalar() or 0

        total_users = (await self.db.execute(select(func.count(User.id)))).scalar() or 0

        active_subscriptions = (
            await self.db.execute(
                select(func.count(Subscription.id)).where(
                    Subscription.status == SubscriptionStatus.active
                )
            )
        ).scalar() or 0

        platform_revenue = (
            await self.db.execute(
                select(func.coalesce(func.sum(Payment.platform_fee), 0)).where(
                    Payment.status == PaymentStatus.succeeded
                )
            )
        ).scalar() or 0

        revenue_30d = (
            await self.db.execute(
                select(func.coalesce(func.sum(Payment.platform_fee), 0)).where(
                    Payment.status == PaymentStatus.succeeded,
                    Payment.created_at >= thirty_days_ago,
                )
            )
        ).scalar() or 0

        revenue_prev_30d = (
            await self.db.execute(
                select(func.coalesce(func.sum(Payment.platform_fee), 0)).where(
                    Payment.status == PaymentStatus.succeeded,
                    Payment.created_at >= sixty_days_ago,
                    Payment.created_at < thirty_days_ago,
                )
            )
        ).scalar() or 0

        users_30d = (
            await self.db.execute(
                select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
            )
        ).scalar() or 0

        establishments_30d = (
            await self.db.execute(
                select(func.count(Establishment.id)).where(
                    Establishment.created_at >= thirty_days_ago
                )
            )
        ).scalar() or 0

        growth_pct = 0.0
        if revenue_prev_30d and float(revenue_prev_30d) > 0:
            growth_pct = round(
                (float(revenue_30d) - float(revenue_prev_30d))
                / float(revenue_prev_30d)
                * 100,
                2,
            )

        return {
            "total_establishments": total_establishments,
            "active_establishments": active_establishments,
            "total_users": total_users,
            "active_subscriptions": active_subscriptions,
            "platform_revenue_total": float(platform_revenue),
            "platform_revenue_30d": float(revenue_30d),
            "revenue_growth_percent_30d": growth_pct,
            "new_users_30d": users_30d,
            "new_establishments_30d": establishments_30d,
            "generated_at": now.isoformat(),
        }

    async def list_establishments(
        self, *, skip: int = 0, limit: int = 50, status: EstablishmentStatus | None = None
    ) -> tuple[list[Establishment], int]:
        query = select(Establishment).order_by(Establishment.created_at.desc())
        count_q = select(func.count(Establishment.id))
        if status:
            query = query.where(Establishment.status == status)
            count_q = count_q.where(Establishment.status == status)
        total = (await self.db.execute(count_q)).scalar() or 0
        result = await self.db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def get_establishment(self, establishment_id: UUID) -> Establishment | None:
        return await self.db.get(Establishment, establishment_id)

    async def list_users(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        role: UserRole | None = None,
        search: str | None = None,
    ) -> tuple[list[User], int]:
        query = select(User).order_by(User.created_at.desc())
        count_q = select(func.count(User.id))
        if role:
            query = query.where(User.role == role)
            count_q = count_q.where(User.role == role)
        if search:
            pattern = f"%{search}%"
            filt = (User.name.ilike(pattern)) | (User.phone.ilike(pattern))
            query = query.where(filt)
            count_q = count_q.where(filt)
        total = (await self.db.execute(count_q)).scalar() or 0
        result = await self.db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def get_user(self, user_id: UUID) -> User | None:
        return await self.db.get(User, user_id)

    async def list_subscriptions(
        self, *, skip: int = 0, limit: int = 50, status: SubscriptionStatus | None = None
    ) -> tuple[list[Subscription], int]:
        query = select(Subscription).order_by(Subscription.created_at.desc())
        count_q = select(func.count(Subscription.id))
        if status:
            query = query.where(Subscription.status == status)
            count_q = count_q.where(Subscription.status == status)
        total = (await self.db.execute(count_q)).scalar() or 0
        result = await self.db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def list_payments(
        self, *, skip: int = 0, limit: int = 50, status: PaymentStatus | None = None
    ) -> tuple[list[Payment], int]:
        query = select(Payment).order_by(Payment.created_at.desc())
        count_q = select(func.count(Payment.id))
        if status:
            query = query.where(Payment.status == status)
            count_q = count_q.where(Payment.status == status)
        total = (await self.db.execute(count_q)).scalar() or 0
        result = await self.db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all()), total
