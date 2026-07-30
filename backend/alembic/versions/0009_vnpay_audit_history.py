"""add VNPAY reconciliation fields and immutable status history

Revision ID: 0009_vnpay_audit
Revises: 0008_movie_tmdb_metadata
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0009_vnpay_audit"
down_revision = "0008_movie_tmdb_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("provider_ref", sa.String(100), nullable=True))
    op.add_column("payments", sa.Column("provider_transaction_no", sa.String(30), nullable=True))
    op.add_column("payments", sa.Column("bank_transaction_no", sa.String(255), nullable=True))
    op.add_column("payments", sa.Column("bank_code", sa.String(30), nullable=True))
    op.add_column("payments", sa.Column("card_type", sa.String(30), nullable=True))
    op.add_column("payments", sa.Column("response_code", sa.String(10), nullable=True))
    op.add_column("payments", sa.Column("provider_status", sa.String(10), nullable=True))
    op.add_column("payments", sa.Column("signature_valid", sa.Boolean(), nullable=True))
    op.add_column("payments", sa.Column("provider_paid_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("payments", sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True))
    op.create_unique_constraint("uq_payments_provider_ref", "payments", ["provider_ref"])
    op.create_index("ix_payments_provider_transaction_no", "payments", ["provider_transaction_no"])

    op.create_table(
        "payment_status_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("old_status", sa.String(20), nullable=True),
        sa.Column("new_status", sa.String(20), nullable=False),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("response_code", sa.String(10), nullable=True),
        sa.Column("provider_status", sa.String(10), nullable=True),
        sa.Column("signature_valid", sa.Boolean(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_payment_status_history_payment_id", "payment_status_history", ["payment_id"])

    # Existing successful demo payments remain valid and are marked as legacy,
    # so historical revenue is preserved without pretending they came from VNPAY.
    op.execute("""
        INSERT INTO payment_status_history (payment_id, old_status, new_status, source, note)
        SELECT id, NULL, status, 'LEGACY', 'Migrated from payment data created before VNPAY integration'
        FROM payments
    """)


def downgrade() -> None:
    op.drop_index("ix_payment_status_history_payment_id", table_name="payment_status_history")
    op.drop_table("payment_status_history")
    op.drop_index("ix_payments_provider_transaction_no", table_name="payments")
    op.drop_constraint("uq_payments_provider_ref", "payments", type_="unique")
    for column in (
        "last_verified_at", "provider_paid_at", "signature_valid", "provider_status",
        "response_code", "card_type", "bank_code", "bank_transaction_no",
        "provider_transaction_no", "provider_ref",
    ):
        op.drop_column("payments", column)
