"""Subscription schemas aligned with DB models (monthly per-item limits)."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.subscription import SubscriptionStatus


class SubscriptionPlanItemUsage(BaseModel):
    """Usage for a single plan item in the current period."""

    plan_item_id: UUID
    service_id: UUID | None
    bundle_id: UUID | None
    quantity_per_month: int
    uses_this_month: int
    remaining: int


class SubscriptionUsageSummary(BaseModel):
    """Aggregated usage for a subscription."""

    items: list[SubscriptionPlanItemUsage]
    period_start: datetime
    period_end: datetime


class SubscriptionCreateRequest(BaseModel):
    """Create customer subscription."""

    plan_id: UUID
    payment_method_id: str | None = Field(
        None,
        description="Stripe payment method ID (optional in dev/MVP)",
    )


class SubscriptionResponse(BaseModel):
    """Customer subscription response."""

    id: UUID
    user_id: UUID
    plan_id: UUID
    establishment_id: UUID
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    created_at: datetime
    cancelled_at: datetime | None = None
    plan_name: str | None = None
    usage: SubscriptionUsageSummary | None = None

    model_config = {"from_attributes": True}


class AvailabilitySlot(BaseModel):
    """Available appointment slot."""

    start_at: datetime
    end_at: datetime


class AvailabilityResponse(BaseModel):
    """Available slots for a staff member on a date."""

    establishment_id: UUID
    staff_id: UUID
    service_id: UUID
    date: date
    slots: list[AvailabilitySlot]


class SearchHistoryCreate(BaseModel):
    """Record a search query."""

    query: str = Field(..., min_length=1, max_length=255)
    establishment_clicked_id: UUID | None = None


class SearchHistoryResponse(BaseModel):
    """Search history entry."""

    id: UUID
    query: str
    establishment_clicked_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
