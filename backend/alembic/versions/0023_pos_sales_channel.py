"""POS sales channel and walk-in customer snapshot

Revision ID: 0023_pos_sales_channel
Revises: 0022_notification_outbox
"""

from alembic import op
import sqlalchemy as sa


revision = "0023_pos_sales_channel"
down_revision = "0022_notification_outbox"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("bookings", sa.Column("sales_channel", sa.String(20), nullable=False, server_default="ONLINE"))
    op.add_column("bookings", sa.Column("customer_name", sa.String(150)))
    op.add_column("bookings", sa.Column("customer_email", sa.String(255)))
    op.add_column("bookings", sa.Column("customer_phone", sa.String(20)))


def downgrade() -> None:
    op.drop_column("bookings", "customer_phone")
    op.drop_column("bookings", "customer_email")
    op.drop_column("bookings", "customer_name")
    op.drop_column("bookings", "sales_channel")
