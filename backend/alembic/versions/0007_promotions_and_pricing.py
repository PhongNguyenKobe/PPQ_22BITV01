"""promotions and seat pricing

Revision ID: 0007_promotions_pricing
Revises: 0006_branch_admin_role
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007_promotions_pricing"
down_revision = "0006_branch_admin_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("seat_types", sa.Column("price_multiplier", sa.Numeric(5, 2), nullable=False, server_default="1.00"))
    op.create_table(
        "promotions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("discount_type", sa.String(20), nullable=False),
        sa.Column("discount_value", sa.Numeric(12, 2), nullable=False),
        sa.Column("max_discount", sa.Numeric(12, 2)),
        sa.Column("min_order_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usage_limit", sa.Integer()),
        sa.Column("used_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("discount_value > 0", name="ck_promotions_discount_positive"),
        sa.CheckConstraint("usage_limit IS NULL OR usage_limit >= 0", name="ck_promotions_usage_limit"),
    )
    op.add_column("bookings", sa.Column("subtotal_price", sa.Numeric(12, 2), nullable=False, server_default="0"))
    op.add_column("bookings", sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False, server_default="0"))
    op.add_column("bookings", sa.Column("promotion_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_bookings_promotion", "bookings", "promotions", ["promotion_id"], ["id"], ondelete="SET NULL")
    op.execute("UPDATE bookings SET subtotal_price = total_price")
    op.execute("UPDATE seat_types SET price_multiplier = CASE code WHEN 'VIP' THEN 1.25 WHEN 'COUPLE' THEN 2.00 ELSE 1.00 END")


def downgrade() -> None:
    op.drop_constraint("fk_bookings_promotion", "bookings", type_="foreignkey")
    op.drop_column("bookings", "promotion_id")
    op.drop_column("bookings", "discount_amount")
    op.drop_column("bookings", "subtotal_price")
    op.drop_table("promotions")
    op.drop_column("seat_types", "price_multiplier")
