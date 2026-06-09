"""Google review service unit tests."""

from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.review import Review
from app.models.user import User
from app.services.google_review_service import GoogleReviewService


@pytest.mark.asyncio
async def test_google_review_approve_and_send(db_engine, establishment_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    est_id = UUID(str(establishment_id))
    async with Session() as session:
        user = User(phone="+5511333000001", referral_code="GREV0001")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        review = Review(
            user_id=user.id,
            establishment_id=est_id,
            rating=5,
            comment="Ótimo!",
        )
        session.add(review)
        await session.commit()
        await session.refresh(review)

        service = GoogleReviewService(session)
        approved = await service.approve_for_google(review.id, est_id)
        assert approved is not None
        assert approved.approved_for_google is True

        sent = await service.send_to_google(review.id, est_id)
        assert sent is not None
        assert sent.sent_to_google is True
        assert sent.google_review_id is not None
