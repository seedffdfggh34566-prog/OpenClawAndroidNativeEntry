from __future__ import annotations

from sqlalchemy import inspect

from backend.api.database import get_engine, init_db


SALES_WORKSPACE_TABLES = {
    "sales_workspaces",
    "sales_workspace_product_profile_revisions",
    "sales_workspace_lead_directions",
    "sales_workspace_lead_candidates",
    "sales_workspace_research_sources",
    "sales_workspace_research_observations",
    "sales_workspace_patch_commits",
    "sales_workspace_draft_reviews",
    "sales_workspace_draft_review_events",
    "sales_workspace_conversation_messages",
    "sales_workspace_conversation_threads",
    "sales_workspace_agent_runs",
    "sales_workspace_context_packs",
}


def test_sales_workspace_persistence_schema_tables_exist(backend_env) -> None:
    init_db()

    inspector = inspect(get_engine())
    table_names = set(inspector.get_table_names())

    assert SALES_WORKSPACE_TABLES.issubset(table_names)


def test_sales_workspace_persistence_schema_core_columns_exist(backend_env) -> None:
    init_db()

    inspector = inspect(get_engine())
    columns_by_table = {
        table: {column["name"] for column in inspector.get_columns(table)}
        for table in SALES_WORKSPACE_TABLES
    }

    assert {
        "workspace_id",
        "workspace_version",
        "payload_json",
        "created_at",
        "updated_at",
    }.issubset(columns_by_table["sales_workspaces"])
    assert {"workspace_id", "patch_id", "base_workspace_version", "resulting_workspace_version"}.issubset(
        columns_by_table["sales_workspace_patch_commits"]
    )
    assert {"workspace_id", "draft_review_id", "status", "draft_json", "preview_json"}.issubset(
        columns_by_table["sales_workspace_draft_reviews"]
    )
    assert {"workspace_id", "draft_review_id", "event_id", "event_type", "event_json"}.issubset(
        columns_by_table["sales_workspace_draft_review_events"]
    )
    assert {"workspace_id", "thread_id", "message_id", "role", "message_type", "content", "payload_json"}.issubset(
        columns_by_table["sales_workspace_conversation_messages"]
    )
    assert {"workspace_id", "thread_id", "title", "status", "payload_json"}.issubset(
        columns_by_table["sales_workspace_conversation_threads"]
    )
    assert {"workspace_id", "thread_id", "agent_run_id", "run_type", "status", "input_refs_json", "output_refs_json"}.issubset(
        columns_by_table["sales_workspace_agent_runs"]
    )
    assert {"workspace_id", "thread_id", "context_pack_id", "agent_run_id", "task_type", "payload_json"}.issubset(
        columns_by_table["sales_workspace_context_packs"]
    )
