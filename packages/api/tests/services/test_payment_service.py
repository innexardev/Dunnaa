"""Payment service unit tests."""

from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.payment import Payment, PaymentPurpose, PaymentStatus
from app.services.payment_service import PaymentService


@pytest.mark.asyncio
async def test_list_payments_empty(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        service = PaymentService(session)
        result = await service.list_by_user(uuid4())
        assert result == []


@pytest.mark.asyncio
async def test_handle_webhook_succeeds(db_engine, establishment_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    provider_id = f"mp_svc_{uuid4().hex[:8]}"
    est_id = UUID(str(establishment_id))

    async with Session() as session:
        from app.models.user import User
        from sqlalchemy import select

        user = (await session.execute(select(User).limit(1))).scalar_one()
        payment = Payment(
            user_id=user.id,
            establishment_id=est_id,
            purpose=PaymentPurpose.single,
            amount=80.0,
            platform_fee=4.0,
            gateway_fee=2.4,
            net_amount=73.6,
            status=PaymentStatus.pending,
            provider="mercadopago",
            provider_payment_id=provider_id,
        )
        session.add(payment)
        await session.commit()

        service = PaymentService(session)
        await service.handle_webhook(
            "mercadopago",
            {
                "action": "payment.updated",
                "data": {"id": provider_id, "status": "approved"},
            },
        )

        refreshed = await service.list_by_establishment(est_id)
        assert refreshed[0].status == PaymentStatus.succeeded


@pytest.mark.asyncio
async def test_handle_webhook_idempotent(db_engine, establishment_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    provider_id = f"mp_idem_{uuid4().hex[:8]}"
    est_id = UUID(str(establishment_id))

    async with Session() as session:
        from app.models.user import User
        from sqlalchemy import select

        user = (await session.execute(select(User).limit(1))).scalar_one()
        payment = Payment(
            user_id=user.id,
            establishment_id=est_id,
            purpose=PaymentPurpose.single,
            amount=40.0,
            platform_fee=2.0,
            gateway_fee=1.2,
            net_amount=36.8,
            status=PaymentStatus.succeeded,
            provider="mercadopago",
            provider_payment_id=provider_id,
        )
        session.add(payment)
        await session.commit()

        service = PaymentService(session)
        await service.handle_webhook(
            "mercadopago",
            {
                "action": "payment.updated",
                "data": {"id": provider_id, "status": "approved"},
            },
        )
        payments = await service.list_by_establishment(est_id)
        assert payments[0].status == PaymentStatus.succeeded
