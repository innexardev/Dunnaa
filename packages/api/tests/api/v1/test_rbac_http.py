"""HTTP RBAC integration tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_establishment_appointments_forbidden_for_customer(
    client: AsyncClient,
    auth_headers_second_user: dict,
    establishment_id: str,
):
    resp = await client.get(
        f"/api/v1/appointments/establishments/{establishment_id}",
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_establishment_appointments_allowed_for_owner(
    client: AsyncClient,
    auth_headers: dict,
    establishment_id: str,
):
    resp = await client.get(
        f"/api/v1/appointments/establishments/{establishment_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_payouts_forbidden_for_customer(
    client: AsyncClient,
    auth_headers_second_user: dict,
    establishment_id: str,
):
    resp = await client.get(
        f"/api/v1/payouts/establishments/{establishment_id}/balance",
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_analytics_forbidden_for_customer(
    client: AsyncClient,
    auth_headers_second_user: dict,
    establishment_id: str,
):
    resp = await client.get(
        f"/api/v1/analytics/establishments/{establishment_id}/dashboard",
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 403
