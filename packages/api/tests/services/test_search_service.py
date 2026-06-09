"""Search service unit tests."""

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.user import User
from app.services.search_service import SearchService


@pytest.mark.asyncio
async def test_search_history_record_and_clear(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        user = User(phone="+5511666000001", referral_code="SRCH0001")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        service = SearchService(session)
        entry = await service.record(user.id, "barbearia sp")
        assert entry.query == "barbearia sp"

        items = await service.list_for_user(user.id)
        assert len(items) == 1

        deleted = await service.delete_entry(user.id, entry.id)
        assert deleted is True

        await service.record(user.id, "salão")
        cleared = await service.clear(user.id)
        assert cleared >= 1
        assert await service.list_for_user(user.id) == []
