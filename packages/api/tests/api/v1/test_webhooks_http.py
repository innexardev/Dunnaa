"""HTTP webhook integration tests."""

from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.payment import Payment, PaymentPurpose, PaymentStatus
from app.services.payment_service import PaymentService


@pytest.mark.asyncio
async def test_mercadopago_webhook_http(
    client: AsyncClient, db_engine, establishment_id, auth_headers
):
    """Mercado Pago webhook marks pending payment as succeeded."""
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    payment_id = f"mp_test_{uuid4().hex[:8]}"

    async with Session() as session:
        from app.models.user import User
        from sqlalchemy import select

        user = (await session.execute(select(User).limit(1))).scalar_one()
        payment = Payment(
            user_id=user.id,
            establishment_id=UUID(str(establishment_id)),
            purpose=PaymentPurpose.single,
            amount=50.0,
            platform_fee=2.5,
            gateway_fee=1.5,
            net_amount=46.0,
            status=PaymentStatus.pending,
            provider="mercadopago",
            provider_payment_id=payment_id,
        )
        session.add(payment)
        await session.commit()

    payload = {
        "action": "payment.updated",
        "data": {"id": payment_id, "status": "approved"},
        "metadata": {},
    }
    resp = await client.post("/api/v1/payments/webhooks/mercadopago", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

    async with Session() as session:
        service = PaymentService(session)
        payments = await service.list_by_establishment(UUID(str(establishment_id)))
        mp_payment = next(p for p in payments if p.provider_payment_id == payment_id)
        assert mp_payment.status == PaymentStatus.succeeded


@pytest.mark.asyncio
async def test_mercadopago_webhook_idempotent(client: AsyncClient, db_engine, establishment_id):
    """Duplicate webhook does not fail."""
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    payment_id = f"mp_dup_{uuid4().hex[:8]}"

    async with Session() as session:
        from app.models.user import User
        from sqlalchemy import select

        user = (await session.execute(select(User).limit(1))).scalar_one()
        payment = Payment(
            user_id=user.id,
            establishment_id=UUID(str(establishment_id)),
            purpose=PaymentPurpose.single,
            amount=30.0,
            platform_fee=1.5,
            gateway_fee=0.9,
            net_amount=27.6,
            status=PaymentStatus.succeeded,
            provider="mercadopago",
            provider_payment_id=payment_id,
        )
        session.add(payment)
        await session.commit()

    payload = {
        "action": "payment.updated",
        "data": {"id": payment_id, "status": "approved"},
    }
    resp = await client.post("/api/v1/payments/webhooks/mercadopago", json=payload)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_stripe_webhook_invalid_signature(client: AsyncClient):
    resp = await client.post(
        "/api/v1/payments/webhooks/stripe",
        content=b"{}",
        headers={"stripe-signature": "invalid"},
    )
    assert resp.status_code == 400
