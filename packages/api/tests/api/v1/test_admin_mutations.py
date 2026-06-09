"""Admin mutation tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_patch_establishment(
    client: AsyncClient, admin_headers: dict, establishment_id: str
):
    resp = await client.patch(
        f"/api/v1/admin/establishments/{establishment_id}",
        json={"status": "active"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"


@pytest.mark.asyncio
async def test_admin_get_establishment(
    client: AsyncClient, admin_headers: dict, establishment_id: str
):
    resp = await client.get(
        f"/api/v1/admin/establishments/{establishment_id}",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == establishment_id


@pytest.mark.asyncio
async def test_admin_patch_user_role(
    client: AsyncClient, admin_headers: dict, auth_headers_second_user: dict
):
    me = await client.get("/api/v1/users/me", headers=auth_headers_second_user)
    user_id = me.json()["id"]

    resp = await client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={"role": "owner"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "owner"
