"""Admin API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.establishment import EstablishmentStatus
from app.models.payment import PaymentStatus
from app.models.subscription import SubscriptionStatus
from app.models.user import UserRole


class AdminDashboardResponse(BaseModel):
    total_establishments: int
    active_establishments: int
    total_users: int
    active_subscriptions: int
    platform_revenue_total: float
    platform_revenue_30d: float
    revenue_growth_percent_30d: float
    new_users_30d: int
    new_establishments_30d: int
    generated_at: str


class AdminEstablishmentResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    slug: str
    city: str
    state: str
    status: EstablishmentStatus
    phone: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdminEstablishmentListResponse(BaseModel):
    items: list[AdminEstablishmentResponse]
    total: int


class AdminEstablishmentUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    status: EstablishmentStatus | None = None
    phone: str | None = Field(None, max_length=20)


class AdminUserResponse(BaseModel):
    id: UUID
    phone: str
    name: str | None
    email: str | None
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserListResponse(BaseModel):
    items: list[AdminUserResponse]
    total: int


class AdminUserUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    email: EmailStr | None = None
    role: UserRole | None = None


class AdminSubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    plan_id: UUID
    establishment_id: UUID
    status: SubscriptionStatus
    current_period_start: datetime | None
    current_period_end: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class AdminSubscriptionListResponse(BaseModel):
    items: list[AdminSubscriptionResponse]
    total: int


class AdminPaymentResponse(BaseModel):
    id: UUID
    user_id: UUID
    establishment_id: UUID
    amount: float
    platform_fee: float
    status: PaymentStatus
    purpose: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdminPaymentListResponse(BaseModel):
    items: list[AdminPaymentResponse]
    total: int


class AdminAuditLogResponse(BaseModel):
    id: UUID
    user_id: UUID | None
    action: str
    resource_type: str
    resource_id: UUID | None
    establishment_id: UUID | None
    ip_address: str | None
    request_id: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class AdminAuditLogListResponse(BaseModel):
    items: list[AdminAuditLogResponse]
    total: int
