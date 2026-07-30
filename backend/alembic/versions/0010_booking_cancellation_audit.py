"""preserve booking seats and cancellation audit

Revision ID: 0010_booking_cancel
Revises: 0009_vnpay_audit
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010_booking_cancel"
down_revision = "0009_vnpay_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("bookings", sa.Column("seat_snapshot", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.add_column("bookings", sa.Column("cancellation_reason", sa.Text(), nullable=True))
    op.add_column("bookings", sa.Column("cancellation_requested_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("bookings", sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("bookings", sa.Column("cancelled_by", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_bookings_cancelled_by", "bookings", "users", ["cancelled_by"], ["id"], ondelete="SET NULL")
    op.execute("""
        UPDATE bookings b
        SET seat_snapshot = COALESCE((
            SELECT jsonb_agg(
                jsonb_build_object(
                    'id', bs.seat_id,
                    'row', s.seat_row,
                    'number', s.seat_number
                )
                ORDER BY s.seat_row, s.seat_number
            )
            FROM booking_seats bs
            JOIN seats s ON s.id = bs.seat_id
            WHERE bs.booking_id = b.id
        ), '[]'::jsonb)
    """)


def downgrade() -> None:
    op.drop_constraint("fk_bookings_cancelled_by", "bookings", type_="foreignkey")
    op.drop_column("bookings", "cancelled_by")
    op.drop_column("bookings", "cancelled_at")
    op.drop_column("bookings", "cancellation_requested_at")
    op.drop_column("bookings", "cancellation_reason")
    op.drop_column("bookings", "seat_snapshot")
