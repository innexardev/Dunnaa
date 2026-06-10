"""Tip service unit tests."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.payment import PaymentStatus
from app.models.user import User
from app.services.tip_service import TipService


@pytest.mark.asyncio
async def test_create_direct_tip(db_engine, establishment_id, staff_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        from uuid import UUID

        user = User(phone="+5511666000001", referral_code="TIP00001")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        service = TipService(session)
        tip = await service.create_direct_tip(
            user.id,
            UUID(str(staff_id)),
            25.0,
        )
        assert tip.status == PaymentStatus.succeeded
        assert float(tip.amount) == 25.0


@pytest.mark.asyncio
async def test_create_payment_intent(db_engine, establishment_id, staff_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        from uuid import UUID

        user = User(phone="+5511666000002", referral_code="TIP00002")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        service = TipService(session)
        mock_provider = AsyncMock()
        mock_provider.create_intent = AsyncMock(
            return_value={
                "provider_payment_id": "pi_test_123",
                "client_secret": "sec_test",
                "provider": "stripe",
            }
        )

        with patch("app.services.tip_service.settings.STRIPE_SECRET_KEY", "sk_test"):
            with patch(
                "app.services.tip_service.PaymentProviderFactory.get_provider",
                return_value=mock_provider,
            ):
                result = await service.create_payment_intent(
                    user.id,
                    UUID(str(staff_id)),
                    30.0,
                )

        assert result["client_secret"] == "sec_test"
        assert result["provider_payment_id"] == "pi_test_123"


@pytest.mark.asyncio
async def test_confirm_from_webhook(db_engine, establishment_id, staff_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        from uuid import UUID

        from app.models.payment import Tip

        user = User(phone="+5511666000003", referral_code="TIP00003")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        tip = Tip(
            user_id=user.id,
            staff_id=UUID(str(staff_id)),
            establishment_id=UUID(str(establishment_id)),
            amount=15.0,
            status=PaymentStatus.pending,
            provider_payment_id="pi_tip_999",
        )
        session.add(tip)
        await session.commit()

        service = TipService(session)
        assert await service.confirm_from_webhook("pi_tip_999") is True

        await session.refresh(tip)
        assert tip.status == PaymentStatus.succeeded


@pytest.mark.asyncio
async def test_invalid_staff(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        user = User(phone="+5511666000004", referral_code="TIP00004")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        service = TipService(session)
        with pytest.raises(ValueError, match="Profissional não encontrado"):
            await service.create_direct_tip(user.id, uuid4(), 10.0)
