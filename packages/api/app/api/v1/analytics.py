"""Analytics endpoints."""

from datetime import date, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DBSession, verify_establishment_owner
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/establishments/{establishment_id}/dashboard")
async def get_dashboard(
    establishment_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    end_date: date = Query(default_factory=lambda: date.today()),
):
    """Get dashboard analytics for an establishment."""
    await verify_establishment_owner(db, establishment_id, current_user)

    service = AnalyticsService(db)
    return await service.get_establishment_dashboard(establishment_id, start_date, end_date)
