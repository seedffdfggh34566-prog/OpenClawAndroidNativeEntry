"""v3 sandbox drop legacy memory path

Revision ID: 20260502_0007
Revises: 20260430_0006
Create Date: 2026-05-02 00:07:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260502_0007"
down_revision = "20260430_0006"
branch_labels = None
depends_on = None


def _json_payload() -> sa.TypeEngine:
    return sa.JSON().with_variant(postgresql.JSONB(none_as_null=False), "postgresql")


def upgrade() -> None:
    op.drop_index(
        "ix_v3_sandbox_memory_transitions_session_trace",
        table_name="v3_sandbox_memory_transition_events",
    )
    op.drop_index(
        "ix_v3_sandbox_memory_transitions_session_after_status",
        table_name="v3_sandbox_memory_transition_events",
    )
    op.drop_index(
        "ix_v3_sandbox_memory_transitions_session_memory",
        table_name="v3_sandbox_memory_transition_events",
    )
    op.drop_index(
        "ix_v3_sandbox_memory_transitions_session_created_at",
        table_name="v3_sandbox_memory_transition_events",
    )
    op.drop_table("v3_sandbox_memory_transition_events")

    op.drop_index("ix_v3_sandbox_memory_items_session_source", table_name="v3_sandbox_memory_items")
    op.drop_index("ix_v3_sandbox_memory_items_session_updated_at", table_name="v3_sandbox_memory_items")
    op.drop_index("ix_v3_sandbox_memory_items_session_status", table_name="v3_sandbox_memory_items")
    op.drop_table("v3_sandbox_memory_items")

    op.drop_index("ix_v3_sandbox_action_events_session_turn", table_name="v3_sandbox_action_events")
    op.drop_index("ix_v3_sandbox_action_events_session_type", table_name="v3_sandbox_action_events")
    op.drop_index("ix_v3_sandbox_action_events_session_created_at", table_name="v3_sandbox_action_events")
    op.drop_table("v3_sandbox_action_events")


def downgrade() -> None:
    op.create_table(
        "v3_sandbox_action_events",
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("trace_event_id", sa.String(length=96), nullable=False),
        sa.Column("action_index", sa.Integer(), nullable=False),
        sa.Column("turn_id", sa.String(length=96), nullable=False),
        sa.Column("action_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id", "trace_event_id"],
            ["v3_sandbox_trace_events.session_id", "v3_sandbox_trace_events.trace_event_id"],
            name="fk_v3_sandbox_action_events_trace",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("session_id", "trace_event_id", "action_index"),
    )
    op.create_index(
        "ix_v3_sandbox_action_events_session_created_at",
        "v3_sandbox_action_events",
        ["session_id", "created_at"],
    )
    op.create_index(
        "ix_v3_sandbox_action_events_session_type",
        "v3_sandbox_action_events",
        ["session_id", "action_type"],
    )
    op.create_index(
        "ix_v3_sandbox_action_events_session_turn",
        "v3_sandbox_action_events",
        ["session_id", "turn_id"],
    )

    op.create_table(
        "v3_sandbox_memory_items",
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("memory_id", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("superseded_by", sa.String(length=128), nullable=True),
        sa.Column("tags_json", _json_payload(), nullable=False),
        sa.Column("evidence_json", _json_payload(), nullable=False),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status in ('observed', 'inferred', 'hypothesis', 'confirmed', 'rejected', 'superseded')",
            name="ck_v3_sandbox_memory_items_status",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["v3_sandbox_sessions.session_id"],
            name="fk_v3_sandbox_memory_items_session_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("session_id", "memory_id"),
    )
    op.create_index(
        "ix_v3_sandbox_memory_items_session_status",
        "v3_sandbox_memory_items",
        ["session_id", "status"],
    )
    op.create_index(
        "ix_v3_sandbox_memory_items_session_updated_at",
        "v3_sandbox_memory_items",
        ["session_id", "updated_at"],
    )
    op.create_index(
        "ix_v3_sandbox_memory_items_session_source",
        "v3_sandbox_memory_items",
        ["session_id", "source"],
    )

    op.create_table(
        "v3_sandbox_memory_transition_events",
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("transition_event_id", sa.String(length=192), nullable=False),
        sa.Column("trace_event_id", sa.String(length=96), nullable=True),
        sa.Column("turn_id", sa.String(length=96), nullable=True),
        sa.Column("action_index", sa.Integer(), nullable=True),
        sa.Column("transition_type", sa.String(length=64), nullable=False),
        sa.Column("memory_id", sa.String(length=128), nullable=False),
        sa.Column("before_status", sa.String(length=32), nullable=True),
        sa.Column("after_status", sa.String(length=32), nullable=True),
        sa.Column("superseded_by", sa.String(length=128), nullable=True),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["v3_sandbox_sessions.session_id"],
            name="fk_v3_sandbox_memory_transition_events_session_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("session_id", "transition_event_id"),
    )
    op.create_index(
        "ix_v3_sandbox_memory_transitions_session_created_at",
        "v3_sandbox_memory_transition_events",
        ["session_id", "created_at"],
    )
    op.create_index(
        "ix_v3_sandbox_memory_transitions_session_memory",
        "v3_sandbox_memory_transition_events",
        ["session_id", "memory_id"],
    )
    op.create_index(
        "ix_v3_sandbox_memory_transitions_session_after_status",
        "v3_sandbox_memory_transition_events",
        ["session_id", "after_status"],
    )
    op.create_index(
        "ix_v3_sandbox_memory_transitions_session_trace",
        "v3_sandbox_memory_transition_events",
        ["session_id", "trace_event_id"],
    )
