"""Ad campaign API tests."""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_ad_campaign(
    client: AsyncClient, auth_headers: dict, establishment_id: str
):
    today = date.today()
    resp = await client.post(
        f"/api/v1/establishments/{establishment_id}/ad-campaigns",
        json={
            "name": "Boost Verão",
            "budget_daily": 25.0,
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=30)).isoformat(),
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["budget_daily"] == 25.0
    assert data["active"] is True
    campaign_id = data["id"]

    imp = await client.post(
        f"/api/v1/establishments/{establishment_id}/ad-campaigns/{campaign_id}/impressions"
    )
    assert imp.status_code == 204

    listed = await client.get(
        f"/api/v1/establishments/{establishment_id}/ad-campaigns",
        headers=auth_headers,
    )
    assert listed.status_code == 200
    assert listed.json()[0]["impressions"] >= 1


@pytest.mark.asyncio
async def test_ad_campaign_forbidden(
    client: AsyncClient, auth_headers_second_user: dict, establishment_id: str
):
    resp = await client.post(
        f"/api/v1/establishments/{establishment_id}/ad-campaigns",
        json={"budget_daily": 10.0, "start_date": date.today().isoformat()},
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 403
