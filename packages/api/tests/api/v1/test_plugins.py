"""Plugin API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_install_and_list_plugins(
    client: AsyncClient, auth_headers: dict, establishment_id: str
):
    resp = await client.post(
        f"/api/v1/establishments/{establishment_id}/plugins",
        json={"plugin_type": "analytics", "config": {"tier": "pro"}},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["plugin_type"] == "analytics"
    assert resp.json()["active"] is True

    listed = await client.get(
        f"/api/v1/establishments/{establishment_id}/plugins",
        headers=auth_headers,
    )
    assert listed.status_code == 200
    assert len(listed.json()) >= 1


@pytest.mark.asyncio
async def test_plugins_forbidden_for_customer(
    client: AsyncClient, auth_headers_second_user: dict, establishment_id: str
):
    resp = await client.get(
        f"/api/v1/establishments/{establishment_id}/plugins",
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_deactivate_plugin(client: AsyncClient, auth_headers: dict, establishment_id: str):
    create = await client.post(
        f"/api/v1/establishments/{establishment_id}/plugins",
        json={"plugin_type": "ads", "config": {}},
        headers=auth_headers,
    )
    plugin_id = create.json()["id"]

    delete = await client.delete(
        f"/api/v1/establishments/{establishment_id}/plugins/{plugin_id}",
        headers=auth_headers,
    )
    assert delete.status_code == 204
