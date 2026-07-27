"""Add showtime lifecycle, drafts, and expiring seat holds.

Revision ID: 0004_showtime_lifecycle_holds
Revises: 0003_bookings_payments
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_showtime_lifecycle_holds"
down_revision = "0003_bookings_payments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("showtimes", sa.Column("booking_closes_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("showtimes", sa.Column("cancellation_reason", sa.Text(), nullable=True))
    op.execute("UPDATE showtimes SET booking_closes_at = starts_at - INTERVAL '15 minutes'")
    op.alter_column("showtimes", "booking_closes_at", nullable=False)
    op.add_column("bookings", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "seat_holds",
        sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("showtime_id", sa.UUID(as_uuid=True), sa.ForeignKey("showtimes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("seat_id", sa.UUID(as_uuid=True), sa.ForeignKey("seats.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("showtime_id", "seat_id", name="uq_seat_holds_showtime_seat"),
    )
    op.create_index("ix_seat_holds_expires_at", "seat_holds", ["expires_at"])
    op.create_index("ix_seat_holds_user_showtime", "seat_holds", ["user_id", "showtime_id"])


def downgrade() -> None:
    op.drop_index("ix_seat_holds_user_showtime", table_name="seat_holds")
    op.drop_index("ix_seat_holds_expires_at", table_name="seat_holds")
    op.drop_table("seat_holds")
    op.drop_column("bookings", "expires_at")
    op.drop_column("showtimes", "cancellation_reason")
    op.drop_column("showtimes", "booking_closes_at")
