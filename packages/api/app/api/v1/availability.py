"""Availability endpoints."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import DBSession
from app.schemas.subscription import AvailabilityResponse
from app.services.availability_service import AvailabilityService

router = APIRouter(tags=["Availability"])


@router.get(
    "/establishments/{establishment_id}/staff/{staff_id}/availability",
    response_model=AvailabilityResponse,
)
async def get_staff_availability(
    establishment_id: UUID,
    staff_id: UUID,
    db: DBSession,
    service_id: UUID = Query(..., description="Service ID for slot duration"),
    target_date: date = Query(..., alias="date", description="Date (YYYY-MM-DD)"),
) -> AvailabilityResponse:
    """List available slots for a staff member on a date (C33)."""
    service = AvailabilityService(db)
    try:
        slots = await service.get_slots(establishment_id, staff_id, service_id, target_date)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "AVAILABILITY_ERROR", "message": str(e)},
        )

    return AvailabilityResponse(
        establishment_id=establishment_id,
        staff_id=staff_id,
        service_id=service_id,
        date=target_date,
        slots=slots,
    )
