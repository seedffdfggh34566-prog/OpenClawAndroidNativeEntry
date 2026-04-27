from __future__ import annotations

import copy
import json
import os
from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.api.config import reset_settings_cache
from backend.api.database import get_session_factory, reset_database_state
from backend.api.main import create_app

POSTGRES_VERIFY_ENV = "OPENCLAW_BACKEND_POSTGRES_VERIFY_URL"

EXAMPLE_DIR = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "reference"
    / "api"
    / "examples"
    / "sales_workspace_kernel_v0"
)


@pytest.fixture
def postgres_draft_review_client(monkeypatch) -> Generator[TestClient, None, None]:
    database_url = os.environ.get(POSTGRES_VERIFY_ENV)
    if not database_url:
        pytest.skip(f"set {POSTGRES_VERIFY_ENV} to run Postgres Draft Review verification")

    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", database_url)
    monkeypatch.setenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND", "postgres")
    monkeypatch.delenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR", raising=False)
    reset_settings_cache()
    reset_database_state()
    with TestClient(create_app()) as client:
        yield client
    reset_database_state()
    reset_settings_cache()


def test_draft_review_postgres_create_get_accept_apply_events(postgres_draft_review_client) -> None:
    workspace_id = _workspace_id()
    _build_demo_workspace(postgres_draft_review_client, workspace_id)

    draft_review = _create_draft_review(postgres_draft_review_client, workspace_id)
    draft_review_id = draft_review["id"]
    assert draft_review["status"] == "previewed"
    assert draft_review["preview"]["preview_ranking_board"]["ranked_items"][0]["candidate_id"] == "cand_runtime_001"
    assert _event_types(workspace_id, draft_review_id) == ["created"]

    get_response = postgres_draft_review_client.get(
        f"/sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}"
    )
    assert get_response.status_code == 200
    assert get_response.json()["draft_review"]["status"] == "previewed"

    review_response = postgres_draft_review_client.post(
        f"/sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/review",
        json={
            "decision": "accept",
            "reviewed_by": "android_demo_user",
            "comment": "Accept postgres review.",
            "client": "android",
        },
    )
    assert review_response.status_code == 200
    assert review_response.json()["draft_review"]["status"] == "reviewed"
    assert _event_types(workspace_id, draft_review_id) == ["created", "reviewed"]

    apply_response = postgres_draft_review_client.post(
        f"/sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/apply",
        json={"requested_by": "android_demo_user"},
    )
    assert apply_response.status_code == 200
    payload = apply_response.json()
    assert payload["draft_review"]["status"] == "applied"
    assert payload["workspace"]["workspace_version"] == 4
    assert payload["ranking_board"]["ranked_items"][0]["candidate_id"] == "cand_runtime_001"
    assert _event_types(workspace_id, draft_review_id) == ["created", "reviewed", "applied"]


def test_draft_review_postgres_reject_is_terminal_and_audited(postgres_draft_review_client) -> None:
    workspace_id = _workspace_id()
    _build_demo_workspace(postgres_draft_review_client, workspace_id)
    draft_review_id = _create_draft_review(postgres_draft_review_client, workspace_id)["id"]

    reject_response = postgres_draft_review_client.post(
        f"/sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/reject",
        json={"rejected_by": "android_demo_user", "reason": "Need more evidence."},
    )
    assert reject_response.status_code == 200
    assert reject_response.json()["draft_review"]["status"] == "rejected"
    assert _event_types(workspace_id, draft_review_id) == ["created", "rejected"]

    apply_response = postgres_draft_review_client.post(
        f"/sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/apply",
        json={"requested_by": "android_demo_user"},
    )
    assert apply_response.status_code == 409
    assert apply_response.json()["error"]["code"] == "draft_review_state_conflict"


def test_draft_review_postgres_stale_apply_expires_without_second_workspace_write(
    postgres_draft_review_client,
) -> None:
    workspace_id = _workspace_id()
    _build_demo_workspace(postgres_draft_review_client, workspace_id)
    draft_review_id = _create_draft_review(postgres_draft_review_client, workspace_id)["id"]

    review_response = postgres_draft_review_client.post(
        f"/sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/review",
        json={"decision": "accept", "reviewed_by": "android_demo_user"},
    )
    assert review_response.status_code == 200

    direct_apply_response = postgres_draft_review_client.post(
        f"/sales-workspaces/{workspace_id}/runtime/patch-drafts/prototype",
        json={"base_workspace_version": 3, "instruction": "advance workspace before reviewed apply"},
    )
    assert direct_apply_response.status_code == 200
    assert direct_apply_response.json()["workspace"]["workspace_version"] == 4

    stale_apply_response = postgres_draft_review_client.post(
        f"/sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/apply",
        json={"requested_by": "android_demo_user"},
    )
    assert stale_apply_response.status_code == 409
    assert stale_apply_response.json()["error"]["code"] == "workspace_version_conflict"

    get_response = postgres_draft_review_client.get(
        f"/sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}"
    )
    assert get_response.status_code == 200
    draft_review = get_response.json()["draft_review"]
    assert draft_review["status"] == "expired"
    assert draft_review["apply_result"]["status"] == "failed"
    assert draft_review["apply_result"]["error_code"] == "workspace_version_conflict"

    workspace_response = postgres_draft_review_client.get(f"/sales-workspaces/{workspace_id}")
    assert workspace_response.status_code == 200
    assert workspace_response.json()["workspace"]["workspace_version"] == 4
    assert _event_types(workspace_id, draft_review_id) == [
        "created",
        "reviewed",
        "expired",
        "apply_failed",
    ]


def _build_demo_workspace(client: TestClient, workspace_id: str) -> None:
    response = client.post(
        "/sales-workspaces",
        json={
            **_example("01_create_workspace_request.json"),
            "workspace_id": workspace_id,
        },
    )
    assert response.status_code == 201

    for filename, expected_version in [
        ("03_patch_product_direction_request.json", 1),
        ("04_patch_round_1_request.json", 2),
        ("05_patch_round_2_request.json", 3),
    ]:
        response = client.post(
            f"/sales-workspaces/{workspace_id}/patches",
            json=_patch_example(filename, workspace_id),
        )
        assert response.status_code == 200
        assert response.json()["workspace"]["workspace_version"] == expected_version


def _create_draft_review(client: TestClient, workspace_id: str) -> dict:
    preview_response = client.post(
        f"/sales-workspaces/{workspace_id}/runtime/patch-drafts/prototype/preview",
        json={
            "base_workspace_version": 3,
            "instruction": "add one deterministic runtime candidate",
        },
    )
    assert preview_response.status_code == 200
    response = client.post(
        f"/sales-workspaces/{workspace_id}/draft-reviews",
        json={"patch_draft": preview_response.json()["patch_draft"]},
    )
    assert response.status_code == 201
    return response.json()["draft_review"]


def _event_types(workspace_id: str, draft_review_id: str) -> list[str]:
    session = get_session_factory()()
    try:
        rows = session.execute(
            text(
                """
                select event_type
                from sales_workspace_draft_review_events
                where workspace_id = :workspace_id
                  and draft_review_id = :draft_review_id
                order by event_id
                """
            ),
            {"workspace_id": workspace_id, "draft_review_id": draft_review_id},
        ).all()
    finally:
        session.close()
    return [row.event_type for row in rows]


def _workspace_id() -> str:
    return f"ws_review_pg_{uuid4().hex[:12]}"


def _patch_example(filename: str, workspace_id: str) -> dict:
    payload = copy.deepcopy(_example(filename))
    payload["patch"]["workspace_id"] = workspace_id
    payload["patch"]["id"] = f'{payload["patch"]["id"]}_{workspace_id}'
    return payload


def _example(filename: str) -> dict:
    return json.loads((EXAMPLE_DIR / filename).read_text(encoding="utf-8"))
