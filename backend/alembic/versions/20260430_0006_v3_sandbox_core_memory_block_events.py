"""v3 sandbox core memory block transition events

Revision ID: 20260430_0006
Revises: 20260430_0005
Create Date: 2026-04-30 00:06:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260430_0006"
down_revision = "20260430_0005"
branch_labels = None
depends_on = None


def _json_payload() -> sa.TypeEngine:
    return sa.JSON().with_variant(postgresql.JSONB(none_as_null=False), "postgresql")


def upgrade() -> None:
    op.create_table(
        "v3_sandbox_core_memory_block_transition_events",
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("transition_event_id", sa.String(length=192), nullable=False),
        sa.Column("trace_event_id", sa.String(length=96), nullable=True),
        sa.Column("turn_id", sa.String(length=96), nullable=True),
        sa.Column("tool_event_id", sa.String(length=96), nullable=True),
        sa.Column("tool_call_id", sa.String(length=128), nullable=True),
        sa.Column("tool_name", sa.String(length=64), nullable=False),
        sa.Column("block_label", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("before_value", sa.Text(), nullable=True),
        sa.Column("after_value", sa.Text(), nullable=True),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["v3_sandbox_sessions.session_id"],
            name="fk_v3_sandbox_core_memory_block_transitions_session_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("session_id", "transition_event_id"),
    )
    op.create_index(
        "ix_v3_sandbox_core_memory_transitions_session_created_at",
        "v3_sandbox_core_memory_block_transition_events",
        ["session_id", "created_at"],
    )
    op.create_index(
        "ix_v3_sandbox_core_memory_transitions_session_block",
        "v3_sandbox_core_memory_block_transition_events",
        ["session_id", "block_label"],
    )
    op.create_index(
        "ix_v3_sandbox_core_memory_transitions_session_trace",
        "v3_sandbox_core_memory_block_transition_events",
        ["session_id", "trace_event_id"],
    )
    op.create_index(
        "ix_v3_sandbox_core_memory_transitions_session_tool_event",
        "v3_sandbox_core_memory_block_transition_events",
        ["session_id", "tool_event_id"],
    )
    op.create_index(
        "ix_v3_sandbox_core_memory_transitions_session_tool_name",
        "v3_sandbox_core_memory_block_transition_events",
        ["session_id", "tool_name"],
    )
    op.create_index(
        "ix_v3_sandbox_core_memory_transitions_session_status",
        "v3_sandbox_core_memory_block_transition_events",
        ["session_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_v3_sandbox_core_memory_transitions_session_status", table_name="v3_sandbox_core_memory_block_transition_events")
    op.drop_index("ix_v3_sandbox_core_memory_transitions_session_tool_name", table_name="v3_sandbox_core_memory_block_transition_events")
    op.drop_index("ix_v3_sandbox_core_memory_transitions_session_tool_event", table_name="v3_sandbox_core_memory_block_transition_events")
    op.drop_index("ix_v3_sandbox_core_memory_transitions_session_trace", table_name="v3_sandbox_core_memory_block_transition_events")
    op.drop_index("ix_v3_sandbox_core_memory_transitions_session_block", table_name="v3_sandbox_core_memory_block_transition_events")
    op.drop_index("ix_v3_sandbox_core_memory_transitions_session_created_at", table_name="v3_sandbox_core_memory_block_transition_events")
    op.drop_table("v3_sandbox_core_memory_block_transition_events")
