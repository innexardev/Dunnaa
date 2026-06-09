"""Establishment service unit tests."""

from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.establishment import EstablishmentStatus
from app.schemas.establishment import EstablishmentCreate
from app.services.establishment_service import EstablishmentService


@pytest.mark.asyncio
async def test_establishment_create_and_list(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        from app.models.user import User

        owner = User(phone="+5511444000001", referral_code="EST00001")
        session.add(owner)
        await session.commit()
        await session.refresh(owner)

        service = EstablishmentService(session)
        data = EstablishmentCreate(
            name="Salão Teste",
            category="salon",
            address="Rua A, 1",
            city="São Paulo",
            state="SP",
            phone="+551133333333",
            business_hours={
                day: {"open": "09:00", "close": "18:00"}
                for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            },
        )
        est = await service.create(owner.id, data)
        assert est.slug
        assert est.status == EstablishmentStatus.pending

        fetched = await service.get(est.id)
        assert fetched is not None
        assert fetched.name == "Salão Teste"

        est.status = EstablishmentStatus.active
        await session.commit()

        listed = await service.list(q="Salão")
        assert listed.pagination.total >= 1


@pytest.mark.asyncio
async def test_establishment_slug_generation(db_engine):
    service = EstablishmentService(None)  # type: ignore[arg-type]
    slug = service._generate_slug("Barbearia do João!!!")
    assert slug == "barbearia-do-joao"
