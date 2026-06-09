"""Establishment payments API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_establishment_payments_empty(
    client: AsyncClient, auth_headers: dict, establishment_id: str
):
    resp = await client.get(
        f"/api/v1/payments/establishments/{establishment_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_establishment_payments_forbidden(
    client: AsyncClient, auth_headers_second_user: dict, establishment_id: str
):
    resp = await client.get(
        f"/api/v1/payments/establishments/{establishment_id}",
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 403
