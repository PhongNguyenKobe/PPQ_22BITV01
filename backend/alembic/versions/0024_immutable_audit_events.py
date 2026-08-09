"""immutable business audit events

Revision ID: 0024_immutable_audit
Revises: 0023_pos_sales_channel
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0024_immutable_audit"
down_revision = "0023_pos_sales_channel"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "audit_events" not in tables:
        op.create_table(
            "audit_events",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
            sa.Column("entity_type", sa.String(50), nullable=False),
            sa.Column("entity_id", sa.String(100), nullable=False),
            sa.Column("action", sa.String(100), nullable=False),
            sa.Column("old_data", postgresql.JSONB()),
            sa.Column("new_data", postgresql.JSONB()),
            sa.Column("transaction_id", sa.String(50)),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
    else:
        columns = {column["name"] for column in inspector.get_columns("audit_events")}
        if "old_data" not in columns:
            op.add_column("audit_events", sa.Column("old_data", postgresql.JSONB()))

    indexes = {index["name"] for index in sa.inspect(bind).get_indexes("audit_events")}
    if "ix_audit_events_entity_type" not in indexes:
        op.create_index("ix_audit_events_entity_type", "audit_events", ["entity_type"])
    if "ix_audit_events_entity_id" not in indexes:
        op.create_index("ix_audit_events_entity_id", "audit_events", ["entity_id"])
    if "ix_audit_events_created_at" not in indexes:
        op.create_index("ix_audit_events_created_at", "audit_events", ["created_at"])
    op.execute("""
        CREATE OR REPLACE FUNCTION cineai_audit_row() RETURNS trigger AS $$
        DECLARE row_id text;
        BEGIN
            row_id := COALESCE((to_jsonb(NEW)->>'id'), (to_jsonb(OLD)->>'id'), 'unknown');
            INSERT INTO audit_events(entity_type, entity_id, action, old_data, new_data, transaction_id)
            VALUES (TG_TABLE_NAME, row_id, TG_OP,
                    CASE WHEN TG_OP IN ('UPDATE','DELETE') THEN to_jsonb(OLD) END,
                    CASE WHEN TG_OP IN ('INSERT','UPDATE') THEN to_jsonb(NEW) END,
                    txid_current()::text);
            RETURN COALESCE(NEW, OLD);
        END; $$ LANGUAGE plpgsql;
    """)
    for table in ("bookings", "booking_seats", "booking_combos", "payments", "tickets", "promotions"):
        op.execute(f"CREATE TRIGGER trg_audit_{table} AFTER INSERT OR UPDATE OR DELETE ON {table} FOR EACH ROW EXECUTE FUNCTION cineai_audit_row()")
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_audit_mutation() RETURNS trigger AS $$
        BEGIN RAISE EXCEPTION 'audit_events are immutable'; END; $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trg_audit_events_immutable BEFORE UPDATE OR DELETE ON audit_events
        FOR EACH ROW EXECUTE FUNCTION prevent_audit_mutation()
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_events_immutable ON audit_events")
    for table in ("bookings", "booking_seats", "booking_combos", "payments", "tickets", "promotions"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_audit_{table} ON {table}")
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_mutation()")
    op.execute("DROP FUNCTION IF EXISTS cineai_audit_row()")
    op.drop_index("ix_audit_events_created_at", table_name="audit_events")
    op.drop_index("ix_audit_events_entity_id", table_name="audit_events")
    op.drop_index("ix_audit_events_entity_type", table_name="audit_events")
    op.drop_table("audit_events")
