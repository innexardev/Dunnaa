"""Settings service unit tests."""

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.settings_service import SettingsService


@pytest.mark.asyncio
async def test_settings_set_and_get(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        service = SettingsService(session)
        await service.set("test.key", "value123", description="Test")
        value = await service.get("test.key")
        assert value == "value123"
        assert await service.get_bool("test.key") is False


@pytest.mark.asyncio
async def test_settings_seed_defaults(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        service = SettingsService(session)
        count = await service.seed_defaults()
        assert count >= 1
