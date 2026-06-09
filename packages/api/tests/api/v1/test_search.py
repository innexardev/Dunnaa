"""Search history API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_history_crud(client: AsyncClient, auth_headers: dict, establishment_id: str):
    create = await client.post(
        "/api/v1/users/me/search-history",
        json={"query": "barbearia centro", "establishment_clicked_id": establishment_id},
        headers=auth_headers,
    )
    assert create.status_code == 201
    entry_id = create.json()["id"]

    listed = await client.get("/api/v1/users/me/search-history", headers=auth_headers)
    assert listed.status_code == 200
    assert len(listed.json()) >= 1

    deleted = await client.delete(
        f"/api/v1/users/me/search-history/{entry_id}",
        headers=auth_headers,
    )
    assert deleted.status_code == 204

    cleared = await client.delete("/api/v1/users/me/search-history", headers=auth_headers)
    assert cleared.status_code == 204


@pytest.mark.asyncio
async def test_search_history_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/users/me/search-history")
    assert resp.status_code == 401
