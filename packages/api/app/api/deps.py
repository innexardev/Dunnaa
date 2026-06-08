"""API dependencies for route injection."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.logging import bind_context
from app.core.security import decode_access_token
from app.models import Establishment, StaffMember, User, UserRole

security = HTTPBearer()


# ─── Database Session ──────────────────────────────────────────────────────────

DBSession = Annotated[AsyncSession, Depends(get_db)]


# ─── Authentication ────────────────────────────────────────────────────────────


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: DBSession,
) -> User:
    """Get current authenticated user from token."""
    try:
        user_id = decode_access_token(credentials.credentials)
    except Exception as e:
        raise UnauthorizedError("Token inválido ou expirado") from e

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedError("Usuário não encontrado")

    bind_context(user_id=str(user.id), user_role=user.role.value)

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# ─── Authorization ─────────────────────────────────────────────────────────────


def require_role(*roles: UserRole):
    """Dependency to require user role."""

    async def role_checker(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise ForbiddenError("Sem permissão para esta ação")
        return current_user

    return role_checker


def require_admin():
    """Require admin role."""
    return require_role(UserRole.admin)


def require_owner():
    """Require owner or admin role."""
    return require_role(UserRole.owner, UserRole.admin)


def require_staff():
    """Require staff, owner, or admin role."""
    return require_role(UserRole.staff, UserRole.owner, UserRole.admin)


# ─── Type Aliases ──────────────────────────────────────────────────────────────

AdminUser = Annotated[User, Depends(require_admin())]
OwnerUser = Annotated[User, Depends(require_owner())]
StaffUser = Annotated[User, Depends(require_staff())]


# ─── Optional Auth ─────────────────────────────────────────────────────────────


async def get_optional_user(
    db: DBSession,
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> User | None:
    """Get current user if authenticated, otherwise None."""
    if not credentials:
        return None

    try:
        user_id = decode_access_token(credentials.credentials)
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    except Exception:
        return None


OptionalUser = Annotated[User | None, Depends(get_optional_user)]


# ─── Establishment Access ──────────────────────────────────────────────────────


async def verify_establishment_owner(
    db: AsyncSession,
    establishment_id: UUID,
    user: User,
) -> Establishment:
    """Verify that user owns the establishment (or is admin)."""
    result = await db.execute(select(Establishment).where(Establishment.id == establishment_id))
    establishment = result.scalar_one_or_none()

    if not establishment:
        raise NotFoundError("Estabelecimento não encontrado")

    if user.role == UserRole.admin:
        return establishment

    if establishment.owner_id != user.id:
        raise ForbiddenError("Sem permissão para esta ação")

    return establishment


async def verify_establishment_access(
    db: AsyncSession,
    establishment_id: UUID,
    user: User,
) -> Establishment:
    """Verify owner, admin, or active staff access."""
    result = await db.execute(select(Establishment).where(Establishment.id == establishment_id))
    establishment = result.scalar_one_or_none()

    if not establishment:
        raise NotFoundError("Estabelecimento não encontrado")

    if user.role == UserRole.admin:
        return establishment

    if establishment.owner_id == user.id:
        return establishment

    staff_result = await db.execute(
        select(StaffMember.id).where(
            StaffMember.establishment_id == establishment_id,
            StaffMember.user_id == user.id,
            StaffMember.active == True,
        )
    )
    if staff_result.scalar_one_or_none():
        return establishment

    raise ForbiddenError("Sem permissão para esta ação")
