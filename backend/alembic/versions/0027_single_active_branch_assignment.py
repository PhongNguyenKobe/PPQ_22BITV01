"""enforce one active branch assignment per administrator

Revision ID: 0029_single_active_branch
Revises: 0026_short_scan_code, 0028_audit_events
"""

from alembic import op
import sqlalchemy as sa


revision = "0029_single_active_branch"
down_revision = ("0026_short_scan_code", "0028_audit_events")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        WITH ranked AS (
            SELECT branch_id, user_id,
                   row_number() OVER (PARTITION BY user_id ORDER BY assigned_at DESC, branch_id DESC) AS position
            FROM branch_staff
            WHERE is_active = TRUE
        )
        UPDATE branch_staff bs
        SET is_active = FALSE
        FROM ranked r
        WHERE bs.branch_id = r.branch_id
          AND bs.user_id = r.user_id
          AND r.position > 1
        """
    )
    op.create_index(
        "uq_branch_staff_one_active_user",
        "branch_staff",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_active = TRUE"),
    )


def downgrade() -> None:
    op.drop_index("uq_branch_staff_one_active_user", table_name="branch_staff")
