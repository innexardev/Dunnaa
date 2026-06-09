"""Establishment plugin service."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plugin import EstablishmentPlugin


class PluginService:
    """Manage establishment plugins."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_establishment(self, establishment_id: UUID) -> list[EstablishmentPlugin]:
        result = await self.db.execute(
            select(EstablishmentPlugin)
            .where(EstablishmentPlugin.establishment_id == establishment_id)
            .order_by(EstablishmentPlugin.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, establishment_id: UUID, plugin_id: UUID) -> EstablishmentPlugin | None:
        result = await self.db.execute(
            select(EstablishmentPlugin).where(
                EstablishmentPlugin.id == plugin_id,
                EstablishmentPlugin.establishment_id == establishment_id,
            )
        )
        return result.scalar_one_or_none()

    async def install(
        self,
        establishment_id: UUID,
        plugin_type: str,
        config: dict | None = None,
    ) -> EstablishmentPlugin:
        existing = await self.db.execute(
            select(EstablishmentPlugin).where(
                EstablishmentPlugin.establishment_id == establishment_id,
                EstablishmentPlugin.plugin_type == plugin_type,
            )
        )
        plugin = existing.scalar_one_or_none()
        if plugin:
            plugin.active = True
            if config is not None:
                plugin.config = config
        else:
            plugin = EstablishmentPlugin(
                establishment_id=establishment_id,
                plugin_type=plugin_type,
                config=config or {},
                active=True,
            )
            self.db.add(plugin)
        await self.db.commit()
        await self.db.refresh(plugin)
        return plugin

    async def update(
        self,
        plugin: EstablishmentPlugin,
        *,
        active: bool | None = None,
        config: dict | None = None,
        expires_at: datetime | None = None,
    ) -> EstablishmentPlugin:
        if active is not None:
            plugin.active = active
        if config is not None:
            plugin.config = config
        if expires_at is not None:
            plugin.expires_at = expires_at
        await self.db.commit()
        await self.db.refresh(plugin)
        return plugin

    async def deactivate(self, plugin: EstablishmentPlugin) -> None:
        plugin.active = False
        await self.db.commit()

    async def has_active(self, establishment_id: UUID, plugin_type: str) -> bool:
        result = await self.db.execute(
            select(EstablishmentPlugin.id).where(
                EstablishmentPlugin.establishment_id == establishment_id,
                EstablishmentPlugin.plugin_type == plugin_type,
                EstablishmentPlugin.active == True,
            )
        )
        return result.scalar_one_or_none() is not None
