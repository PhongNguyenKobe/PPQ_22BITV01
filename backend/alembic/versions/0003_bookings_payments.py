"""Add bookings and payments.

Revision ID: 0003_bookings_payments
Revises: 0002_movie_approval_requests
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_bookings_payments"
down_revision = "0002_movie_approval_requests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bookings",
        sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("showtime_id", sa.UUID(as_uuid=True), sa.ForeignKey("showtimes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(20), server_default=sa.text("'PENDING'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "booking_seats",
        sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("booking_id", sa.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("showtime_id", sa.UUID(as_uuid=True), sa.ForeignKey("showtimes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("seat_id", sa.UUID(as_uuid=True), sa.ForeignKey("seats.id", ondelete="RESTRICT"), nullable=False),
        sa.UniqueConstraint("showtime_id", "seat_id", name="uq_booking_seats_showtime_seat"),
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("booking_id", sa.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_method", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), server_default=sa.text("'PENDING'"), nullable=False),
        sa.Column("transaction_id", sa.String(150), unique=True),
        sa.Column("paid_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("booking_seats")
    op.drop_table("bookings")
