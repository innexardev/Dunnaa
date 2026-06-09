"""Admin API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_dashboard_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/admin/dashboard")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_dashboard_forbidden_for_customer(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/admin/dashboard", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_dashboard_success(client: AsyncClient, admin_headers: dict):
    response = await client.get("/api/v1/admin/dashboard", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_establishments" in data
    assert "total_users" in data
    assert "platform_revenue_total" in data


@pytest.mark.asyncio
async def test_admin_list_users(client: AsyncClient, admin_headers: dict):
    response = await client.get("/api/v1/admin/users", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_admin_list_establishments(
    client: AsyncClient, admin_headers: dict, establishment_id: str
):
    response = await client.get("/api/v1/admin/establishments", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1


@pytest.mark.asyncio
async def test_admin_audit_logs(client: AsyncClient, admin_headers: dict):
    response = await client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert response.status_code == 200
    assert "items" in response.json()
