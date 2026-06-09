"""Google review sync API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_google_review_flow(
    client: AsyncClient,
    auth_headers: dict,
    auth_headers_second_user: dict,
    establishment_id: str,
):
    # Customer creates 5-star review
    create = await client.post(
        "/api/v1/reviews",
        json={
            "establishment_id": establishment_id,
            "rating": 5,
            "comment": "Excelente atendimento!",
        },
        headers=auth_headers_second_user,
    )
    assert create.status_code == 201
    review_id = create.json()["id"]

    # Owner approves for Google
    approve = await client.post(
        f"/api/v1/reviews/{review_id}/approve-google",
        headers=auth_headers,
    )
    assert approve.status_code == 200

    pending = await client.get(
        f"/api/v1/reviews/establishments/{establishment_id}/google-pending",
        headers=auth_headers,
    )
    assert pending.status_code == 200
    assert len(pending.json()) == 1

    # Send to Google
    send = await client.post(
        f"/api/v1/reviews/{review_id}/send-google",
        headers=auth_headers,
    )
    assert send.status_code == 200

    pending_after = await client.get(
        f"/api/v1/reviews/establishments/{establishment_id}/google-pending",
        headers=auth_headers,
    )
    assert pending_after.json() == []

    # Second send fails
    send2 = await client.post(
        f"/api/v1/reviews/{review_id}/send-google",
        headers=auth_headers,
    )
    assert send2.status_code == 400


@pytest.mark.asyncio
async def test_google_approve_low_rating_rejected(
    client: AsyncClient,
    auth_headers: dict,
    auth_headers_second_user: dict,
    establishment_id: str,
):
    create = await client.post(
        "/api/v1/reviews",
        json={"establishment_id": establishment_id, "rating": 2, "comment": "Ruim"},
        headers=auth_headers_second_user,
    )
    review_id = create.json()["id"]

    approve = await client.post(
        f"/api/v1/reviews/{review_id}/approve-google",
        headers=auth_headers,
    )
    assert approve.status_code == 400
