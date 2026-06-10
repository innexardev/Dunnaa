"""Staff endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models import Establishment, StaffBlock, StaffMember, UserRole
from app.schemas.staff import StaffBlockCreate, StaffBlockResponse
from app.services.staff_service import StaffService

router = APIRouter(prefix="/establishments/{establishment_id}/staff", tags=["Staff"])


# ─── Schemas ───────────────────────────────────────────────────────────────────


class StaffCreate(BaseModel):
    """Create staff request."""

    name: str = Field(..., min_length=2, max_length=200)
    phone: str | None = Field(None, max_length=20)
    role: str = Field("barbeiro", max_length=100)
    avatar_url: str | None = Field(None, max_length=500)
    commission_rate: float | None = Field(None, ge=0, le=100)
    work_schedule: dict | None = Field(default_factory=dict)


class StaffUpdate(BaseModel):
    """Update staff request."""

    name: str | None = Field(None, max_length=200)
    phone: str | None = Field(None, max_length=20)
    role: str | None = Field(None, max_length=100)
    avatar_url: str | None = Field(None, max_length=500)
    commission_rate: float | None = Field(None, ge=0, le=100)
    work_schedule: dict | None = None
    active: bool | None = None


class StaffLinkRequest(BaseModel):
    """Link staff member to a user account."""

    user_id: UUID | None = None
    phone: str | None = Field(None, max_length=20)


class StaffResponse(BaseModel):
    """Staff response."""

    id: str
    name: str
    phone: str | None
    role: str
    avatar_url: str | None
    work_schedule: dict
    commission_rate: float | None
    active: bool
    user_id: str | None = None

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


def _staff_response(staff: StaffMember) -> StaffResponse:
    return StaffResponse(
        id=str(staff.id),
        name=staff.name,
        phone=staff.phone,
        role=staff.role,
        avatar_url=staff.avatar_url,
        work_schedule=staff.work_schedule,
        commission_rate=float(staff.commission_rate) if staff.commission_rate else None,
        active=staff.active,
        user_id=str(staff.user_id) if staff.user_id else None,
    )


# ─── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("", response_model=list[StaffResponse])
async def list_staff(
    establishment_id: UUID,
    db: DBSession,
    active_only: bool = True,
) -> list[StaffResponse]:
    """List staff members for an establishment."""
    query = select(StaffMember).where(StaffMember.establishment_id == establishment_id)

    if active_only:
        query = query.where(StaffMember.active == True)

    query = query.order_by(StaffMember.name)

    result = await db.execute(query)
    staff = result.scalars().all()

    return [_staff_response(s) for s in staff]


@router.post("", response_model=StaffResponse, status_code=201)
async def create_staff(
    establishment_id: UUID,
    request: StaffCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> StaffResponse:
    """Create new staff member."""
    establishment = await get_establishment_or_404(db, establishment_id)
    check_ownership(establishment, current_user)

    staff = StaffMember(
        establishment_id=establishment_id,
        name=request.name,
        phone=request.phone,
        role=request.role,
        avatar_url=request.avatar_url,
        commission_rate=request.commission_rate,
        work_schedule=request.work_schedule or {},
    )

    db.add(staff)
    await db.commit()
    await db.refresh(staff)

    return _staff_response(staff)


@router.get("/{staff_id}", response_model=StaffResponse)
async def get_staff(
    establishment_id: UUID,
    staff_id: UUID,
    db: DBSession,
) -> StaffResponse:
    """Get staff member by ID."""
    result = await db.execute(
        select(StaffMember).where(
            StaffMember.id == staff_id,
            StaffMember.establishment_id == establishment_id,
        )
    )
    staff = result.scalar_one_or_none()

    if not staff:
        raise NotFoundError("Funcionário")

    return _staff_response(staff)


@router.patch("/{staff_id}", response_model=StaffResponse)
async def update_staff(
    establishment_id: UUID,
    staff_id: UUID,
    request: StaffUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> StaffResponse:
    """Update staff member."""
    establishment = await get_establishment_or_404(db, establishment_id)
    check_ownership(establishment, current_user)

    result = await db.execute(
        select(StaffMember).where(
            StaffMember.id == staff_id,
            StaffMember.establishment_id == establishment_id,
        )
    )
    staff = result.scalar_one_or_none()

    if not staff:
        raise NotFoundError("Funcionário")

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(staff, field, value)

    await db.commit()
    await db.refresh(staff)

    return _staff_response(staff)


@router.post("/{staff_id}/link", response_model=StaffResponse)
async def link_staff_user(
    establishment_id: UUID,
    staff_id: UUID,
    request: StaffLinkRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> StaffResponse:
    """Link staff member to a user account (grants staff RBAC)."""
    establishment = await get_establishment_or_404(db, establishment_id)
    check_ownership(establishment, current_user)

    service = StaffService(db)
    try:
        staff = await service.link_user(
            staff_id,
            establishment_id,
            user_id=request.user_id,
            phone=request.phone,
        )
    except ValueError as e:
        status = 404 if "não encontrado" in str(e) else 400
        raise HTTPException(status_code=status, detail=str(e)) from e

    return _staff_response(staff)


@router.delete("/{staff_id}", status_code=204)
async def delete_staff(
    establishment_id: UUID,
    staff_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    """Delete staff member (soft delete)."""
    establishment = await get_establishment_or_404(db, establishment_id)
    check_ownership(establishment, current_user)

    result = await db.execute(
        select(StaffMember).where(
            StaffMember.id == staff_id,
            StaffMember.establishment_id == establishment_id,
        )
    )
    staff = result.scalar_one_or_none()

    if not staff:
        raise NotFoundError("Funcionário")

    staff.active = False
    await db.commit()


@router.post("/{staff_id}/blocks", response_model=StaffBlockResponse, status_code=201)
async def create_staff_block(
    establishment_id: UUID,
    staff_id: UUID,
    request: StaffBlockCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> StaffBlock:
    """Create a block period for a staff member."""
    establishment = await get_establishment_or_404(db, establishment_id)
    check_ownership(establishment, current_user)

    result = await db.execute(
        select(StaffMember).where(
            StaffMember.id == staff_id,
            StaffMember.establishment_id == establishment_id,
        )
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise NotFoundError("Funcionário")

    block = StaffBlock(
        staff_id=staff_id,
        start_at=request.start_at,
        end_at=request.end_at,
        reason=request.reason,
    )
    db.add(block)
    await db.commit()
    await db.refresh(block)
    return block


@router.get("/{staff_id}/blocks", response_model=list[StaffBlockResponse])
async def list_staff_blocks(
    establishment_id: UUID,
    staff_id: UUID,
    db: DBSession,
) -> list[StaffBlock]:
    """List blocks for a staff member."""
    result = await db.execute(select(StaffBlock).where(StaffBlock.staff_id == staff_id))
    return result.scalars().all()
