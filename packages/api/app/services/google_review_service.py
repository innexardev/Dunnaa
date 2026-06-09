"""Google review sync service (mock Places API)."""

import secrets
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review


class GoogleReviewService:
    """Approve and sync reviews to Google (mock in dev)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def approve_for_google(self, review_id: UUID, establishment_id: UUID) -> Review | None:
        result = await self.db.execute(
            select(Review).where(
                Review.id == review_id,
                Review.establishment_id == establishment_id,
            )
        )
        review = result.scalar_one_or_none()
        if not review:
            return None
        if review.rating < 4:
            raise ValueError("Apenas avaliações com 4+ estrelas podem ir para o Google")
        review.approved_for_google = True
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def send_to_google(self, review_id: UUID, establishment_id: UUID) -> Review | None:
        result = await self.db.execute(
            select(Review).where(
                Review.id == review_id,
                Review.establishment_id == establishment_id,
            )
        )
        review = result.scalar_one_or_none()
        if not review:
            return None
        if not review.approved_for_google:
            raise ValueError("Avaliação precisa ser aprovada antes do envio")
        if review.sent_to_google:
            raise ValueError("Avaliação já enviada ao Google")

        # Mock Google Places API response
        review.sent_to_google = True
        review.google_review_id = f"g_{secrets.token_hex(8)}"
        review.sent_to_google_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def list_pending_sync(self, establishment_id: UUID) -> list[Review]:
        result = await self.db.execute(
            select(Review).where(
                Review.establishment_id == establishment_id,
                Review.approved_for_google == True,
                Review.sent_to_google == False,
            )
        )
        return list(result.scalars().all())
