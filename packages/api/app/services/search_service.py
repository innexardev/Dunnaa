"""Search history service."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import SearchHistory


class SearchService:
    """User search history."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_user(self, user_id: UUID, limit: int = 20) -> list[SearchHistory]:
        result = await self.db.execute(
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def record(
        self,
        user_id: UUID,
        query: str,
        establishment_clicked_id: UUID | None = None,
    ) -> SearchHistory:
        entry = SearchHistory(
            user_id=user_id,
            query=query.strip(),
            establishment_clicked_id=establishment_clicked_id,
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def delete_entry(self, user_id: UUID, entry_id: UUID) -> bool:
        result = await self.db.execute(
            delete(SearchHistory).where(
                SearchHistory.id == entry_id,
                SearchHistory.user_id == user_id,
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    async def clear(self, user_id: UUID) -> int:
        result = await self.db.execute(
            delete(SearchHistory).where(SearchHistory.user_id == user_id)
        )
        await self.db.commit()
        return result.rowcount or 0
