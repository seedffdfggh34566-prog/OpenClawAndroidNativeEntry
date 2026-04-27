from __future__ import annotations

import os
from collections.abc import Generator
from uuid import uuid4

import pytest
from sqlalchemy import text

from backend.api.config import reset_settings_cache
from backend.api.database import get_session_factory, init_db, reset_database_state
from backend.sales_workspace.context_pack import compile_context_pack
from backend.sales_workspace.patches import WorkspaceVersionConflict
from backend.sales_workspace.projection import render_markdown_projection
from backend.sales_workspace.repository import PostgresWorkspaceStore
from backend.sales_workspace.schemas import WorkspaceOperation, WorkspacePatch

POSTGRES_VERIFY_ENV = "OPENCLAW_BACKEND_POSTGRES_VERIFY_URL"


@pytest.fixture
def postgres_workspace_store(monkeypatch) -> Generator[PostgresWorkspaceStore, None, None]:
    database_url = os.environ.get(POSTGRES_VERIFY_ENV)
    if not database_url:
        pytest.skip(f"set {POSTGRES_VERIFY_ENV} to run Postgres repository verification")

    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", database_url)
    reset_settings_cache()
    reset_database_state()
    init_db()
    yield PostgresWorkspaceStore()
    reset_database_state()
    reset_settings_cache()


def test_postgres_workspace_repository_create_get_and_save(postgres_workspace_store) -> None:
    workspace_id = _workspace_id()
    workspace = postgres_workspace_store.create_workspace(
        workspace_id=workspace_id,
        name="Repository Demo",
        goal="Persist a workspace",
        owner_id="repo_test_user",
        workspace_key="repo_demo",
    )

    loaded = postgres_workspace_store.get(workspace_id)
    assert loaded.id == workspace.id
    assert loaded.workspace_version == 0
    assert loaded.owner_id == "repo_test_user"

    updated = loaded.model_copy(update={"goal": "Updated goal"})
    postgres_workspace_store.save(updated)

    reloaded = postgres_workspace_store.get(workspace_id)
    assert reloaded.goal == "Updated goal"


def test_postgres_workspace_repository_apply_patch_and_reload_derived_outputs(postgres_workspace_store) -> None:
    workspace_id = _workspace_id()
    postgres_workspace_store.create_workspace(
        workspace_id=workspace_id,
        name="Repository Patch Demo",
        goal="Persist patch results",
    )

    updated = postgres_workspace_store.apply_patch(_demo_patch(workspace_id, base_workspace_version=0))
    assert updated.workspace_version == 1
    assert updated.commits[-1].patch_id.startswith("patch_")
    assert updated.ranking_board is not None
    assert updated.ranking_board.ranked_items[0].candidate_id == f"{workspace_id}_cand"

    reloaded = postgres_workspace_store.get(workspace_id)
    assert reloaded.workspace_version == 1
    assert reloaded.current_product_profile_revision_id == f"{workspace_id}_product"
    assert reloaded.ranking_board is not None
    assert "rankings/current.md" in render_markdown_projection(reloaded)
    assert compile_context_pack(reloaded).top_candidates[0].candidate_id == f"{workspace_id}_cand"

    session = get_session_factory()()
    try:
        commit_count = session.execute(
            text("select count(*) from sales_workspace_patch_commits where workspace_id = :workspace_id"),
            {"workspace_id": workspace_id},
        ).scalar_one()
    finally:
        session.close()
    assert commit_count == 1


def test_postgres_workspace_repository_version_conflict_does_not_mutate(postgres_workspace_store) -> None:
    workspace_id = _workspace_id()
    postgres_workspace_store.create_workspace(
        workspace_id=workspace_id,
        name="Repository Conflict Demo",
    )
    postgres_workspace_store.apply_patch(_demo_patch(workspace_id, base_workspace_version=0))

    with pytest.raises(WorkspaceVersionConflict):
        postgres_workspace_store.apply_patch(_demo_patch(workspace_id, base_workspace_version=0, suffix="stale"))

    reloaded = postgres_workspace_store.get(workspace_id)
    assert reloaded.workspace_version == 1
    assert len(reloaded.commits) == 1

    session = get_session_factory()()
    try:
        commit_count = session.execute(
            text("select count(*) from sales_workspace_patch_commits where workspace_id = :workspace_id"),
            {"workspace_id": workspace_id},
        ).scalar_one()
    finally:
        session.close()
    assert commit_count == 1


def _workspace_id() -> str:
    return f"ws_repo_{uuid4().hex[:12]}"


def _demo_patch(workspace_id: str, *, base_workspace_version: int, suffix: str = "v1") -> WorkspacePatch:
    return WorkspacePatch(
        id=f"patch_{workspace_id}_{suffix}",
        workspace_id=workspace_id,
        base_workspace_version=base_workspace_version,
        author="repository_test",
        message="Persist repository demo patch",
        operations=[
            WorkspaceOperation(
                type="upsert_product_profile_revision",
                payload={
                    "id": f"{workspace_id}_product",
                    "product_name": "Repository AI",
                    "one_liner": "Helps persist structured sales workspaces.",
                    "target_customers": ["sales teams"],
                    "target_industries": ["software"],
                    "pain_points": ["workspace state disappears"],
                    "value_props": ["durable workspace memory"],
                },
            ),
            WorkspaceOperation(
                type="upsert_lead_direction_version",
                payload={
                    "id": f"{workspace_id}_direction",
                    "priority_industries": ["software"],
                    "target_customer_types": ["operations leaders"],
                    "regions": ["US"],
                    "company_sizes": ["mid-market"],
                    "change_reason": "repository test",
                },
            ),
            WorkspaceOperation(
                type="upsert_research_round",
                payload={
                    "id": f"{workspace_id}_round",
                    "round_index": 1,
                    "objective": "Find a durable candidate",
                    "summary": "Repository-backed research round.",
                },
            ),
            WorkspaceOperation(
                type="upsert_research_source",
                payload={
                    "id": f"{workspace_id}_source",
                    "round_id": f"{workspace_id}_round",
                    "title": "Repository source",
                    "url": "https://example.com/repository-source",
                    "source_type": "public_web",
                    "reliability": "high",
                    "excerpt": "Evidence that the candidate fits.",
                },
            ),
            WorkspaceOperation(
                type="upsert_company_candidate",
                payload={
                    "id": f"{workspace_id}_cand",
                    "name": "Repository Candidate Co",
                    "summary": "A candidate for repository testing.",
                    "industry": "software",
                    "region": "US",
                    "company_size": "mid-market",
                    "round_ids": [f"{workspace_id}_round"],
                },
            ),
            WorkspaceOperation(
                type="upsert_candidate_observation",
                payload={
                    "id": f"{workspace_id}_obs",
                    "candidate_id": f"{workspace_id}_cand",
                    "source_id": f"{workspace_id}_source",
                    "round_id": f"{workspace_id}_round",
                    "signal_type": "fit",
                    "summary": "Candidate matches the target profile.",
                    "polarity": "positive",
                    "strength": 5,
                },
            ),
        ],
    )
