"""Initial schema with TimescaleDB hypertables.

Revision ID: 001
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prices",
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Float(), nullable=False),
        sa.Column("source", sa.String(50), server_default="alpha_vantage"),
        sa.PrimaryKeyConstraint("timestamp", "symbol"),
    )

    # TimescaleDB hypertable conversion (requires extension installed)
    op.execute(
        "SELECT create_hypertable('prices', 'timestamp', chunk_time_interval => INTERVAL '1 day')"
    )


def downgrade() -> None:
    op.drop_table("prices")

