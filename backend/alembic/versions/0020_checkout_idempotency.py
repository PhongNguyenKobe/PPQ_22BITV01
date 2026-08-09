"""booking and payment idempotency

Revision ID: 0020_checkout_idempotency
Revises: 0019_combo_inventory_lifecycle
"""

from alembic import op
import sqlalchemy as sa


revision = "0020_checkout_idempotency"
down_revision = "0019_combo_inventory_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("bookings", sa.Column("idempotency_key", sa.String(100)))
    op.create_unique_constraint("uq_bookings_user_idempotency", "bookings", ["user_id", "idempotency_key"])
    op.add_column("payments", sa.Column("idempotency_key", sa.String(100)))
    op.add_column("payments", sa.Column("checkout_url", sa.Text()))
    op.create_unique_constraint("uq_payments_user_idempotency", "payments", ["user_id", "idempotency_key"])


def downgrade() -> None:
    op.drop_constraint("uq_payments_user_idempotency", "payments", type_="unique")
    op.drop_column("payments", "checkout_url")
    op.drop_column("payments", "idempotency_key")
    op.drop_constraint("uq_bookings_user_idempotency", "bookings", type_="unique")
    op.drop_column("bookings", "idempotency_key")
