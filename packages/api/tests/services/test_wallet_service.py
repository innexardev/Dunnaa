"""Wallet service unit tests."""

from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.user import User
from app.services.wallet_service import WalletService


@pytest.mark.asyncio
async def test_wallet_create_and_deposit(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        user = User(phone="+5511777000001", referral_code="WALLET01")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        service = WalletService(session)
        wallet = await service.get_wallet(user.id)
        assert float(wallet.balance) == 0

        updated = await service.add_balance(user.id, 50.0, "Crédito teste")
        assert float(updated.balance) == 50.0


@pytest.mark.asyncio
async def test_wallet_withdraw_insufficient(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        user = User(phone="+5511777000002", referral_code="WALLET02")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        service = WalletService(session)
        with pytest.raises(ValueError, match="Saldo insuficiente"):
            await service.withdraw_balance(user.id, 10.0, "Saque teste")
