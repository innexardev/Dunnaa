"""Admin API tests."""

from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.user import User, UserRole


@pytest.fixture
async def admin_headers(client: AsyncClient, db_engine) -> dict:
    phone = "+5511955555555"
    resp = await client.post("/api/v1/auth/send-code", json={"phone": phone})
    code = resp.json()["message"].split(": ")[1].strip()
    resp = await client.post("/api/v1/auth/verify", json={"phone": phone, "code": code})
    user_id = resp.json()["user"]["id"]
    refresh_token = resp.json()["tokens"]["refresh_token"]

    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        user = await session.get(User, UUID(user_id))
        user.role = UserRole.admin
        await session.commit()

    refresh = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    token = refresh.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_admin_dashboard_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/admin/dashboard")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_dashboard_forbidden_for_customer(
    client: AsyncClient, auth_headers: dict
):
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
