"""Queue service unit tests."""

from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.queue import QueueStatus
from app.schemas.queue import QueueEntryCreate
from app.services.queue_service import QueueService


@pytest.mark.asyncio
async def test_queue_join_sends_eta_notification(db_engine, establishment_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    est_id = UUID(str(establishment_id))

    async with Session() as session:
        from app.models.user import User
        from sqlalchemy import select

        user = (await session.execute(select(User).limit(1))).scalar_one()
        service = QueueService(session)

        with patch.object(
            service,
            "_notify_queue_join",
            new=AsyncMock(),
        ) as notify_mock:
            entry = await service.join_queue(
                user.id,
                QueueEntryCreate(establishment_id=est_id),
            )
            notify_mock.assert_awaited_once()
            assert entry.position == 1


@pytest.mark.asyncio
async def test_queue_join_and_list(db_engine, establishment_id, auth_headers):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    est_id = UUID(str(establishment_id))

    async with Session() as session:
        from app.models.user import User
        from sqlalchemy import select

        user = (await session.execute(select(User).limit(1))).scalar_one()
        service = QueueService(session)

        entry = await service.join_queue(
            user.id,
            QueueEntryCreate(establishment_id=est_id),
        )
        assert entry.status == QueueStatus.waiting

        entries = await service.list_by_establishment(est_id)
        assert len(entries) == 1

        user_entries = await service.list_by_user(user.id)
        assert len(user_entries) == 1


@pytest.mark.asyncio
async def test_queue_position(db_engine, establishment_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    est_id = UUID(str(establishment_id))

    async with Session() as session:
        from app.models.user import User
        from sqlalchemy import select

        user = (await session.execute(select(User).limit(1))).scalar_one()
        service = QueueService(session)

        await service.join_queue(user.id, QueueEntryCreate(establishment_id=est_id))
        position = await service.get_user_position(est_id, user.id)
        assert position is not None
        assert position.establishment_id == est_id
