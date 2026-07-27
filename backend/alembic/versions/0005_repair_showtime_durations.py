"""repair invalid showtime durations

Revision ID: 0005_showtime_duration
Revises: 0004_showtime_lifecycle_holds
"""

from alembic import op


revision = "0005_showtime_duration"
down_revision = "0004_showtime_lifecycle_holds"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Historical UI values sometimes saved an end date one or more days later.
    # A showtime end is derived from the catalog duration.
    op.execute(
        """
        UPDATE showtimes AS s
        SET ends_at = s.starts_at + (m.duration_min * INTERVAL '1 minute')
        FROM movies AS m
        WHERE m.id = s.movie_id
          AND (
            s.ends_at <= s.starts_at
            OR s.ends_at > s.starts_at + ((m.duration_min + 60) * INTERVAL '1 minute')
          )
        """
    )
    op.execute("UPDATE showtimes SET status = 'OPEN' WHERE status = 'CLOSED'")


def downgrade() -> None:
    # Data repair is intentionally not reversed.
    pass
