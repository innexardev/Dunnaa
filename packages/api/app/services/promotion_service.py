"""Promotion service."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.promotion import Promotion


class PromotionService:
    """Promotion CRUD and listing."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_establishment(
        self,
        establishment_id: UUID,
        active_only: bool = True,
        on_date: date | None = None,
    ) -> list[Promotion]:
        """List promotions for an establishment."""
        query = select(Promotion).where(Promotion.establishment_id == establishment_id)

        if active_only:
            query = query.where(Promotion.active == True)
            ref = on_date or date.today()
            query = query.where(
                or_(Promotion.start_date.is_(None), Promotion.start_date <= ref),
                or_(Promotion.end_date.is_(None), Promotion.end_date >= ref),
            )

        query = query.order_by(Promotion.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get(self, establishment_id: UUID, promotion_id: UUID) -> Promotion | None:
        result = await self.db.execute(
            select(Promotion).where(
                Promotion.id == promotion_id,
                Promotion.establishment_id == establishment_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        establishment_id: UUID,
        *,
        title: str,
        description: str | None = None,
        discount_type: str | None = None,
        discount_value: Decimal | float | None = None,
        service_id: UUID | None = None,
        bundle_id: UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Promotion:
        promotion = Promotion(
            establishment_id=establishment_id,
            title=title,
            description=description,
            discount_type=discount_type,
            discount_value=Decimal(str(discount_value)) if discount_value is not None else None,
            service_id=service_id,
            bundle_id=bundle_id,
            start_date=start_date,
            end_date=end_date,
            active=True,
        )
        self.db.add(promotion)
        await self.db.commit()
        await self.db.refresh(promotion)
        return promotion

    async def update(self, promotion: Promotion, **fields) -> Promotion:
        for key, value in fields.items():
            if value is not None and hasattr(promotion, key):
                if key == "discount_value":
                    value = Decimal(str(value))
                setattr(promotion, key, value)
        await self.db.commit()
        await self.db.refresh(promotion)
        return promotion

    async def deactivate(self, promotion: Promotion) -> None:
        promotion.active = False
        await self.db.commit()
