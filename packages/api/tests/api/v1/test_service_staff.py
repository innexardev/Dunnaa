"""Service-staff assignment tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_service_staff_empty(
    client: AsyncClient, establishment_id: str, service_id: str
):
    resp = await client.get(
        f"/api/v1/establishments/{establishment_id}/services/{service_id}/staff"
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_assign_service_staff(
    client: AsyncClient,
    auth_headers: dict,
    establishment_id: str,
    service_id: str,
    staff_id: str,
):
    resp = await client.put(
        f"/api/v1/establishments/{establishment_id}/services/{service_id}/staff",
        json={"staff_ids": [staff_id]},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == staff_id

    listed = await client.get(
        f"/api/v1/establishments/{establishment_id}/services/{service_id}/staff"
    )
    assert len(listed.json()) == 1


@pytest.mark.asyncio
async def test_assign_service_staff_forbidden(
    client: AsyncClient,
    auth_headers_second_user: dict,
    establishment_id: str,
    service_id: str,
    staff_id: str,
):
    resp = await client.put(
        f"/api/v1/establishments/{establishment_id}/services/{service_id}/staff",
        json={"staff_ids": [staff_id]},
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_link_staff_to_user(
    client: AsyncClient,
    auth_headers: dict,
    auth_headers_second_user: dict,
    establishment_id: str,
    staff_id: str,
):
    resp = await client.post(
        f"/api/v1/establishments/{establishment_id}/staff/{staff_id}/link",
        json={"phone": "+5511977777777"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["user_id"] is not None
