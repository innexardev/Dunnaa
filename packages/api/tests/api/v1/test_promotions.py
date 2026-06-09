"""Promotion API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_promotions_public(client: AsyncClient, establishment_id: str):
    resp = await client.get(
        f"/api/v1/establishments/{establishment_id}/promotions"
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_promotion_owner(
    client: AsyncClient, auth_headers: dict, establishment_id: str, service_id: str
):
    resp = await client.post(
        f"/api/v1/establishments/{establishment_id}/promotions",
        json={
            "title": "Corte 20% off",
            "discount_type": "percent",
            "discount_value": 20,
            "service_id": service_id,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Corte 20% off"
    assert data["active"] is True


@pytest.mark.asyncio
async def test_create_promotion_forbidden(
    client: AsyncClient, auth_headers_second_user: dict, establishment_id: str
):
    resp = await client.post(
        f"/api/v1/establishments/{establishment_id}/promotions",
        json={"title": "Hack", "discount_type": "fixed", "discount_value": 5},
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_update_and_delete_promotion(
    client: AsyncClient, auth_headers: dict, establishment_id: str
):
    create = await client.post(
        f"/api/v1/establishments/{establishment_id}/promotions",
        json={"title": "Promo", "discount_type": "fixed", "discount_value": 10},
        headers=auth_headers,
    )
    promo_id = create.json()["id"]

    update = await client.patch(
        f"/api/v1/establishments/{establishment_id}/promotions/{promo_id}",
        json={"title": "Promo Atualizada"},
        headers=auth_headers,
    )
    assert update.status_code == 200
    assert update.json()["title"] == "Promo Atualizada"

    delete = await client.delete(
        f"/api/v1/establishments/{establishment_id}/promotions/{promo_id}",
        headers=auth_headers,
    )
    assert delete.status_code == 204

    listed = await client.get(
        f"/api/v1/establishments/{establishment_id}/promotions"
    )
    assert listed.json() == []
