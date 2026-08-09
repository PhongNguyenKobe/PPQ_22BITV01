"""combo inventory lifecycle

Revision ID: 0019_combo_inventory_lifecycle
Revises: 0018_per_seat_tickets
"""

from alembic import op
import sqlalchemy as sa


revision = "0019_combo_inventory_lifecycle"
down_revision = "0018_per_seat_tickets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("booking_combos", sa.Column("inventory_status", sa.String(20), nullable=False, server_default="RESERVED"))
    op.execute("""
        UPDATE booking_combos bc
        SET inventory_status = CASE WHEN b.status = 'CONFIRMED' THEN 'SOLD' ELSE 'RELEASED' END
        FROM bookings b WHERE b.id = bc.booking_id
    """)


def downgrade() -> None:
    op.drop_column("booking_combos", "inventory_status")
