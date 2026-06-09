"""Plugin endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, DBSession, verify_establishment_owner
from app.services.plugin_service import PluginService

router = APIRouter(prefix="/establishments/{establishment_id}/plugins", tags=["Plugins"])


class PluginInstall(BaseModel):
    plugin_type: str = Field(..., min_length=2, max_length=50)
    config: dict = Field(default_factory=dict)


class PluginUpdate(BaseModel):
    active: bool | None = None
    config: dict | None = None
    expires_at: datetime | None = None


class PluginResponse(BaseModel):
    id: str
    establishment_id: str
    plugin_type: str
    active: bool
    config: dict
    expires_at: datetime | None

    model_config = {"from_attributes": True}


def _to_response(p) -> PluginResponse:
    return PluginResponse(
        id=str(p.id),
        establishment_id=str(p.establishment_id),
        plugin_type=p.plugin_type,
        active=p.active,
        config=p.config or {},
        expires_at=p.expires_at,
    )


@router.get("", response_model=list[PluginResponse])
async def list_plugins(establishment_id: UUID, db: DBSession, current_user: CurrentUser):
    """List plugins (owner)."""
    await verify_establishment_owner(db, establishment_id, current_user)
    service = PluginService(db)
    return [_to_response(p) for p in await service.list_for_establishment(establishment_id)]


@router.post("", response_model=PluginResponse, status_code=status.HTTP_201_CREATED)
async def install_plugin(
    establishment_id: UUID,
    data: PluginInstall,
    db: DBSession,
    current_user: CurrentUser,
):
    """Install or reactivate a plugin (owner)."""
    await verify_establishment_owner(db, establishment_id, current_user)
    service = PluginService(db)
    plugin = await service.install(establishment_id, data.plugin_type, data.config)
    return _to_response(plugin)


@router.patch("/{plugin_id}", response_model=PluginResponse)
async def update_plugin(
    establishment_id: UUID,
    plugin_id: UUID,
    data: PluginUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Update plugin config (owner)."""
    await verify_establishment_owner(db, establishment_id, current_user)
    service = PluginService(db)
    plugin = await service.get(establishment_id, plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin não encontrado")
    updated = await service.update(
        plugin,
        active=data.active,
        config=data.config,
        expires_at=data.expires_at,
    )
    return _to_response(updated)


@router.delete("/{plugin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_plugin(
    establishment_id: UUID,
    plugin_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Deactivate plugin (owner)."""
    await verify_establishment_owner(db, establishment_id, current_user)
    service = PluginService(db)
    plugin = await service.get(establishment_id, plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin não encontrado")
    await service.deactivate(plugin)
