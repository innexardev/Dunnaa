"""Referral endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import CurrentUser, DBSession
from app.services.referral_service import ReferralService

router = APIRouter(prefix="/referrals", tags=["Referrals"])


class ReferralItem(BaseModel):
    id: str
    referred_id: str
    referred_name: str | None
    reward_amount: float | None
    reward_claimed: bool
    created_at: str

    model_config = {"from_attributes": True}


class ReferralListResponse(BaseModel):
    items: list[ReferralItem]
    stats: dict


class ClaimResponse(BaseModel):
    id: str
    reward_claimed: bool
    reward_amount: float | None


@router.get("/me", response_model=ReferralListResponse)
async def list_my_referrals(current_user: CurrentUser, db: DBSession) -> ReferralListResponse:
    """List referrals made by the current user."""
    service = ReferralService(db)
    referrals = await service.list_by_referrer(current_user.id)
    stats = await service.get_stats(current_user.id)
    items = [
        ReferralItem(
            id=str(r.id),
            referred_id=str(r.referred_id),
            referred_name=r.referred.name if r.referred else None,
            reward_amount=float(r.reward_amount) if r.reward_amount else None,
            reward_claimed=r.reward_claimed,
            created_at=r.created_at.isoformat(),
        )
        for r in referrals
    ]
    return ReferralListResponse(items=items, stats=stats)


@router.post("/{referral_id}/claim", response_model=ClaimResponse)
async def claim_referral_reward(
    referral_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> ClaimResponse:
    """Claim pending referral reward."""
    service = ReferralService(db)
    try:
        referral = await service.claim_reward(referral_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ClaimResponse(
        id=str(referral.id),
        reward_claimed=referral.reward_claimed,
        reward_amount=float(referral.reward_amount) if referral.reward_amount else None,
    )
