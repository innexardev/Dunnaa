"""Notification service unit tests."""

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.notification import NotificationType
from app.models.user import User
from app.services.notification_service import NotificationService


@pytest.mark.asyncio
async def test_notify_and_mark_read(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        user = User(phone="+5511555000001", referral_code="NOTIF001")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        service = NotificationService(session)
        await service.notify(
            user_id=user.id,
            title="Teste",
            message="Mensagem de teste",
            type=NotificationType.system,
        )

        items, total, unread = await service.list_user_notifications(user.id)
        assert total >= 1
        assert unread >= 1

        notif_id = items[0].id
        updated = await service.mark_read(user.id, notif_id)
        assert updated.is_read is True

        count = await service.mark_all_read(user.id)
        assert count >= 0

        _, _, unread_after = await service.list_user_notifications(user.id)
        assert unread_after == 0
