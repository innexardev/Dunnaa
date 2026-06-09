"""Referral API tests."""

import pytest
from httpx import AsyncClient


async def _signup(client: AsyncClient, phone: str, referral_code: str | None = None) -> dict:
    resp = await client.post("/api/v1/auth/send-code", json={"phone": phone})
    code = resp.json()["message"].split(": ")[1].strip()
    payload: dict = {"phone": phone, "code": code}
    if referral_code:
        payload["referral_code"] = referral_code
    resp = await client.post("/api/v1/auth/verify", json=payload)
    token = resp.json()["tokens"]["access_token"]
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "user": resp.json()["user"],
    }


@pytest.mark.asyncio
async def test_referral_flow(client: AsyncClient):
    referrer = await _signup(client, "+5511911111111")
    ref_code = referrer["user"]["referral_code"]
    assert ref_code

    referred = await _signup(client, "+5511922222222", referral_code=ref_code)

    resp = await client.get("/api/v1/referrals/me", headers=referrer["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["stats"]["total_referrals"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["reward_claimed"] is False

    referral_id = data["items"][0]["id"]
    claim = await client.post(
        f"/api/v1/referrals/{referral_id}/claim",
        headers=referrer["headers"],
    )
    assert claim.status_code == 200
    assert claim.json()["reward_claimed"] is True

    # Second claim fails
    claim2 = await client.post(
        f"/api/v1/referrals/{referral_id}/claim",
        headers=referrer["headers"],
    )
    assert claim2.status_code == 400


@pytest.mark.asyncio
async def test_referrals_empty_for_new_user(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/referrals/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["stats"]["total_referrals"] == 0
