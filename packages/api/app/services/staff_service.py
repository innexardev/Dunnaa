"""Staff management helpers."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.staff import StaffMember
from app.models.user import User, UserRole


class StaffService:
    """Link staff records to user accounts."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def link_user(
        self,
        staff_id: UUID,
        establishment_id: UUID,
        *,
        user_id: UUID | None = None,
        phone: str | None = None,
    ) -> StaffMember:
        """Associate a staff member with a platform user account."""
        if not user_id and not phone:
            raise ValueError("Informe user_id ou phone")

        staff_result = await self.db.execute(
            select(StaffMember).where(
                StaffMember.id == staff_id,
                StaffMember.establishment_id == establishment_id,
            )
        )
        staff = staff_result.scalar_one_or_none()
        if not staff:
            raise ValueError("Funcionário não encontrado")

        if user_id:
            user_result = await self.db.execute(select(User).where(User.id == user_id))
        else:
            user_result = await self.db.execute(select(User).where(User.phone == phone))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("Usuário não encontrado")

        existing = await self.db.execute(
            select(StaffMember).where(
                StaffMember.establishment_id == establishment_id,
                StaffMember.user_id == user.id,
                StaffMember.id != staff_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Usuário já vinculado a outro profissional neste estabelecimento")

        staff.user_id = user.id
        if user.role == UserRole.customer:
            user.role = UserRole.staff

        await self.db.commit()
        await self.db.refresh(staff)
        return staff
