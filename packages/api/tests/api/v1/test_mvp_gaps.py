"""MVP 1.0 gap tests — subscriptions, availability, search, check-in credits."""

from datetime import UTC, date, datetime, timedelta
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.establishment import Establishment, EstablishmentStatus
from app.models.user import User, UserRole


async def _activate_establishment(db_engine, establishment_id: str) -> None:
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        est = await session.get(Establishment, UUID(establishment_id))
        est.status = EstablishmentStatus.active
        await session.commit()


async def _create_plan(
    client: AsyncClient,
    auth_headers: dict,
    establishment_id: str,
    service_id: str,
) -> str:
    resp = await client.post(
        f"/api/v1/establishments/{establishment_id}/subscription-plans",
        json={
            "name": "Plano Mensal",
            "description": "2 cortes por mês",
            "price": 99.9,
            "items": [{"service_id": service_id, "quantity_per_month": 2}],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_search_establishments_by_name(
    client: AsyncClient, auth_headers: dict, establishment_id: str, db_engine
):
    await _activate_establishment(db_engine, establishment_id)
    resp = await client.get("/api/v1/establishments", params={"q": "Barbearia"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_search_history_crud(
    client: AsyncClient, auth_headers_second_user: dict
):
    resp = await client.post(
        "/api/v1/users/me/search-history",
        json={"query": "barbearia centro"},
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 201
    entry_id = resp.json()["id"]

    resp = await client.get(
        "/api/v1/users/me/search-history",
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    resp = await client.delete(
        f"/api/v1/users/me/search-history/{entry_id}",
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_availability_slots(
    client: AsyncClient,
    auth_headers: dict,
    establishment_id: str,
    service_id: str,
    staff_id: str,
    db_engine,
):
    await _activate_establishment(db_engine, establishment_id)
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    resp = await client.get(
        f"/api/v1/establishments/{establishment_id}/staff/{staff_id}/availability",
        params={"service_id": service_id, "date": tomorrow},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["staff_id"] == staff_id
    assert isinstance(data["slots"], list)
    assert len(data["slots"]) > 0


@pytest.mark.asyncio
async def test_customer_subscription_flow(
    client: AsyncClient,
    auth_headers: dict,
    auth_headers_second_user: dict,
    establishment_id: str,
    service_id: str,
    db_engine,
):
    await _activate_establishment(db_engine, establishment_id)
    plan_id = await _create_plan(client, auth_headers, establishment_id, service_id)

    resp = await client.post(
        "/api/v1/subscriptions",
        json={"plan_id": plan_id},
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 201
    sub_id = resp.json()["id"]
    assert resp.json()["usage"]["items"][0]["remaining"] == 2

    resp = await client.get("/api/v1/subscriptions", headers=auth_headers_second_user)
    assert resp.status_code == 200
    assert any(s["id"] == sub_id for s in resp.json())

    resp = await client.get(
        f"/api/v1/establishments/{establishment_id}/subscriptions",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    resp = await client.delete(
        f"/api/v1/subscriptions/{sub_id}",
        headers=auth_headers_second_user,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_checkin_consumes_subscription_credit(
    client: AsyncClient,
    auth_headers: dict,
    auth_headers_second_user: dict,
    establishment_id: str,
    service_id: str,
    staff_id: str,
    db_engine,
):
    await _activate_establishment(db_engine, establishment_id)
    plan_id = await _create_plan(client, auth_headers, establishment_id, service_id)

    await client.post(
        "/api/v1/subscriptions",
        json={"plan_id": plan_id},
        headers=auth_headers_second_user,
    )

    scheduled_at = datetime.now(UTC) + timedelta(hours=2)
    appt = await client.post(
        "/api/v1/appointments",
        json={
            "establishment_id": establishment_id,
            "service_id": service_id,
            "staff_id": staff_id,
            "scheduled_at": scheduled_at.isoformat(),
            "payment_type": "subscription",
        },
        headers=auth_headers_second_user,
    )
    assert appt.status_code == 201

    qr = await client.get(
        f"/api/v1/checkins/establishments/{establishment_id}/qr",
        headers=auth_headers,
    )
    assert qr.status_code == 200
    token = qr.json()["qr_token"]

    checkin = await client.post(
        "/api/v1/checkins",
        json={"qr_token": token},
        headers=auth_headers_second_user,
    )
    assert checkin.status_code == 200
    data = checkin.json()
    assert data["success"] is True
    assert data.get("subscription_usage") is not None
    assert data["subscription_usage"]["items"][0]["uses_this_month"] == 1
