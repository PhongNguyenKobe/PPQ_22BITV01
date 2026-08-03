"""add real movie reviews

Revision ID: 0014_movie_reviews
Revises: 0013_compact_codes
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0014_movie_reviews"
down_revision = "0013_compact_codes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "movie_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("movie_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rating", sa.SmallInteger(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_visible", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_movie_reviews_rating"),
        sa.ForeignKeyConstraint(["movie_id"], ["movies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("movie_id", "user_id", name="uq_movie_reviews_movie_user"),
    )
    op.create_index("ix_movie_reviews_movie_id", "movie_reviews", ["movie_id"])
    op.create_index("ix_movie_reviews_user_id", "movie_reviews", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_movie_reviews_user_id", table_name="movie_reviews")
    op.drop_index("ix_movie_reviews_movie_id", table_name="movie_reviews")
    op.drop_table("movie_reviews")
