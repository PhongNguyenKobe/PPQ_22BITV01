"""complete cancellation review and VNPAY refund workflow

Revision ID: 0011_refund_workflow
Revises: 0010_booking_cancel
"""

from alembic import op
import sqlalchemy as sa


revision = "0011_refund_workflow"
down_revision = "0010_booking_cancel"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("bookings", sa.Column("cancellation_review_note", sa.Text(), nullable=True))
    op.add_column("bookings", sa.Column("cancellation_reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("bookings", sa.Column("cancellation_reviewed_by", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_bookings_cancellation_reviewed_by",
        "bookings",
        "users",
        ["cancellation_reviewed_by"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("payments", sa.Column("refund_request_id", sa.String(32), nullable=True))
    op.add_column("payments", sa.Column("refund_transaction_no", sa.String(30), nullable=True))
    op.add_column("payments", sa.Column("refund_response_code", sa.String(10), nullable=True))
    op.add_column("payments", sa.Column("refund_provider_status", sa.String(10), nullable=True))
    op.add_column("payments", sa.Column("refund_error", sa.Text(), nullable=True))
    op.add_column("payments", sa.Column("refund_attempts", sa.Integer(), nullable=False, server_default=sa.text("0")))
    op.add_column("payments", sa.Column("refund_requested_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("payments", sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True))
    op.create_unique_constraint("uq_payments_refund_request_id", "payments", ["refund_request_id"])


def downgrade() -> None:
    op.drop_constraint("uq_payments_refund_request_id", "payments", type_="unique")
    for column in (
        "refunded_at",
        "refund_requested_at",
        "refund_attempts",
        "refund_error",
        "refund_provider_status",
        "refund_response_code",
        "refund_transaction_no",
        "refund_request_id",
    ):
        op.drop_column("payments", column)
    op.drop_constraint("fk_bookings_cancellation_reviewed_by", "bookings", type_="foreignkey")
    op.drop_column("bookings", "cancellation_reviewed_by")
    op.drop_column("bookings", "cancellation_reviewed_at")
    op.drop_column("bookings", "cancellation_review_note")
