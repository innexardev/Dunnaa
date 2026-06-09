"""Review endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DBSession, verify_establishment_owner
from app.schemas.review import (
    ReviewCreate,
    ReviewListResponse,
    ReviewOwnerResponse,
    ReviewResponse,
    ReviewUpdate,
)
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    data: ReviewCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> ReviewResponse:
    """Create a review."""
    service = ReviewService(db)
    try:
        review = await service.create(current_user.id, data)

        # Prepare response (handle optional user loading if not joined)
        # Service returns ORM object. If lazy loading issue, it should be handled there
        # or we manually populate for response
        resp = ReviewResponse.model_validate(review)
        resp.user_name = current_user.name
        return resp

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/establishments/{establishment_id}", response_model=ReviewListResponse)
async def list_establishment_reviews(
    establishment_id: UUID,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> ReviewListResponse:
    """List public reviews for an establishment."""
    service = ReviewService(db)
    reviews, total = await service.list_by_establishment(establishment_id, page, page_size)

    items = []
    for r in reviews:
        item = ReviewResponse.model_validate(r)
        if r.user:
            item.user_name = r.user.name or "Anônimo"
        items.append(item)

    return ReviewListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/my", response_model=list[ReviewResponse])
async def list_my_reviews(
    current_user: CurrentUser,
    db: DBSession,
) -> list[ReviewResponse]:
    """List reviews created by current user."""
    service = ReviewService(db)
    reviews = await service.list_by_user(current_user.id)
    return [ReviewResponse.model_validate(r) for r in reviews]


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: UUID,
    data: ReviewUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> ReviewResponse:
    """Update a review (Author only)."""
    service = ReviewService(db)
    review = await service.update(current_user.id, review_id, data)

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return ReviewResponse.model_validate(review)


@router.patch("/{review_id}/respond", response_model=ReviewResponse)
async def respond_to_review(
    review_id: UUID,
    data: ReviewOwnerResponse,
    current_user: CurrentUser,
    db: DBSession,
) -> ReviewResponse:
    """Respond to a review (Establishment Owner only)."""
    service = ReviewService(db)

    # 1. Fetch review to get establishment_id
    from sqlalchemy import select

    from app.models.review import Review

    # This logic ideally belongs in service but verification requires db access
    # or service needs to support ownership check
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # 2. Verify ownership
    await verify_establishment_owner(db, review.establishment_id, current_user)

    # 3. Add response
    updated_review = await service.respond(review_id, data.response)
    return ReviewResponse.model_validate(updated_review)


@router.post("/{review_id}/approve-google", response_model=ReviewResponse)
async def approve_review_for_google(
    review_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> ReviewResponse:
    """Approve review for Google sync (owner, rating >= 4)."""
    from sqlalchemy import select

    from app.models.review import Review
    from app.services.google_review_service import GoogleReviewService

    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    await verify_establishment_owner(db, review.establishment_id, current_user)

    service = GoogleReviewService(db)
    try:
        updated = await service.approve_for_google(review_id, review.establishment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ReviewResponse.model_validate(updated)


@router.post("/{review_id}/send-google", response_model=ReviewResponse)
async def send_review_to_google(
    review_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> ReviewResponse:
    """Send approved review to Google (owner)."""
    from sqlalchemy import select

    from app.models.review import Review
    from app.services.google_review_service import GoogleReviewService

    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    await verify_establishment_owner(db, review.establishment_id, current_user)

    service = GoogleReviewService(db)
    try:
        updated = await service.send_to_google(review_id, review.establishment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ReviewResponse.model_validate(updated)


@router.get(
    "/establishments/{establishment_id}/google-pending", response_model=list[ReviewResponse]
)
async def list_pending_google_reviews(
    establishment_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[ReviewResponse]:
    """List reviews approved but not yet sent to Google (owner)."""
    await verify_establishment_owner(db, establishment_id, current_user)
    from app.services.google_review_service import GoogleReviewService

    service = GoogleReviewService(db)
    reviews = await service.list_pending_sync(establishment_id)
    return [ReviewResponse.model_validate(r) for r in reviews]
