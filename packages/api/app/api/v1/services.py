"""Service endpoints."""

from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DBSession
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models import Establishment, Service, StaffMember, UserRole
from app.models.service import service_staff

router = APIRouter(prefix="/establishments/{establishment_id}/services", tags=["Services"])


# ─── Schemas ───────────────────────────────────────────────────────────────────


class ServiceCreate(BaseModel):
    """Create service request."""

    name: str = Field(..., min_length=2, max_length=200)
    description: str | None = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    duration_minutes: int = Field(30, ge=5, le=480)
    deposit_required: bool = False


class ServiceUpdate(BaseModel):
    """Update service request."""

    name: str | None = Field(None, max_length=200)
    description: str | None = Field(None, max_length=1000)
    price: float | None = Field(None, gt=0)
    duration_minutes: int | None = Field(None, ge=5)
    active: bool | None = None
    sort_order: int | None = None
    deposit_required: bool | None = None


class ServiceResponse(BaseModel):
    """Service response."""

    id: str
    name: str
    description: str | None
    price: float
    duration_minutes: int
    active: bool
    sort_order: int
    deposit_required: bool

    class Config:
        from_attributes = True


# ─── Helpers ───────────────────────────────────────────────────────────────────


async def get_establishment_or_404(db: DBSession, establishment_id: UUID) -> Establishment:
    """Get establishment or raise 404."""
    result = await db.execute(select(Establishment).where(Establishment.id == establishment_id))
    establishment = result.scalar_one_or_none()
    if not establishment:
        raise NotFoundError("Estabelecimento")
    return establishment


def check_ownership(establishment: Establishment, user: CurrentUser) -> None:
    """Check if user owns the establishment."""
    if establishment.owner_id != user.id and user.role != UserRole.admin:
        raise ForbiddenError()


# ─── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("", response_model=list[ServiceResponse])
async def list_services(
    establishment_id: UUID,
    db: DBSession,
    active_only: bool = True,
) -> list[ServiceResponse]:
    """List services for an establishment."""
    query = select(Service).where(Service.establishment_id == establishment_id)

    if active_only:
        query = query.where(Service.active == True)

    query = query.order_by(Service.sort_order, Service.name)

    result = await db.execute(query)
    services = result.scalars().all()

    return [
        ServiceResponse(
            id=str(s.id),
            name=s.name,
            description=s.description,
            price=float(s.price),
            duration_minutes=s.duration_minutes,
            active=s.active,
            sort_order=s.sort_order,
            deposit_required=s.deposit_required,
        )
        for s in services
    ]


@router.post("", response_model=ServiceResponse, status_code=201)
async def create_service(
    establishment_id: UUID,
    request: ServiceCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> ServiceResponse:
    """Create new service."""
    establishment = await get_establishment_or_404(db, establishment_id)
    check_ownership(establishment, current_user)

    service = Service(
        establishment_id=establishment_id,
        name=request.name,
        description=request.description,
        price=request.price,
        duration_minutes=request.duration_minutes,
        deposit_required=request.deposit_required,
    )

    db.add(service)
    await db.commit()
    await db.refresh(service)

    return ServiceResponse(
        id=str(service.id),
        name=service.name,
        description=service.description,
        price=float(service.price),
        duration_minutes=service.duration_minutes,
        active=service.active,
        sort_order=service.sort_order,
        deposit_required=service.deposit_required,
    )


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    establishment_id: UUID,
    service_id: UUID,
    db: DBSession,
) -> ServiceResponse:
    """Get service by ID."""
    result = await db.execute(
        select(Service).where(
            Service.id == service_id,
            Service.establishment_id == establishment_id,
        )
    )
    service = result.scalar_one_or_none()

    if not service:
        raise NotFoundError("Serviço")

    return ServiceResponse(
        id=str(service.id),
        name=service.name,
        description=service.description,
        price=float(service.price),
        duration_minutes=service.duration_minutes,
        active=service.active,
        sort_order=service.sort_order,
        deposit_required=service.deposit_required,
    )


@router.patch("/{service_id}", response_model=ServiceResponse)
async def update_service(
    establishment_id: UUID,
    service_id: UUID,
    request: ServiceUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> ServiceResponse:
    """Update service."""
    establishment = await get_establishment_or_404(db, establishment_id)
    check_ownership(establishment, current_user)

    result = await db.execute(
        select(Service).where(
            Service.id == service_id,
            Service.establishment_id == establishment_id,
        )
    )
    service = result.scalar_one_or_none()

    if not service:
        raise NotFoundError("Serviço")

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(service, field, value)

    await db.commit()
    await db.refresh(service)

    return ServiceResponse(
        id=str(service.id),
        name=service.name,
        description=service.description,
        price=float(service.price),
        duration_minutes=service.duration_minutes,
        active=service.active,
        sort_order=service.sort_order,
        deposit_required=service.deposit_required,
    )


@router.delete("/{service_id}", status_code=204)
async def delete_service(
    establishment_id: UUID,
    service_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    """Delete service (soft delete)."""
    establishment = await get_establishment_or_404(db, establishment_id)
    check_ownership(establishment, current_user)

    result = await db.execute(
        select(Service).where(
            Service.id == service_id,
            Service.establishment_id == establishment_id,
        )
    )
    service = result.scalar_one_or_none()

    if not service:
        raise NotFoundError("Serviço")

    service.active = False
    await db.commit()


class StaffAssignRequest(BaseModel):
    """Assign staff members to a service."""

    staff_ids: list[UUID] = Field(default_factory=list)


class ServiceStaffResponse(BaseModel):
    """Staff member linked to a service."""

    id: str
    name: str
    role: str
    active: bool


@router.get("/{service_id}/staff", response_model=list[ServiceStaffResponse])
async def list_service_staff(
    establishment_id: UUID,
    service_id: UUID,
    db: DBSession,
) -> list[ServiceStaffResponse]:
    """List staff members assigned to a service."""
    result = await db.execute(
        select(Service)
        .where(Service.id == service_id, Service.establishment_id == establishment_id)
        .options(selectinload(Service.staff_members))
    )
    service = result.scalar_one_or_none()
    if not service:
        raise NotFoundError("Serviço")

    return [
        ServiceStaffResponse(
            id=str(s.id),
            name=s.name,
            role=s.role,
            active=s.active,
        )
        for s in service.staff_members
        if s.active
    ]


@router.put("/{service_id}/staff", response_model=list[ServiceStaffResponse])
async def assign_service_staff(
    establishment_id: UUID,
    service_id: UUID,
    request: StaffAssignRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> list[ServiceStaffResponse]:
    """Replace staff assignments for a service (owner only)."""
    establishment = await get_establishment_or_404(db, establishment_id)
    check_ownership(establishment, current_user)

    result = await db.execute(
        select(Service).where(
            Service.id == service_id,
            Service.establishment_id == establishment_id,
        )
    )
    service = result.scalar_one_or_none()
    if not service:
        raise NotFoundError("Serviço")

    if request.staff_ids:
        staff_result = await db.execute(
            select(StaffMember).where(
                StaffMember.establishment_id == establishment_id,
                StaffMember.id.in_(request.staff_ids),
                StaffMember.active == True,
            )
        )
        staff_list = list(staff_result.scalars().all())
        if len(staff_list) != len(set(request.staff_ids)):
            raise NotFoundError("Profissional")
    else:
        staff_list = []

    await db.execute(delete(service_staff).where(service_staff.c.service_id == service_id))
    for member in staff_list:
        await db.execute(insert(service_staff).values(service_id=service_id, staff_id=member.id))
    await db.commit()

    refreshed = await db.execute(
        select(Service).where(Service.id == service_id).options(selectinload(Service.staff_members))
    )
    updated = refreshed.scalar_one()
    return [
        ServiceStaffResponse(
            id=str(s.id),
            name=s.name,
            role=s.role,
            active=s.active,
        )
        for s in updated.staff_members
        if s.active
    ]
