"""Tips API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_tip(
    client: AsyncClient,
    auth_headers_second_user: dict,
    staff_id: str,
):
    resp = await client.post(
        "/api/v1/tips/",
        json={"amount": 15.0, "staff_id": staff_id},
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert float(data["amount"]) == 15.0
    assert data["staff_id"] == staff_id


@pytest.mark.asyncio
async def test_list_my_tips(
    client: AsyncClient,
    auth_headers_second_user: dict,
    staff_id: str,
):
    await client.post(
        "/api/v1/tips/",
        json={"amount": 10.0, "staff_id": staff_id},
        headers=auth_headers_second_user,
    )
    resp = await client.get("/api/v1/tips/me", headers=auth_headers_second_user)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_create_tip_invalid_staff(client: AsyncClient, auth_headers: dict):
    from uuid import uuid4

    resp = await client.post(
        "/api/v1/tips/",
        json={"amount": 5.0, "staff_id": str(uuid4())},
        headers=auth_headers,
    )
    assert resp.status_code == 404
