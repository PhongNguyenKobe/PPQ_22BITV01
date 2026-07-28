"""add branch administrator role

Revision ID: 0006_branch_admin_role
Revises: 0005_showtime_duration
"""

from alembic import op


revision = "0006_branch_admin_role"
down_revision = "0005_showtime_duration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO roles (id, code, name)
        VALUES (3, 'BRANCH_ADMIN', 'Branch Administrator')
        ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name
        """
    )
    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('roles', 'id'),
            COALESCE((SELECT MAX(id) FROM roles), 1),
            true
        )
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM roles
        WHERE code = 'BRANCH_ADMIN'
          AND NOT EXISTS (
            SELECT 1 FROM user_roles WHERE user_roles.role_id = roles.id
          )
        """
    )
