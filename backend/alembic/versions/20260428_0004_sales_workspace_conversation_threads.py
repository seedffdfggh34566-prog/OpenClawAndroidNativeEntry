"""sales workspace conversation threads

Revision ID: 20260428_0004
Revises: 20260427_0003
Create Date: 2026-04-28 00:04:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260428_0004"
down_revision = "20260427_0003"
branch_labels = None
depends_on = None


def _json_payload() -> sa.TypeEngine:
    return sa.JSON().with_variant(postgresql.JSONB(none_as_null=False), "postgresql")


def upgrade() -> None:
    op.create_table(
        "sales_workspace_conversation_threads",
        sa.Column("workspace_id", sa.Text(), nullable=False),
        sa.Column("thread_id", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status in ('active', 'archived')", name="ck_sw_conversation_threads_status"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["sales_workspaces.workspace_id"],
            name="fk_sw_conversation_threads_workspace_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("workspace_id", "thread_id"),
    )
    op.create_index(
        "ix_sw_threads_workspace_updated_at",
        "sales_workspace_conversation_threads",
        ["workspace_id", "updated_at"],
    )

    op.add_column(
        "sales_workspace_conversation_messages",
        sa.Column("thread_id", sa.Text(), nullable=False, server_default="main"),
    )
    op.add_column(
        "sales_workspace_agent_runs",
        sa.Column("thread_id", sa.Text(), nullable=False, server_default="main"),
    )
    op.add_column(
        "sales_workspace_context_packs",
        sa.Column("thread_id", sa.Text(), nullable=False, server_default="main"),
    )
    op.create_index(
        "ix_sw_messages_workspace_thread_created_at",
        "sales_workspace_conversation_messages",
        ["workspace_id", "thread_id", "created_at"],
    )
    op.create_index(
        "ix_sw_agent_runs_workspace_thread_created_at",
        "sales_workspace_agent_runs",
        ["workspace_id", "thread_id", "created_at"],
    )
    op.create_index(
        "ix_sw_context_packs_workspace_thread_created_at",
        "sales_workspace_context_packs",
        ["workspace_id", "thread_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_sw_context_packs_workspace_thread_created_at", table_name="sales_workspace_context_packs")
    op.drop_index("ix_sw_agent_runs_workspace_thread_created_at", table_name="sales_workspace_agent_runs")
    op.drop_index("ix_sw_messages_workspace_thread_created_at", table_name="sales_workspace_conversation_messages")
    op.drop_column("sales_workspace_context_packs", "thread_id")
    op.drop_column("sales_workspace_agent_runs", "thread_id")
    op.drop_column("sales_workspace_conversation_messages", "thread_id")
    op.drop_index("ix_sw_threads_workspace_updated_at", table_name="sales_workspace_conversation_threads")
    op.drop_table("sales_workspace_conversation_threads")
