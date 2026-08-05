"""compact human-readable ticket codes

Revision ID: 0013_compact_codes
Revises: 0012_ticket_checkin
"""

from alembic import op


revision = "0013_compact_codes"
down_revision = "0012_ticket_checkin"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        WITH ranked AS (
            SELECT
                b.id,
                COALESCE(
                    NULLIF(UPPER(LEFT(REGEXP_REPLACE(br.code, '[^A-Za-z0-9]', '', 'g'), 5)), ''),
                    'RAP'
                ) || TO_CHAR(s.starts_at, 'YYMMDD') ||
                LPAD((ROW_NUMBER() OVER (
                    PARTITION BY br.id, TO_CHAR(s.starts_at, 'YYMMDD')
                    ORDER BY b.created_at, b.id
                ))::text, 3, '0') AS compact_code
            FROM bookings b
            JOIN showtimes s ON s.id = b.showtime_id
            JOIN auditoriums a ON a.id = s.auditorium_id
            JOIN branches br ON br.id = a.branch_id
        )
        UPDATE bookings b
        SET ticket_code = ranked.compact_code
        FROM ranked
        WHERE ranked.id = b.id
    """)


def downgrade() -> None:
    # Compact codes remain valid and unique; restoring UUID-based codes adds no value.
    pass
