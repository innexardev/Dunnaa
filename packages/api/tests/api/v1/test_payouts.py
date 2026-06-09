"""Payout API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_payout_balance_requires_auth(client: AsyncClient, establishment_id: str):
    resp = await client.get(f"/api/v1/payouts/establishments/{establishment_id}/balance")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_payout_balance_forbidden_for_other_user(
    client: AsyncClient, auth_headers_second_user: dict, establishment_id: str
):
    resp = await client.get(
        f"/api/v1/payouts/establishments/{establishment_id}/balance",
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_payout_balance_success(
    client: AsyncClient, auth_headers: dict, establishment_id: str
):
    resp = await client.get(
        f"/api/v1/payouts/establishments/{establishment_id}/balance",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert "available_balance" in resp.json()
    assert resp.json()["available_balance"] >= 0


@pytest.mark.asyncio
async def test_payout_request_minimum_amount(
    client: AsyncClient, auth_headers: dict, establishment_id: str
):
    resp = await client.post(
        f"/api/v1/payouts/establishments/{establishment_id}/requests",
        json={"amount": 10.0},
        headers=auth_headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_payout_history_empty(client: AsyncClient, auth_headers: dict, establishment_id: str):
    resp = await client.get(
        f"/api/v1/payouts/establishments/{establishment_id}/history",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json() == []
