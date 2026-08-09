"""per-seat tickets with signed QR tokens

Revision ID: 0018_per_seat_tickets
Revises: 0017_issue_tickets_after_payment
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0018_per_seat_tickets"
down_revision = "0017_issue_tickets_after_payment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("booking_seat_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("booking_seats.id", ondelete="SET NULL"), nullable=True),
        sa.Column("seat_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("seats.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("ticket_code", sa.String(40), nullable=False),
        sa.Column("qr_nonce", sa.String(32), nullable=False),
        sa.Column("seat_row", sa.String(5), nullable=False),
        sa.Column("seat_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="ISSUED"),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("checked_in_at", sa.DateTime(timezone=True)),
        sa.Column("checked_in_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.UniqueConstraint("booking_seat_id", name="uq_tickets_booking_seat"),
        sa.UniqueConstraint("ticket_code", name="uq_tickets_ticket_code"),
    )
    op.create_index("ix_tickets_booking_id", "tickets", ["booking_id"])
    op.create_index("ix_tickets_ticket_code", "tickets", ["ticket_code"])
    op.execute("""
        INSERT INTO tickets (
            booking_id, booking_seat_id, seat_id, ticket_code, qr_nonce,
            seat_row, seat_number, status, issued_at, checked_in_at, checked_in_by
        )
        SELECT b.id, bs.id, bs.seat_id,
               b.ticket_code || '-' || LPAD(ROW_NUMBER() OVER (PARTITION BY b.id ORDER BY s.seat_row, s.seat_number)::text, 2, '0'),
               LEFT(REPLACE(uuid_generate_v4()::text, '-', ''), 32),
               s.seat_row, s.seat_number,
               CASE WHEN b.checked_in_at IS NULL THEN 'ISSUED' ELSE 'USED' END,
               b.created_at, b.checked_in_at, b.checked_in_by
        FROM bookings b
        JOIN booking_seats bs ON bs.booking_id = b.id
        JOIN seats s ON s.id = bs.seat_id
        WHERE b.status = 'CONFIRMED' AND b.ticket_code IS NOT NULL
    """)


def downgrade() -> None:
    op.drop_index("ix_tickets_ticket_code", table_name="tickets")
    op.drop_index("ix_tickets_booking_id", table_name="tickets")
    op.drop_table("tickets")
