"""backend baseline

Revision ID: 20260423_0001
Revises: 
Create Date: 2026-04-23 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260423_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_profiles",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("one_line_description", sa.String(length=500), nullable=False),
        sa.Column("source_notes", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("target_customers", sa.JSON(), nullable=False),
        sa.Column("target_industries", sa.JSON(), nullable=False),
        sa.Column("typical_use_cases", sa.JSON(), nullable=False),
        sa.Column("pain_points_solved", sa.JSON(), nullable=False),
        sa.Column("core_advantages", sa.JSON(), nullable=False),
        sa.Column("delivery_model", sa.String(length=255), nullable=False),
        sa.Column("constraints", sa.JSON(), nullable=False),
        sa.Column("missing_fields", sa.JSON(), nullable=False),
        sa.Column("confidence_score", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "lead_analysis_results",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("product_profile_id", sa.String(length=32), nullable=False),
        sa.Column("created_by_agent_run_id", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("analysis_scope", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("priority_industries", sa.JSON(), nullable=False),
        sa.Column("priority_customer_types", sa.JSON(), nullable=False),
        sa.Column("scenario_opportunities", sa.JSON(), nullable=False),
        sa.Column("ranking_explanations", sa.JSON(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=False),
        sa.Column("risks", sa.JSON(), nullable=False),
        sa.Column("limitations", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_lead_analysis_results_created_by_agent_run_id"),
        "lead_analysis_results",
        ["created_by_agent_run_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_lead_analysis_results_product_profile_id"),
        "lead_analysis_results",
        ["product_profile_id"],
        unique=False,
    )
    op.create_table(
        "analysis_reports",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("product_profile_id", sa.String(length=32), nullable=False),
        sa.Column("lead_analysis_result_id", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("sections", sa.JSON(), nullable=False),
        sa.Column("body_markdown", sa.Text(), nullable=True),
        sa.Column("export_status", sa.String(length=32), nullable=True),
        sa.Column("export_refs", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_analysis_reports_lead_analysis_result_id"),
        "analysis_reports",
        ["lead_analysis_result_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_analysis_reports_product_profile_id"),
        "analysis_reports",
        ["product_profile_id"],
        unique=False,
    )
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("run_type", sa.String(length=64), nullable=False),
        sa.Column("triggered_by", sa.String(length=64), nullable=False),
        sa.Column("trigger_source", sa.String(length=64), nullable=False),
        sa.Column("input_refs", sa.JSON(), nullable=False),
        sa.Column("output_refs", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("runtime_provider", sa.String(length=64), nullable=True),
        sa.Column("runtime_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_runs_run_type"), "agent_runs", ["run_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_runs_run_type"), table_name="agent_runs")
    op.drop_table("agent_runs")
    op.drop_index(
        op.f("ix_analysis_reports_product_profile_id"),
        table_name="analysis_reports",
    )
    op.drop_index(
        op.f("ix_analysis_reports_lead_analysis_result_id"),
        table_name="analysis_reports",
    )
    op.drop_table("analysis_reports")
    op.drop_index(
        op.f("ix_lead_analysis_results_product_profile_id"),
        table_name="lead_analysis_results",
    )
    op.drop_index(
        op.f("ix_lead_analysis_results_created_by_agent_run_id"),
        table_name="lead_analysis_results",
    )
    op.drop_table("lead_analysis_results")
    op.drop_table("product_profiles")
