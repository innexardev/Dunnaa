"""Customer subscription endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.subscription import (
    SubscriptionCreateRequest,
    SubscriptionResponse,
    SubscriptionUsageSummary,
)
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


def _to_response(sub, usage: SubscriptionUsageSummary | None = None) -> SubscriptionResponse:
    return SubscriptionResponse(
        id=sub.id,
        user_id=sub.user_id,
        plan_id=sub.plan_id,
        establishment_id=sub.establishment_id,
        status=sub.status,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        created_at=sub.created_at,
        cancelled_at=sub.cancelled_at,
        plan_name=sub.plan.name if sub.plan else None,
        usage=usage,
    )


@router.get("", response_model=list[SubscriptionResponse])
async def list_my_subscriptions(
    current_user: CurrentUser,
    db: DBSession,
) -> list[SubscriptionResponse]:
    """List current user's subscriptions (C52)."""
    service = SubscriptionService(db)
    subs = await service.list_for_user(current_user.id)
    results = []
    for sub in subs:
        usage = await service.build_usage_summary(sub) if sub.status.value == "active" else None
        results.append(_to_response(sub, usage))
    return results


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> SubscriptionResponse:
    """Get subscription with usage (C52)."""
    service = SubscriptionService(db)
    sub = await service.get_for_user(subscription_id, current_user.id)
    if not sub:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    usage = await service.build_usage_summary(sub) if sub.status.value == "active" else None
    return _to_response(sub, usage)


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    request: SubscriptionCreateRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> SubscriptionResponse:
    """Subscribe to a plan (C51). Stripe integration optional for MVP."""
    service = SubscriptionService(db)
    try:
        sub = await service.create(current_user.id, request.plan_id)
        usage = await service.build_usage_summary(sub)
        return _to_response(sub, usage)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "SUBSCRIPTION_ERROR", "message": str(e)},
        )


@router.delete("/{subscription_id}", response_model=SubscriptionResponse)
async def cancel_subscription(
    subscription_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> SubscriptionResponse:
    """Cancel subscription (C53)."""
    service = SubscriptionService(db)
    try:
        sub = await service.cancel(subscription_id, current_user.id)
        return _to_response(sub)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "SUBSCRIPTION_ERROR", "message": str(e)},
        )
