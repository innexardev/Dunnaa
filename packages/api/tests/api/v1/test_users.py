"""Users API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_and_update_profile(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/users/me", headers=auth_headers)
    assert resp.status_code == 200

    update = await client.patch(
        "/api/v1/users/me",
        json={"name": "Cliente Teste", "email": "cliente@test.com"},
        headers=auth_headers,
    )
    assert update.status_code == 200
    assert update.json()["name"] == "Cliente Teste"
    assert update.json()["email"] == "cliente@test.com"


@pytest.mark.asyncio
async def test_list_payments_and_wallet(client: AsyncClient, auth_headers: dict):
    wallet = await client.get("/api/v1/payments/wallet", headers=auth_headers)
    assert wallet.status_code == 200
    assert "balance" in wallet.json()

    txs = await client.get("/api/v1/payments/wallet/transactions", headers=auth_headers)
    assert txs.status_code == 200
    assert isinstance(txs.json(), list)

    payments = await client.get("/api/v1/payments", headers=auth_headers)
    assert payments.status_code == 200
