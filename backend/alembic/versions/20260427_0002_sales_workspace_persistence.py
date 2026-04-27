"""sales workspace persistence

Revision ID: 20260427_0002
Revises: 20260423_0001
Create Date: 2026-04-27 00:02:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260427_0002"
down_revision = "20260423_0001"
branch_labels = None
depends_on = None


def _json_payload() -> sa.TypeEngine:
    return sa.JSON().with_variant(postgresql.JSONB(none_as_null=False), "postgresql")


def upgrade() -> None:
    op.create_table(
        "sales_workspaces",
        sa.Column("workspace_id", sa.Text(), nullable=False),
        sa.Column("workspace_key", sa.Text(), nullable=False),
        sa.Column("owner_id", sa.Text(), nullable=True),
        sa.Column("tenant_id", sa.Text(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("workspace_version", sa.Integer(), nullable=False),
        sa.Column("current_product_profile_revision_id", sa.Text(), nullable=True),
        sa.Column("current_lead_direction_id", sa.Text(), nullable=True),
        sa.Column("latest_research_round_id", sa.Text(), nullable=True),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("created_by", sa.Text(), nullable=True),
        sa.Column("updated_by", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status in ('active', 'archived')", name="ck_sales_workspaces_status"),
        sa.CheckConstraint("workspace_version >= 0", name="ck_sales_workspaces_workspace_version"),
        sa.PrimaryKeyConstraint("workspace_id"),
    )
    op.create_index("ix_sales_workspaces_workspace_key", "sales_workspaces", ["workspace_key"])
    op.create_index("ix_sales_workspaces_owner_id", "sales_workspaces", ["owner_id"])
    op.create_index("ix_sales_workspaces_tenant_id", "sales_workspaces", ["tenant_id"])
    op.create_index("ix_sales_workspaces_status", "sales_workspaces", ["status"])
    op.create_index("ix_sales_workspaces_updated_at", "sales_workspaces", ["updated_at"])

    op.create_table(
        "sales_workspace_product_profile_revisions",
        sa.Column("workspace_id", sa.Text(), nullable=False),
        sa.Column("revision_id", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("product_name", sa.Text(), nullable=False),
        sa.Column("one_liner", sa.Text(), nullable=False, server_default=""),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("version >= 1", name="ck_sales_workspace_profile_revisions_version"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["sales_workspaces.workspace_id"],
            name="fk_sales_workspace_profile_revisions_workspace_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("workspace_id", "revision_id"),
    )

    op.create_table(
        "sales_workspace_lead_directions",
        sa.Column("workspace_id", sa.Text(), nullable=False),
        sa.Column("direction_id", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("change_reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("version >= 1", name="ck_sales_workspace_lead_directions_version"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["sales_workspaces.workspace_id"],
            name="fk_sales_workspace_lead_directions_workspace_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("workspace_id", "direction_id"),
    )

    op.create_table(
        "sales_workspace_lead_candidates",
        sa.Column("workspace_id", sa.Text(), nullable=False),
        sa.Column("candidate_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("industry", sa.Text(), nullable=False, server_default=""),
        sa.Column("region", sa.Text(), nullable=False, server_default=""),
        sa.Column("company_size", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status in ('active', 'archived')", name="ck_sales_workspace_lead_candidates_status"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["sales_workspaces.workspace_id"],
            name="fk_sales_workspace_lead_candidates_workspace_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("workspace_id", "candidate_id"),
    )
    op.create_index(
        "ix_sales_workspace_lead_candidates_workspace_status",
        "sales_workspace_lead_candidates",
        ["workspace_id", "status"],
    )
    op.create_index(
        "ix_sales_workspace_lead_candidates_workspace_name",
        "sales_workspace_lead_candidates",
        ["workspace_id", "name"],
    )
    op.create_index(
        "ix_sales_workspace_lead_candidates_workspace_updated_at",
        "sales_workspace_lead_candidates",
        ["workspace_id", "updated_at"],
    )

    op.create_table(
        "sales_workspace_research_sources",
        sa.Column("workspace_id", sa.Text(), nullable=False),
        sa.Column("source_id", sa.Text(), nullable=False),
        sa.Column("round_id", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column("reliability", sa.Text(), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=False, server_default=""),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "reliability in ('low', 'medium', 'high')",
            name="ck_sales_workspace_research_sources_reliability",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["sales_workspaces.workspace_id"],
            name="fk_sales_workspace_research_sources_workspace_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("workspace_id", "source_id"),
    )
    op.create_index(
        "ix_sales_workspace_research_sources_workspace_round",
        "sales_workspace_research_sources",
        ["workspace_id", "round_id"],
    )
    op.create_index(
        "ix_sales_workspace_research_sources_workspace_url",
        "sales_workspace_research_sources",
        ["workspace_id", "url"],
    )

    op.create_table(
        "sales_workspace_research_observations",
        sa.Column("workspace_id", sa.Text(), nullable=False),
        sa.Column("observation_id", sa.Text(), nullable=False),
        sa.Column("candidate_id", sa.Text(), nullable=False),
        sa.Column("source_id", sa.Text(), nullable=False),
        sa.Column("round_id", sa.Text(), nullable=False),
        sa.Column("signal_type", sa.Text(), nullable=False),
        sa.Column("polarity", sa.Text(), nullable=False),
        sa.Column("strength", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("payload_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "signal_type in ('fit', 'pain', 'timing', 'region', 'source_quality', 'exclusion', 'other')",
            name="ck_sales_workspace_research_observations_signal_type",
        ),
        sa.CheckConstraint("polarity in ('positive', 'negative')", name="ck_sales_workspace_observations_polarity"),
        sa.CheckConstraint("strength >= 1 and strength <= 5", name="ck_sales_workspace_observations_strength"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["sales_workspaces.workspace_id"],
            name="fk_sales_workspace_research_observations_workspace_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id", "candidate_id"],
            ["sales_workspace_lead_candidates.workspace_id", "sales_workspace_lead_candidates.candidate_id"],
            name="fk_sales_workspace_observations_candidate",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id", "source_id"],
            ["sales_workspace_research_sources.workspace_id", "sales_workspace_research_sources.source_id"],
            name="fk_sales_workspace_observations_source",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("workspace_id", "observation_id"),
    )
    op.create_index(
        "ix_sales_workspace_research_observations_workspace_candidate",
        "sales_workspace_research_observations",
        ["workspace_id", "candidate_id"],
    )
    op.create_index(
        "ix_sales_workspace_research_observations_workspace_source",
        "sales_workspace_research_observations",
        ["workspace_id", "source_id"],
    )
    op.create_index(
        "ix_sales_workspace_research_observations_workspace_round",
        "sales_workspace_research_observations",
        ["workspace_id", "round_id"],
    )
    op.create_index(
        "ix_sales_workspace_research_observations_workspace_signal_type",
        "sales_workspace_research_observations",
        ["workspace_id", "signal_type"],
    )

    op.create_table(
        "sales_workspace_patch_commits",
        sa.Column("workspace_id", sa.Text(), nullable=False),
        sa.Column("commit_id", sa.Text(), nullable=False),
        sa.Column("patch_id", sa.Text(), nullable=False),
        sa.Column("base_workspace_version", sa.Integer(), nullable=False),
        sa.Column("resulting_workspace_version", sa.Integer(), nullable=False),
        sa.Column("author", sa.Text(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False, server_default=""),
        sa.Column("operation_count", sa.Integer(), nullable=False),
        sa.Column("changed_object_refs", _json_payload(), nullable=False),
        sa.Column("patch_json", _json_payload(), nullable=False),
        sa.Column("commit_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("base_workspace_version >= 0", name="ck_sales_workspace_patch_commits_base_version"),
        sa.CheckConstraint(
            "resulting_workspace_version = base_workspace_version + 1",
            name="ck_sales_workspace_patch_commits_resulting_version",
        ),
        sa.CheckConstraint("operation_count >= 1", name="ck_sales_workspace_patch_commits_operation_count"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["sales_workspaces.workspace_id"],
            name="fk_sales_workspace_patch_commits_workspace_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("workspace_id", "commit_id"),
        sa.UniqueConstraint("workspace_id", "patch_id", name="uq_sales_workspace_patch_commits_patch_id"),
        sa.UniqueConstraint(
            "workspace_id",
            "resulting_workspace_version",
            name="uq_sales_workspace_patch_commits_resulting_version",
        ),
    )
    op.create_index(
        "ix_sales_workspace_patch_commits_workspace_created_at",
        "sales_workspace_patch_commits",
        ["workspace_id", "created_at"],
    )
    op.create_index(
        "ix_sales_workspace_patch_commits_workspace_base_version",
        "sales_workspace_patch_commits",
        ["workspace_id", "base_workspace_version"],
    )

    op.create_table(
        "sales_workspace_draft_reviews",
        sa.Column("workspace_id", sa.Text(), nullable=False),
        sa.Column("draft_review_id", sa.Text(), nullable=False),
        sa.Column("draft_id", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("base_workspace_version", sa.Integer(), nullable=False),
        sa.Column("instruction", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.Text(), nullable=False),
        sa.Column("reviewed_by", sa.Text(), nullable=True),
        sa.Column("applied_commit_id", sa.Text(), nullable=True),
        sa.Column("failure_code", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("draft_json", _json_payload(), nullable=False),
        sa.Column("preview_json", _json_payload(), nullable=False),
        sa.Column("review_json", _json_payload(), nullable=True),
        sa.Column("apply_result_json", _json_payload(), nullable=True),
        sa.Column("runtime_metadata", _json_payload(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status in ('previewed', 'reviewed', 'applied', 'rejected', 'expired')",
            name="ck_sales_workspace_draft_reviews_status",
        ),
        sa.CheckConstraint("base_workspace_version >= 0", name="ck_sales_workspace_draft_reviews_base_version"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["sales_workspaces.workspace_id"],
            name="fk_sales_workspace_draft_reviews_workspace_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id", "applied_commit_id"],
            ["sales_workspace_patch_commits.workspace_id", "sales_workspace_patch_commits.commit_id"],
            name="fk_sales_workspace_draft_reviews_applied_commit",
        ),
        sa.PrimaryKeyConstraint("workspace_id", "draft_review_id"),
    )
    op.create_index(
        "ix_sales_workspace_draft_reviews_workspace_status",
        "sales_workspace_draft_reviews",
        ["workspace_id", "status"],
    )
    op.create_index(
        "ix_sales_workspace_draft_reviews_workspace_base_version",
        "sales_workspace_draft_reviews",
        ["workspace_id", "base_workspace_version"],
    )
    op.create_index(
        "ix_sales_workspace_draft_reviews_workspace_updated_at",
        "sales_workspace_draft_reviews",
        ["workspace_id", "updated_at"],
    )

    op.create_table(
        "sales_workspace_draft_review_events",
        sa.Column("workspace_id", sa.Text(), nullable=False),
        sa.Column("draft_review_id", sa.Text(), nullable=False),
        sa.Column("event_id", sa.Text(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("from_status", sa.Text(), nullable=True),
        sa.Column("to_status", sa.Text(), nullable=False),
        sa.Column("actor_type", sa.Text(), nullable=False),
        sa.Column("actor_id", sa.Text(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("event_json", _json_payload(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "event_type in ('created', 'reviewed', 'rejected', 'applied', 'expired', 'apply_failed')",
            name="ck_sales_workspace_draft_review_events_event_type",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id", "draft_review_id"],
            ["sales_workspace_draft_reviews.workspace_id", "sales_workspace_draft_reviews.draft_review_id"],
            name="fk_sales_workspace_draft_review_events_review",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("workspace_id", "event_id"),
    )
    op.create_index(
        "ix_sales_workspace_draft_review_events_review_created_at",
        "sales_workspace_draft_review_events",
        ["workspace_id", "draft_review_id", "created_at"],
    )
    op.create_index(
        "ix_sales_workspace_draft_review_events_workspace_event_type",
        "sales_workspace_draft_review_events",
        ["workspace_id", "event_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_sales_workspace_draft_review_events_workspace_event_type", table_name="sales_workspace_draft_review_events")
    op.drop_index("ix_sales_workspace_draft_review_events_review_created_at", table_name="sales_workspace_draft_review_events")
    op.drop_table("sales_workspace_draft_review_events")

    op.drop_index("ix_sales_workspace_draft_reviews_workspace_updated_at", table_name="sales_workspace_draft_reviews")
    op.drop_index("ix_sales_workspace_draft_reviews_workspace_base_version", table_name="sales_workspace_draft_reviews")
    op.drop_index("ix_sales_workspace_draft_reviews_workspace_status", table_name="sales_workspace_draft_reviews")
    op.drop_table("sales_workspace_draft_reviews")

    op.drop_index("ix_sales_workspace_patch_commits_workspace_base_version", table_name="sales_workspace_patch_commits")
    op.drop_index("ix_sales_workspace_patch_commits_workspace_created_at", table_name="sales_workspace_patch_commits")
    op.drop_table("sales_workspace_patch_commits")

    op.drop_index(
        "ix_sales_workspace_research_observations_workspace_signal_type",
        table_name="sales_workspace_research_observations",
    )
    op.drop_index(
        "ix_sales_workspace_research_observations_workspace_round",
        table_name="sales_workspace_research_observations",
    )
    op.drop_index(
        "ix_sales_workspace_research_observations_workspace_source",
        table_name="sales_workspace_research_observations",
    )
    op.drop_index(
        "ix_sales_workspace_research_observations_workspace_candidate",
        table_name="sales_workspace_research_observations",
    )
    op.drop_table("sales_workspace_research_observations")

    op.drop_index("ix_sales_workspace_research_sources_workspace_url", table_name="sales_workspace_research_sources")
    op.drop_index("ix_sales_workspace_research_sources_workspace_round", table_name="sales_workspace_research_sources")
    op.drop_table("sales_workspace_research_sources")

    op.drop_index("ix_sales_workspace_lead_candidates_workspace_updated_at", table_name="sales_workspace_lead_candidates")
    op.drop_index("ix_sales_workspace_lead_candidates_workspace_name", table_name="sales_workspace_lead_candidates")
    op.drop_index("ix_sales_workspace_lead_candidates_workspace_status", table_name="sales_workspace_lead_candidates")
    op.drop_table("sales_workspace_lead_candidates")

    op.drop_table("sales_workspace_lead_directions")
    op.drop_table("sales_workspace_product_profile_revisions")

    op.drop_index("ix_sales_workspaces_updated_at", table_name="sales_workspaces")
    op.drop_index("ix_sales_workspaces_status", table_name="sales_workspaces")
    op.drop_index("ix_sales_workspaces_tenant_id", table_name="sales_workspaces")
    op.drop_index("ix_sales_workspaces_owner_id", table_name="sales_workspaces")
    op.drop_index("ix_sales_workspaces_workspace_key", table_name="sales_workspaces")
    op.drop_table("sales_workspaces")
