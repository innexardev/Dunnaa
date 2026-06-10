"""Review service unit tests."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.establishment import Establishment, EstablishmentCategory, EstablishmentStatus
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.services.review_service import ReviewService


async def _seed_establishment(session, owner: User) -> Establishment:
    est = Establishment(
        owner_id=owner.id,
        slug=f"review-test-{uuid4().hex[:8]}",
        name="Review Barbershop",
        category=EstablishmentCategory.barbershop,
        address="Rua A, 1",
        city="São Paulo",
        state="SP",
        phone="+551133333333",
        business_hours={
            day: {"open": "09:00", "close": "18:00"}
            for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        },
        status=EstablishmentStatus.active,
    )
    session.add(est)
    await session.commit()
    await session.refresh(est)
    return est


@pytest.mark.asyncio
async def test_review_crud_and_lists(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        user = User(phone="+5511777000001", referral_code="REV00001", name="Reviewer")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        establishment = await _seed_establishment(session, user)
        service = ReviewService(session)

        review = await service.create(
            user.id,
            ReviewCreate(
                establishment_id=establishment.id,
                rating=5,
                comment="Excelente atendimento",
            ),
        )
        assert review.rating == 5

        updated = await service.update(
            user.id,
            review.id,
            ReviewUpdate(rating=4, comment="Muito bom"),
        )
        assert updated is not None
        assert updated.rating == 4

        responded = await service.respond(review.id, "Obrigado pelo feedback!")
        assert responded is not None
        assert responded.owner_response == "Obrigado pelo feedback!"

        by_est, total = await service.list_by_establishment(establishment.id)
        assert total == 1
        assert len(by_est) == 1

        by_user = await service.list_by_user(user.id)
        assert len(by_user) == 1

        missing = await service.update(user.id, uuid4(), ReviewUpdate(rating=1))
        assert missing is None

        missing_response = await service.respond(uuid4(), "N/A")
        assert missing_response is None


@pytest.mark.asyncio
async def test_review_invalid_appointment(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        user = User(phone="+5511777000002", referral_code="REV00002")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        establishment = await _seed_establishment(session, user)
        service = ReviewService(session)

        with pytest.raises(ValueError, match="Agendamento não encontrado"):
            await service.create(
                user.id,
                ReviewCreate(
                    establishment_id=establishment.id,
                    appointment_id=uuid4(),
                    rating=3,
                ),
            )
