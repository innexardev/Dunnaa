"""Audit service unit tests."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.audit_service import AuditService


@pytest.mark.asyncio
async def test_audit_log_and_list(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        service = AuditService(session)
        user_id = uuid4()
        entry = await service.log(
            action="establishment.create",
            resource_type="establishment",
            user_id=user_id,
            metadata={"name": "Test"},
        )
        assert entry.action == "establishment.create"

        logs, total = await service.list_logs(action="establishment.create")
        assert total >= 1
        assert logs[0].id == entry.id
