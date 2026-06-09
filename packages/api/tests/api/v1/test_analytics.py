"""Analytics API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analytics_dashboard_requires_auth(client: AsyncClient, establishment_id: str):
    resp = await client.get(
        f"/api/v1/analytics/establishments/{establishment_id}/dashboard"
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_analytics_dashboard_forbidden(
    client: AsyncClient, auth_headers_second_user: dict, establishment_id: str
):
    resp = await client.get(
        f"/api/v1/analytics/establishments/{establishment_id}/dashboard",
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_analytics_dashboard_success(
    client: AsyncClient, auth_headers: dict, establishment_id: str
):
    resp = await client.get(
        f"/api/v1/analytics/establishments/{establishment_id}/dashboard",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_revenue" in data
    assert "total_appointments" in data
    assert "staff_performance" in data
    assert "period" in data
