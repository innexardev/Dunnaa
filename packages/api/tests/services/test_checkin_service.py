"""Check-in service unit tests."""

from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.checkin_service import CheckinService


@pytest.mark.asyncio
async def test_generate_qr_token(db_engine, establishment_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    est_id = UUID(str(establishment_id))
    async with Session() as session:
        service = CheckinService(session)
        result = await service.generate_qr_token(est_id)
        assert "qr_token" in result
        assert "qr_image_base64" in result
        assert result["qr_image_base64"].startswith("data:image/png;base64,")


@pytest.mark.asyncio
async def test_perform_checkin_invalid_token(db_engine):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        from uuid import uuid4

        service = CheckinService(session)
        with pytest.raises(ValueError, match="inválido"):
            await service.perform_checkin(uuid4(), "not-a-valid-token")
