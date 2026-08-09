"""issue tickets only after successful payment

Revision ID: 0017_issue_tickets_after_payment
Revises: 0016_merge_heads
"""

from alembic import op
import sqlalchemy as sa


revision = "0017_issue_tickets_after_payment"
down_revision = "0016_merge_heads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("bookings", "ticket_code", nullable=True)
    op.execute("UPDATE bookings SET ticket_code = NULL WHERE status IN ('PENDING', 'EXPIRED')")
    op.execute("""
        WITH ranked AS (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY booking_id ORDER BY created_at, id) AS position
            FROM payments
            WHERE status IN ('PENDING', 'SUCCESS', 'RECONCILIATION_REQUIRED')
        )
        UPDATE payments SET status = 'CANCELLED'
        WHERE id IN (SELECT id FROM ranked WHERE position > 1)
    """)
    op.create_index(
        "uq_payments_active_booking",
        "payments",
        ["booking_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('PENDING', 'SUCCESS', 'RECONCILIATION_REQUIRED')"),
    )


def downgrade() -> None:
    op.drop_index("uq_payments_active_booking", table_name="payments")
    op.execute("""
        UPDATE bookings
        SET ticket_code = 'LEGACY' || LEFT(REPLACE(id::text, '-', ''), 26)
        WHERE ticket_code IS NULL
    """)
    op.alter_column("bookings", "ticket_code", nullable=False)
