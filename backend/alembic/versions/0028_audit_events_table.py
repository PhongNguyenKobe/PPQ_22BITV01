"""Compatibility marker for the audit-events revision deployed from main.

The actual table is created or upgraded by 0024_immutable_audit. Keeping this
revision lets databases already stamped at 0028_audit_events join the current
migration graph without trying to create the table twice.
"""

revision = "0028_audit_events"
down_revision = "0027_single_branch_assignment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
