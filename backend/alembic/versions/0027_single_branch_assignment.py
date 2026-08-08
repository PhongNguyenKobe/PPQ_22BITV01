"""Compatibility shim for missing revision 0027_single_branch_assignment.

This revision may exist in deployed databases from a previous branch history.
It is intentionally a no-op so Alembic can resolve the revision graph and
allow the service to start.
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "0027_single_branch_assignment"
down_revision = "0016_merge_heads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op compatibility migration.
    pass


def downgrade() -> None:
    # No-op compatibility migration.
    pass
