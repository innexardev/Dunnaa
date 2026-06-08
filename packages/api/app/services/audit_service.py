"""Audit logging service."""

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditService:
    """Record and query audit logs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        *,
        action: str,
        resource_type: str,
        user_id: UUID | None = None,
        resource_id: UUID | None = None,
        establishment_id: UUID | None = None,
        ip_address: str | None = None,
        request_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            establishment_id=establishment_id,
            ip_address=ip_address,
            request_id=request_id,
            metadata_=metadata,
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def list_logs(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        action: str | None = None,
        resource_type: str | None = None,
    ) -> tuple[list[AuditLog], int]:
        query = select(AuditLog).order_by(AuditLog.created_at.desc())
        count_query = select(func.count(AuditLog.id))

        if action:
            query = query.where(AuditLog.action == action)
            count_query = count_query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
            count_query = count_query.where(AuditLog.resource_type == resource_type)

        total = (await self.db.execute(count_query)).scalar() or 0
        result = await self.db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all()), total
