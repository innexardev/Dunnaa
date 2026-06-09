"""Payout service unit tests."""

from uuid import UUID, uuid4, uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.payment import Payment, PaymentPurpose, PaymentStatus
from app.services.payout_service import PayoutService


@pytest.mark.asyncio
async def test_withdrawable_balance(db_engine, establishment_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        payment = Payment(
            establishment_id=UUID(str(establishment_id)),
            user_id=uuid4(),
            amount=100.0,
            net_amount=90.0,
            platform_fee=10.0,
            status=PaymentStatus.succeeded,
            purpose=PaymentPurpose.single,
        )
        session.add(payment)
        await session.commit()

        service = PayoutService(session)
        balance = await service.get_withdrawable_balance(UUID(str(establishment_id)))
        assert balance == 90.0


@pytest.mark.asyncio
async def test_request_payout_minimum(db_engine, establishment_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        service = PayoutService(session)
        with pytest.raises(ValueError, match="mínimo"):
            await service.request_payout(UUID(str(establishment_id)), 10.0)
