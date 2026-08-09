"""pricing rules and promotion controls

Revision ID: 0021_pricing_promotion
Revises: 0020_checkout_idempotency
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0021_pricing_promotion"
down_revision = "0020_checkout_idempotency"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("booking_seats", sa.Column("unit_price", sa.Numeric(12, 2), nullable=False, server_default="0"))
    op.add_column("booking_seats", sa.Column("pricing_details", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")))
    op.add_column("promotions", sa.Column("per_user_limit", sa.Integer()))
    op.add_column("promotions", sa.Column("budget_amount", sa.Numeric(14, 2)))
    op.add_column("promotions", sa.Column("used_amount", sa.Numeric(14, 2), nullable=False, server_default="0"))
    for column in ("branch_ids", "movie_ids", "payment_methods", "excluded_dates"):
        op.add_column("promotions", sa.Column(column, postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.create_table(
        "pricing_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("branches.id", ondelete="CASCADE")),
        sa.Column("screen_type", sa.String(30)), sa.Column("day_of_week", sa.Integer()),
        sa.Column("starts_on", sa.DateTime(timezone=True)), sa.Column("ends_on", sa.DateTime(timezone=True)),
        sa.Column("time_from", sa.Time()), sa.Column("time_to", sa.Time()),
        sa.Column("multiplier", sa.Numeric(6, 3), nullable=False, server_default="1"),
        sa.Column("surcharge", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.CheckConstraint("multiplier > 0", name="ck_pricing_rules_multiplier_positive"),
    )
    op.create_index("ix_pricing_rules_branch_id", "pricing_rules", ["branch_id"])
    op.create_table(
        "promotion_redemptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("promotion_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("promotions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="RESERVED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("payment_id", name="uq_promotion_redemptions_payment"),
    )
    op.create_index("ix_promotion_redemptions_promotion_id", "promotion_redemptions", ["promotion_id"])
    op.create_index("ix_promotion_redemptions_user_id", "promotion_redemptions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_promotion_redemptions_user_id", table_name="promotion_redemptions")
    op.drop_index("ix_promotion_redemptions_promotion_id", table_name="promotion_redemptions")
    op.drop_table("promotion_redemptions")
    op.drop_index("ix_pricing_rules_branch_id", table_name="pricing_rules")
    op.drop_table("pricing_rules")
    for column in ("excluded_dates", "payment_methods", "movie_ids", "branch_ids", "used_amount", "budget_amount", "per_user_limit"):
        op.drop_column("promotions", column)
    op.drop_column("booking_seats", "pricing_details")
    op.drop_column("booking_seats", "unit_price")
