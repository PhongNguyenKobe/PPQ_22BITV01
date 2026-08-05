"""branch combos and booking combo lines

Revision ID: 0015_branch_combos
Revises: 0014_movie_reviews
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0015_branch_combos"
down_revision = "0014_movie_reviews"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("combos",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("branches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False), sa.Column("description", sa.Text()),
        sa.Column("price", sa.Numeric(12,2), nullable=False), sa.Column("image_url", sa.Text()),
        sa.Column("stock_quantity", sa.Integer()), sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price > 0", name="ck_combos_price_positive"))
    op.create_index("ix_combos_branch_id", "combos", ["branch_id"])
    op.create_table("booking_combos",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("combo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("combos.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("combo_name", sa.String(150), nullable=False), sa.Column("unit_price", sa.Numeric(12,2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False), sa.Column("line_total", sa.Numeric(12,2), nullable=False),
        sa.UniqueConstraint("booking_id", "combo_id", name="uq_booking_combos_booking_combo"))


def downgrade():
    op.drop_table("booking_combos")
    op.drop_index("ix_combos_branch_id", table_name="combos")
    op.drop_table("combos")
