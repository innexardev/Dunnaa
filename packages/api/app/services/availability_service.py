"""Availability slot calculation."""

from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentStatus
from app.models.establishment import Establishment
from app.models.service import Service
from app.models.staff import StaffMember
from app.models.staff_block import StaffBlock
from app.schemas.subscription import AvailabilitySlot


WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


class AvailabilityService:
    """Compute available appointment slots."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_slots(
        self,
        establishment_id: UUID,
        staff_id: UUID,
        service_id: UUID,
        target_date: date,
    ) -> list[AvailabilitySlot]:
        service = (
            await self.db.execute(select(Service).where(Service.id == service_id))
        ).scalar_one_or_none()
        if not service:
            raise ValueError("Serviço não encontrado")

        staff = (
            await self.db.execute(
                select(StaffMember).where(
                    StaffMember.id == staff_id,
                    StaffMember.establishment_id == establishment_id,
                )
            )
        ).scalar_one_or_none()
        if not staff:
            raise ValueError("Profissional não encontrado")

        establishment = (
            await self.db.execute(select(Establishment).where(Establishment.id == establishment_id))
        ).scalar_one_or_none()
        if not establishment:
            raise ValueError("Estabelecimento não encontrado")

        day_key = WEEKDAYS[target_date.weekday()]
        est_hours = (
            establishment.business_hours.get(day_key) if establishment.business_hours else None
        )
        if not est_hours:
            return []

        staff_hours = staff.work_schedule.get(day_key) if staff.work_schedule else est_hours
        if not staff_hours:
            return []

        open_time = datetime.strptime(staff_hours["open"], "%H:%M").time()
        close_time = datetime.strptime(staff_hours["close"], "%H:%M").time()
        day_start = datetime.combine(target_date, open_time, tzinfo=UTC)
        day_end = datetime.combine(target_date, close_time, tzinfo=UTC)

        duration = timedelta(minutes=service.duration_minutes)
        step = timedelta(minutes=15)

        blocks_result = await self.db.execute(
            select(StaffBlock).where(
                StaffBlock.staff_id == staff_id,
                StaffBlock.start_at < day_end,
                StaffBlock.end_at > day_start,
            )
        )
        blocks = blocks_result.scalars().all()

        appts_result = await self.db.execute(
            select(Appointment).where(
                Appointment.staff_id == staff_id,
                Appointment.status != AppointmentStatus.cancelled,
                Appointment.scheduled_at >= day_start,
                Appointment.scheduled_at < day_end + timedelta(days=1),
            )
        )
        appointments = appts_result.scalars().all()

        now = datetime.now(UTC)
        slots: list[AvailabilitySlot] = []
        cursor = day_start

        while cursor + duration <= day_end:
            slot_end = cursor + duration
            if cursor > now:
                blocked = any(b.start_at < slot_end and b.end_at > cursor for b in blocks)
                conflict = False
                for appt in appointments:
                    appt_end = appt.scheduled_at + timedelta(minutes=appt.duration_minutes)
                    if appt.scheduled_at < slot_end and appt_end > cursor:
                        conflict = True
                        break
                if not blocked and not conflict:
                    slots.append(AvailabilitySlot(start_at=cursor, end_at=slot_end))
            cursor += step

        return slots
