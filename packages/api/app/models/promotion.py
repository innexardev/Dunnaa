"""Promotion model."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.establishment import Establishment
    from app.models.service import Service, ServiceBundle


class Promotion(BaseModel):
    """Establishment promotion / discount."""

    __tablename__ = "promotions"

    establishment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("establishments.id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    discount_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # percent, fixed
    discount_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    service_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("services.id"),
        nullable=True,
    )
    bundle_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("service_bundles.id"),
        nullable=True,
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    establishment: Mapped["Establishment"] = relationship("Establishment")
    service: Mapped["Service | None"] = relationship("Service")
    bundle: Mapped["ServiceBundle | None"] = relationship("ServiceBundle")
