"""Staff service unit tests."""

from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.user import User, UserRole
from app.services.staff_service import StaffService


@pytest.mark.asyncio
async def test_link_staff_by_phone(db_engine, establishment_id, staff_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        worker = User(phone="+5511555000001", referral_code="STF00001", role=UserRole.customer)
        session.add(worker)
        await session.commit()
        await session.refresh(worker)

        service = StaffService(session)
        staff = await service.link_user(
            UUID(str(staff_id)),
            UUID(str(establishment_id)),
            phone=worker.phone,
        )
        assert staff.user_id == worker.id

        await session.refresh(worker)
        assert worker.role == UserRole.staff


@pytest.mark.asyncio
async def test_link_staff_user_not_found(db_engine, establishment_id, staff_id):
    Session = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with Session() as session:
        service = StaffService(session)
        with pytest.raises(ValueError, match="Usuário não encontrado"):
            await service.link_user(
                UUID(str(staff_id)),
                UUID(str(establishment_id)),
                user_id=uuid4(),
            )
