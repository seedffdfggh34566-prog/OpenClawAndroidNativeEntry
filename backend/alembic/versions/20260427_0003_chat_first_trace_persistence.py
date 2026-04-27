"""chat first trace persistence

Revision ID: 20260427_0003
Revises: 20260427_0002
Create Date: 2026-04-27 00:03:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260427_0003"
down_revision = "20260427_0002"
branch_labels = None
depends_on = None


def _json_payload() -> sa.TypeEngine:
    return sa.JSON().with_variant(postgresql.JSONB(none_as_null=False), "postgresql")


def upgrade() -> None:
    op.create_table(
        "sales_workspace_conversation_messages",
        sa.Column("workspace_id", sa.Text(), nullable=False),
        sa.Column("message_id", sa.Text(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("message_type", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("linked_object_refs_json", _json_payload(), nullable=False),
        sa.Column("created_by_agent_run_id", sa.Text(), nullable=True),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "role in ('user', 'assistant', 'system')",
            name="ck_sales_workspace_conversation_messages_role",
        ),
        sa.CheckConstraint(
            "message_type in ("
            "'product_profile_update', "
            "'lead_direction_update', "
            "'mixed_product_and_direction_update', "
            "'clarifying_question', "
            "'workspace_question', "
            "'draft_summary', "
            "'out_of_scope_v2_2', "
            "'system_note'"
            ")",
            name="ck_sales_workspace_conversation_messages_message_type",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["sales_workspaces.workspace_id"],
            name="fk_sales_workspace_conversation_messages_workspace_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("workspace_id", "message_id"),
    )
    op.create_index(
        "ix_sw_messages_workspace_created_at",
        "sales_workspace_conversation_messages",
        ["workspace_id", "created_at"],
    )
    op.create_index(
        "ix_sw_messages_workspace_role_created_at",
        "sales_workspace_conversation_messages",
        ["workspace_id", "role", "created_at"],
    )
    op.create_index(
        "ix_sw_messages_workspace_agent_run",
        "sales_workspace_conversation_messages",
        ["workspace_id", "created_by_agent_run_id"],
    )

    op.create_table(
        "sales_workspace_agent_runs",
        sa.Column("workspace_id", sa.Text(), nullable=False),
        sa.Column("agent_run_id", sa.Text(), nullable=False),
        sa.Column("run_type", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("input_refs_json", _json_payload(), nullable=False),
        sa.Column("output_refs_json", _json_payload(), nullable=False),
        sa.Column("runtime_metadata_json", _json_payload(), nullable=False),
        sa.Column("error_json", _json_payload(), nullable=True),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "run_type in ('sales_agent_turn')",
            name="ck_sales_workspace_agent_runs_run_type",
        ),
        sa.CheckConstraint(
            "status in ('queued', 'running', 'succeeded', 'failed')",
            name="ck_sales_workspace_agent_runs_status",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["sales_workspaces.workspace_id"],
            name="fk_sales_workspace_agent_runs_workspace_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("workspace_id", "agent_run_id"),
    )
    op.create_index(
        "ix_sw_agent_runs_workspace_created_at",
        "sales_workspace_agent_runs",
        ["workspace_id", "created_at"],
    )
    op.create_index(
        "ix_sw_agent_runs_workspace_status_created_at",
        "sales_workspace_agent_runs",
        ["workspace_id", "status", "created_at"],
    )
    op.create_index(
        "ix_sw_agent_runs_workspace_run_type_created_at",
        "sales_workspace_agent_runs",
        ["workspace_id", "run_type", "created_at"],
    )

    op.create_table(
        "sales_workspace_context_packs",
        sa.Column("workspace_id", sa.Text(), nullable=False),
        sa.Column("context_pack_id", sa.Text(), nullable=False),
        sa.Column("agent_run_id", sa.Text(), nullable=False),
        sa.Column("task_type", sa.Text(), nullable=False),
        sa.Column("token_budget_chars", sa.Integer(), nullable=False),
        sa.Column("input_refs_json", _json_payload(), nullable=False),
        sa.Column("source_versions_json", _json_payload(), nullable=False),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "task_type in ('sales_agent_turn')",
            name="ck_sales_workspace_context_packs_task_type",
        ),
        sa.CheckConstraint(
            "token_budget_chars > 0",
            name="ck_sales_workspace_context_packs_token_budget_chars",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["sales_workspaces.workspace_id"],
            name="fk_sales_workspace_context_packs_workspace_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id", "agent_run_id"],
            ["sales_workspace_agent_runs.workspace_id", "sales_workspace_agent_runs.agent_run_id"],
            name="fk_sales_workspace_context_packs_agent_run",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("workspace_id", "context_pack_id"),
    )
    op.create_index(
        "ix_sw_context_packs_workspace_agent_run",
        "sales_workspace_context_packs",
        ["workspace_id", "agent_run_id"],
    )
    op.create_index(
        "ix_sw_context_packs_workspace_created_at",
        "sales_workspace_context_packs",
        ["workspace_id", "created_at"],
    )
    op.create_index(
        "ix_sw_context_packs_workspace_task_type_created_at",
        "sales_workspace_context_packs",
        ["workspace_id", "task_type", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_sw_context_packs_workspace_task_type_created_at",
        table_name="sales_workspace_context_packs",
    )
    op.drop_index("ix_sw_context_packs_workspace_created_at", table_name="sales_workspace_context_packs")
    op.drop_index("ix_sw_context_packs_workspace_agent_run", table_name="sales_workspace_context_packs")
    op.drop_table("sales_workspace_context_packs")

    op.drop_index(
        "ix_sw_agent_runs_workspace_run_type_created_at",
        table_name="sales_workspace_agent_runs",
    )
    op.drop_index("ix_sw_agent_runs_workspace_status_created_at", table_name="sales_workspace_agent_runs")
    op.drop_index("ix_sw_agent_runs_workspace_created_at", table_name="sales_workspace_agent_runs")
    op.drop_table("sales_workspace_agent_runs")

    op.drop_index(
        "ix_sw_messages_workspace_agent_run",
        table_name="sales_workspace_conversation_messages",
    )
    op.drop_index(
        "ix_sw_messages_workspace_role_created_at",
        table_name="sales_workspace_conversation_messages",
    )
    op.drop_index(
        "ix_sw_messages_workspace_created_at",
        table_name="sales_workspace_conversation_messages",
    )
    op.drop_table("sales_workspace_conversation_messages")
