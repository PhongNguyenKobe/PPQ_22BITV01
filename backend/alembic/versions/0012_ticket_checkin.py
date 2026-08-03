"""short ticket codes and check-in audit

Revision ID: 0012_ticket_checkin
Revises: 0011_refund_workflow
"""

from alembic import op
import sqlalchemy as sa


revision = "0012_ticket_checkin"
down_revision = "0011_refund_workflow"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("bookings", sa.Column("ticket_code", sa.String(32), nullable=True))
    op.add_column("bookings", sa.Column("checked_in_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("bookings", sa.Column("checked_in_by", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_bookings_checked_in_by", "bookings", "users", ["checked_in_by"], ["id"], ondelete="SET NULL"
    )
    op.execute("""
        UPDATE bookings b
        SET ticket_code = COALESCE(NULLIF(UPPER(LEFT(REGEXP_REPLACE(br.code, '[^A-Za-z0-9]', '', 'g'), 5)), ''), 'RAP')
            || '-' || TO_CHAR(s.starts_at, 'YYMMDD')
            || '-' || UPPER(LEFT(REPLACE(b.id::text, '-', ''), 8))
        FROM showtimes s
        JOIN auditoriums a ON a.id = s.auditorium_id
        JOIN branches br ON br.id = a.branch_id
        WHERE b.showtime_id = s.id
    """)
    op.alter_column("bookings", "ticket_code", nullable=False)
    op.create_unique_constraint("uq_bookings_ticket_code", "bookings", ["ticket_code"])
    op.create_index("ix_bookings_ticket_code", "bookings", ["ticket_code"])


def downgrade() -> None:
    op.drop_index("ix_bookings_ticket_code", table_name="bookings")
    op.drop_constraint("uq_bookings_ticket_code", "bookings", type_="unique")
    op.drop_constraint("fk_bookings_checked_in_by", "bookings", type_="foreignkey")
    op.drop_column("bookings", "checked_in_by")
    op.drop_column("bookings", "checked_in_at")
    op.drop_column("bookings", "ticket_code")
