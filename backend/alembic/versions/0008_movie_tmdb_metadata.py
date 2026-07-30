"""store TMDB identity and credits on movies

Revision ID: 0008_movie_tmdb_metadata
Revises: 0007_promotions_pricing
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_movie_tmdb_metadata"
down_revision = "0007_promotions_pricing"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("movies", sa.Column("tmdb_id", sa.Integer(), nullable=True))
    op.add_column("movies", sa.Column("director", sa.String(length=255), nullable=True))
    op.add_column("movies", sa.Column("cast_names", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.create_index("ix_movies_tmdb_id", "movies", ["tmdb_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_movies_tmdb_id", table_name="movies")
    op.drop_column("movies", "cast_names")
    op.drop_column("movies", "director")
    op.drop_column("movies", "tmdb_id")
