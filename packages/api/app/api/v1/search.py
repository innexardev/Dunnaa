"""Search history endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.subscription import SearchHistoryCreate, SearchHistoryResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/users/me/search-history", tags=["Search"])


@router.get("", response_model=list[SearchHistoryResponse])
async def list_search_history(
    current_user: CurrentUser,
    db: DBSession,
) -> list[SearchHistoryResponse]:
    """List user search history (C12)."""
    service = SearchService(db)
    entries = await service.list_for_user(current_user.id)
    return [SearchHistoryResponse.model_validate(e) for e in entries]


@router.post("", response_model=SearchHistoryResponse, status_code=status.HTTP_201_CREATED)
async def record_search(
    request: SearchHistoryCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> SearchHistoryResponse:
    """Record a search query (C12)."""
    service = SearchService(db)
    entry = await service.record(
        current_user.id,
        request.query,
        request.establishment_clicked_id,
    )
    return SearchHistoryResponse.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search_entry(
    entry_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> None:
    """Delete a search history entry."""
    service = SearchService(db)
    deleted = await service.delete_entry(current_user.id, entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Registro não encontrado")


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_search_history(
    current_user: CurrentUser,
    db: DBSession,
) -> None:
    """Clear all search history for user."""
    service = SearchService(db)
    await service.clear(current_user.id)
