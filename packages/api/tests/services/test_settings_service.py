"""Settings service unit tests."""

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.settings_service import SettingsService, get_cached_bool, get_cached_setting


@pytest.fixture(autouse=True)
def clear_settings_cache():
    SettingsService.clear_cache()
    yield
    SettingsService.clear_cache()


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


@pytest.mark.asyncio
async def test_settings_types_cache_and_delete(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        service = SettingsService(session)
        await service.set("bool.key", "true", category="general")
        await service.set("float.key", "12.5", category="metrics")
        await service.set("float.key", "15.0", description="Updated")

        assert await service.get_bool("bool.key") is True
        assert await service.get_float("float.key") == 15.0
        assert await service.get_float("missing.key", default=3.5) == 3.5

        await service.load_cache()
        assert get_cached_setting("bool.key") == "true"
        assert get_cached_bool("bool.key") is True

        all_settings = await service.list_all(category="metrics")
        assert len(all_settings) == 1

        assert await service.delete("bool.key") is True
        assert await service.delete("missing.key") is False
        assert await service.get("bool.key") is None
