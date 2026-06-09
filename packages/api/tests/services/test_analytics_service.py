"""Analytics service unit tests."""

from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.analytics_service import AnalyticsService


@pytest.mark.asyncio
async def test_dashboard_empty(db_engine, establishment_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    est_id = UUID(str(establishment_id))
    async with Session() as session:
        from datetime import date, timedelta

        service = AnalyticsService(session)
        end = date.today()
        start = end - timedelta(days=30)
        data = await service.get_establishment_dashboard(est_id, start, end)
        assert data["total_revenue"] == 0
        assert data["total_appointments"] == 0
        assert data["no_show_rate"] == 0
