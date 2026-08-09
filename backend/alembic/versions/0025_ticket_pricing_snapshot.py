"""add immutable pricing snapshot to per-seat tickets

Revision ID: 0025_ticket_pricing
Revises: 0024_immutable_audit
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0025_ticket_pricing"
down_revision = "0024_immutable_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tickets",
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "tickets",
        sa.Column(
            "pricing_details",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.execute("""
        UPDATE tickets AS t
        SET unit_price = bs.unit_price,
            pricing_details = bs.pricing_details
        FROM booking_seats AS bs
        WHERE t.booking_seat_id = bs.id
    """)


def downgrade() -> None:
    op.drop_column("tickets", "pricing_details")
    op.drop_column("tickets", "unit_price")
