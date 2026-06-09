"""Admin settings API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_settings_requires_admin(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/admin/settings", headers=auth_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_settings_list(client: AsyncClient, admin_headers: dict):
    resp = await client.get("/api/v1/admin/settings", headers=admin_headers)
    assert resp.status_code == 200
    assert "items" in resp.json()


@pytest.mark.asyncio
async def test_admin_settings_seed_defaults(client: AsyncClient, admin_headers: dict):
    resp = await client.post("/api/v1/admin/settings/seed-defaults", headers=admin_headers)
    assert resp.status_code == 200
    assert "Seeded" in resp.json()["message"]


@pytest.mark.asyncio
async def test_admin_settings_crud(client: AsyncClient, admin_headers: dict):
    create = await client.post(
        "/api/v1/admin/settings",
        json={
            "key": "test.setting",
            "value": "hello",
            "description": "Test setting",
            "category": "test",
        },
        headers=admin_headers,
    )
    assert create.status_code == 201

    get = await client.get("/api/v1/admin/settings/test.setting", headers=admin_headers)
    assert get.status_code == 200
    assert get.json()["value"] == "hello"

    update = await client.put(
        "/api/v1/admin/settings/test.setting",
        json={"value": "world"},
        headers=admin_headers,
    )
    assert update.status_code == 200
    assert update.json()["value"] == "world"

    delete = await client.delete("/api/v1/admin/settings/test.setting", headers=admin_headers)
    assert delete.status_code == 204
