"""Tip payment service."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.appointment import Appointment
from app.models.payment import PaymentStatus, Tip
from app.models.staff import StaffMember
from app.services.payment_providers.factory import PaymentProviderFactory


class TipService:
    """Create and confirm tip payments (100% to staff, no platform fee)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _validate_staff_and_appointment(
        self,
        user_id: UUID,
        staff_id: UUID,
        appointment_id: UUID | None,
    ) -> StaffMember:
        staff_result = await self.db.execute(select(StaffMember).where(StaffMember.id == staff_id))
        staff = staff_result.scalar_one_or_none()
        if not staff:
            raise ValueError("Profissional não encontrado")

        if appointment_id:
            appt_result = await self.db.execute(
                select(Appointment).where(
                    Appointment.id == appointment_id,
                    Appointment.user_id == user_id,
                )
            )
            if not appt_result.scalar_one_or_none():
                raise ValueError("Agendamento não encontrado ou não pertence ao usuário")

        return staff

    async def create_direct_tip(
        self,
        user_id: UUID,
        staff_id: UUID,
        amount: float,
        appointment_id: UUID | None = None,
    ) -> Tip:
        """Record an immediately succeeded tip (dev / no gateway)."""
        if amount <= 0:
            raise ValueError("Valor da gorjeta deve ser positivo")

        staff = await self._validate_staff_and_appointment(user_id, staff_id, appointment_id)

        tip = Tip(
            user_id=user_id,
            staff_id=staff_id,
            establishment_id=staff.establishment_id,
            appointment_id=appointment_id,
            amount=amount,
            status=PaymentStatus.succeeded,
        )
        self.db.add(tip)
        await self.db.commit()
        await self.db.refresh(tip)
        return tip

    async def create_payment_intent(
        self,
        user_id: UUID,
        staff_id: UUID,
        amount: float,
        appointment_id: UUID | None = None,
        provider_name: str = "stripe",
    ) -> dict[str, Any]:
        """Create pending tip + provider payment intent."""
        if amount <= 0:
            raise ValueError("Valor da gorjeta deve ser positivo")
        if not settings.STRIPE_SECRET_KEY and provider_name == "stripe":
            raise ValueError("Pagamentos Stripe não configurados")

        staff = await self._validate_staff_and_appointment(user_id, staff_id, appointment_id)

        tip = Tip(
            user_id=user_id,
            staff_id=staff_id,
            establishment_id=staff.establishment_id,
            appointment_id=appointment_id,
            amount=amount,
            status=PaymentStatus.pending,
            provider=provider_name,
        )
        self.db.add(tip)
        await self.db.flush()

        provider = PaymentProviderFactory.get_provider(provider_name)
        intent = await provider.create_intent(
            user_id=user_id,
            amount=amount,
            metadata={
                "type": "tip",
                "tip_id": str(tip.id),
                "staff_id": str(staff_id),
                "establishment_id": str(staff.establishment_id),
            },
        )

        tip.provider_payment_id = intent["provider_payment_id"]
        tip.stripe_payment_id = intent["provider_payment_id"]
        await self.db.commit()
        await self.db.refresh(tip)

        return {
            "tip_id": tip.id,
            "amount": amount,
            "provider": provider_name,
            "provider_payment_id": intent["provider_payment_id"],
            "client_secret": intent.get("client_secret"),
        }

    async def confirm_from_webhook(self, provider_payment_id: str) -> bool:
        """Mark tip as succeeded when payment intent succeeds."""
        result = await self.db.execute(
            select(Tip).where(
                (Tip.provider_payment_id == provider_payment_id)
                | (Tip.stripe_payment_id == provider_payment_id)
            )
        )
        tip = result.scalar_one_or_none()
        if not tip or tip.status == PaymentStatus.succeeded:
            return tip is not None

        tip.status = PaymentStatus.succeeded
        await self.db.commit()
        return True
