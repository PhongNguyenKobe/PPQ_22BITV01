"""add user verification and registration fields

Revision ID: 0012_user_verification
Revises: 0011_refund_workflow
"""

from alembic import op
import sqlalchemy as sa


revision = "0012_user_verification"
down_revision = "0011_refund_workflow"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("address", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("receive_marketing_emails", sa.Boolean(), nullable=False, server_default=sa.text("true")))
    op.add_column("users", sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("users", sa.Column("verification_code", sa.String(10), nullable=True))
    op.add_column("users", sa.Column("verification_code_expires_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "verification_code_expires_at")
    op.drop_column("users", "verification_code")
    op.drop_column("users", "is_verified")
    op.drop_column("users", "receive_marketing_emails")
    op.drop_column("users", "address")
