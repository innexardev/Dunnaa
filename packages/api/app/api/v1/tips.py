"""Tips endpoints."""

from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.core.config import settings
from app.models.payment import Tip
from app.schemas.payment import TipCreate, TipResponse
from app.services.tip_service import TipService

router = APIRouter(prefix="/tips", tags=["Tips"])


class TipIntentResponse(BaseModel):
    """Stripe tip payment intent."""

    tip_id: UUID
    amount: float
    provider: str
    provider_payment_id: str
    client_secret: str | None = None


@router.post("/intent", response_model=TipIntentResponse)
async def create_tip_intent(
    request: TipCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> TipIntentResponse:
    """Create a Stripe PaymentIntent for a tip (100% to staff)."""
    service = TipService(db)
    try:
        result = await service.create_payment_intent(
            current_user.id,
            request.staff_id,
            request.amount,
            request.appointment_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return TipIntentResponse(**result)


@router.post("/", response_model=TipResponse)
async def create_tip(
    request: TipCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> Tip:
    """Give a tip to a staff member (direct when Stripe is not configured)."""
    service = TipService(db)
    try:
        if settings.STRIPE_SECRET_KEY:
            raise ValueError("Use POST /tips/intent para pagar gorjeta com cartão")
        tip = await service.create_direct_tip(
            current_user.id,
            request.staff_id,
            request.amount,
            request.appointment_id,
        )
    except ValueError as e:
        status = 404 if "não encontrado" in str(e) else 400
        raise HTTPException(status_code=status, detail=str(e)) from e

    return tip


@router.get("/me", response_model=Sequence[TipResponse])
async def list_my_tips(
    db: DBSession,
    current_user: CurrentUser,
) -> Sequence[Tip]:
    """List tips given by current user."""
    result = await db.execute(
        select(Tip).where(Tip.user_id == current_user.id).order_by(Tip.created_at.desc())
    )
    return result.scalars().all()
