"""Platform admin endpoints (A01-A14)."""

from uuid import UUID

from fastapi import APIRouter, Query, Request, status
from pydantic import BaseModel, Field
from slugify import slugify

from app.api.deps import AdminUser, DBSession
from app.core.exceptions import NotFoundError
from app.models.establishment import Establishment, EstablishmentCategory, EstablishmentStatus
from app.models.payment import PaymentStatus
from app.models.subscription import SubscriptionStatus
from app.models.user import User, UserRole
from app.schemas.admin import (
    AdminAuditLogListResponse,
    AdminAuditLogResponse,
    AdminDashboardResponse,
    AdminEstablishmentListResponse,
    AdminEstablishmentResponse,
    AdminEstablishmentUpdate,
    AdminPaymentListResponse,
    AdminPaymentResponse,
    AdminSubscriptionListResponse,
    AdminSubscriptionResponse,
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserUpdate,
)
from app.services.admin_service import AdminService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin", tags=["Admin"])


class AdminEstablishmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    owner_id: UUID
    category: EstablishmentCategory = EstablishmentCategory.barbershop
    address: str = Field(..., max_length=500)
    city: str = Field(..., max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    phone: str = Field(..., max_length=20)


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


async def _audit(
    db: DBSession,
    admin: User,
    request: Request,
    action: str,
    resource_type: str,
    resource_id: UUID | None = None,
) -> None:
    svc = AuditService(db)
    await svc.log(
        action=action,
        resource_type=resource_type,
        user_id=admin.id,
        resource_id=resource_id,
        ip_address=_client_ip(request),
        request_id=request.headers.get("x-request-id"),
    )


@router.get("/dashboard", response_model=AdminDashboardResponse)
async def admin_dashboard(db: DBSession, admin: AdminUser) -> AdminDashboardResponse:
    """Platform dashboard metrics (A01-A05)."""
    data = await AdminService(db).get_dashboard()
    return AdminDashboardResponse(**data)


@router.get("/establishments", response_model=AdminEstablishmentListResponse)
async def admin_list_establishments(
    db: DBSession,
    admin: AdminUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: EstablishmentStatus | None = Query(None, alias="status"),
) -> AdminEstablishmentListResponse:
    items, total = await AdminService(db).list_establishments(
        skip=skip, limit=limit, status=status_filter
    )
    return AdminEstablishmentListResponse(
        items=[AdminEstablishmentResponse.model_validate(e) for e in items],
        total=total,
    )


@router.post(
    "/establishments",
    response_model=AdminEstablishmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def admin_create_establishment(
    data: AdminEstablishmentCreate,
    request: Request,
    db: DBSession,
    admin: AdminUser,
) -> AdminEstablishmentResponse:
    owner = await db.get(User, data.owner_id)
    if not owner:
        raise NotFoundError("Proprietário não encontrado")

    slug_base = slugify(data.name)
    slug = slug_base
    counter = 1
    while True:
        from sqlalchemy import select

        existing = await db.execute(select(Establishment.id).where(Establishment.slug == slug))
        if not existing.scalar_one_or_none():
            break
        slug = f"{slug_base}-{counter}"
        counter += 1

    est = Establishment(
        owner_id=data.owner_id,
        name=data.name,
        slug=slug,
        category=data.category,
        address=data.address,
        city=data.city,
        state=data.state,
        phone=data.phone,
        status=EstablishmentStatus.active,
    )
    db.add(est)
    await db.commit()
    await db.refresh(est)
    await _audit(db, admin, request, "establishment.create", "establishment", est.id)
    return AdminEstablishmentResponse.model_validate(est)


@router.get("/establishments/{establishment_id}", response_model=AdminEstablishmentResponse)
async def admin_get_establishment(
    establishment_id: UUID,
    db: DBSession,
    admin: AdminUser,
) -> AdminEstablishmentResponse:
    est = await AdminService(db).get_establishment(establishment_id)
    if not est:
        raise NotFoundError("Estabelecimento não encontrado")
    return AdminEstablishmentResponse.model_validate(est)


@router.patch("/establishments/{establishment_id}", response_model=AdminEstablishmentResponse)
async def admin_update_establishment(
    establishment_id: UUID,
    data: AdminEstablishmentUpdate,
    request: Request,
    db: DBSession,
    admin: AdminUser,
) -> AdminEstablishmentResponse:
    est = await AdminService(db).get_establishment(establishment_id)
    if not est:
        raise NotFoundError("Estabelecimento não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(est, field, value)
    await db.commit()
    await db.refresh(est)
    await _audit(db, admin, request, "establishment.update", "establishment", est.id)
    return AdminEstablishmentResponse.model_validate(est)


@router.delete("/establishments/{establishment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_establishment(
    establishment_id: UUID,
    request: Request,
    db: DBSession,
    admin: AdminUser,
) -> None:
    est = await AdminService(db).get_establishment(establishment_id)
    if not est:
        raise NotFoundError("Estabelecimento não encontrado")
    est.status = EstablishmentStatus.closed
    await db.commit()
    await _audit(db, admin, request, "establishment.close", "establishment", est.id)


@router.get("/users", response_model=AdminUserListResponse)
async def admin_list_users(
    db: DBSession,
    admin: AdminUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: UserRole | None = None,
    search: str | None = None,
) -> AdminUserListResponse:
    items, total = await AdminService(db).list_users(
        skip=skip, limit=limit, role=role, search=search
    )
    return AdminUserListResponse(
        items=[AdminUserResponse.model_validate(u) for u in items],
        total=total,
    )


@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def admin_get_user(user_id: UUID, db: DBSession, admin: AdminUser) -> AdminUserResponse:
    user = await AdminService(db).get_user(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")
    return AdminUserResponse.model_validate(user)


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
async def admin_update_user(
    user_id: UUID,
    data: AdminUserUpdate,
    request: Request,
    db: DBSession,
    admin: AdminUser,
) -> AdminUserResponse:
    user = await AdminService(db).get_user(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    await _audit(db, admin, request, "user.update", "user", user.id)
    return AdminUserResponse.model_validate(user)


@router.get("/subscriptions", response_model=AdminSubscriptionListResponse)
async def admin_list_subscriptions(
    db: DBSession,
    admin: AdminUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: SubscriptionStatus | None = Query(None, alias="status"),
) -> AdminSubscriptionListResponse:
    items, total = await AdminService(db).list_subscriptions(
        skip=skip, limit=limit, status=status_filter
    )
    return AdminSubscriptionListResponse(
        items=[AdminSubscriptionResponse.model_validate(s) for s in items],
        total=total,
    )


@router.get("/payments", response_model=AdminPaymentListResponse)
async def admin_list_payments(
    db: DBSession,
    admin: AdminUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: PaymentStatus | None = Query(None, alias="status"),
) -> AdminPaymentListResponse:
    items, total = await AdminService(db).list_payments(
        skip=skip, limit=limit, status=status_filter
    )
    return AdminPaymentListResponse(
        items=[
            AdminPaymentResponse(
                id=p.id,
                user_id=p.user_id,
                establishment_id=p.establishment_id,
                amount=float(p.amount),
                platform_fee=float(p.platform_fee),
                status=p.status,
                purpose=p.purpose.value,
                created_at=p.created_at,
            )
            for p in items
        ],
        total=total,
    )


@router.get("/audit-logs", response_model=AdminAuditLogListResponse)
async def admin_list_audit_logs(
    db: DBSession,
    admin: AdminUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action: str | None = None,
    resource_type: str | None = None,
) -> AdminAuditLogListResponse:
    items, total = await AuditService(db).list_logs(
        skip=skip, limit=limit, action=action, resource_type=resource_type
    )
    return AdminAuditLogListResponse(
        items=[AdminAuditLogResponse.model_validate(i) for i in items],
        total=total,
    )
