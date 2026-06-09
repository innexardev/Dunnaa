"""Add subscription fields to checkins table."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "e5f9b2c3d4a1"
down_revision = "d4e8a1b2c3f0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "checkins",
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "checkins",
        sa.Column(
            "subscription_use_consumed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.create_foreign_key(
        "fk_checkins_subscription_id",
        "checkins",
        "subscriptions",
        ["subscription_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_checkins_subscription_id", "checkins", type_="foreignkey")
    op.drop_column("checkins", "subscription_use_consumed")
    op.drop_column("checkins", "subscription_id")
