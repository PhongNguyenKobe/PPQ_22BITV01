"""short opaque scan code for tickets

Revision ID: 0026_short_scan_code
Revises: 0025_ticket_pricing
"""

from alembic import op
import sqlalchemy as sa


revision = "0026_short_scan_code"
down_revision = "0025_ticket_pricing"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tickets", sa.Column("scan_code", sa.String(12), nullable=True))
    op.execute("UPDATE tickets SET scan_code = 'Q' || upper(substr(md5(id::text || qr_nonce), 1, 11))")
    op.alter_column("tickets", "scan_code", nullable=False)
    op.create_index("ix_tickets_scan_code", "tickets", ["scan_code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_tickets_scan_code", table_name="tickets")
    op.drop_column("tickets", "scan_code")
