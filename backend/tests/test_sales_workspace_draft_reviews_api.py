from __future__ import annotations

import copy
import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.config import reset_settings_cache
from backend.api.main import create_app


EXAMPLE_DIR = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "reference"
    / "api"
    / "examples"
    / "sales_workspace_kernel_v0"
)


def _example(filename: str) -> dict:
    return json.loads((EXAMPLE_DIR / filename).read_text(encoding="utf-8"))


def _build_demo_workspace(client) -> dict:
    create_response = client.post("/sales-workspaces", json=_example("01_create_workspace_request.json"))
    assert create_response.status_code == 201

    for filename, expected_version in [
        ("03_patch_product_direction_request.json", 1),
        ("04_patch_round_1_request.json", 2),
        ("05_patch_round_2_request.json", 3),
    ]:
        response = client.post("/sales-workspaces/ws_demo/patches", json=_example(filename))
        assert response.status_code == 200
        assert response.json()["workspace"]["workspace_version"] == expected_version

    return client.get("/sales-workspaces/ws_demo").json()["workspace"]


def _runtime_patch_draft(client, *, base_workspace_version: int = 3) -> dict:
    preview_response = client.post(
        "/sales-workspaces/ws_demo/runtime/patch-drafts/prototype/preview",
        json={
            "base_workspace_version": base_workspace_version,
            "instruction": "add one deterministic runtime candidate",
        },
    )
    assert preview_response.status_code == 200
    return preview_response.json()["patch_draft"]


def _create_draft_review(client, patch_draft: dict | None = None) -> dict:
    draft = patch_draft or _runtime_patch_draft(client)
    response = client.post("/sales-workspaces/ws_demo/draft-reviews", json={"patch_draft": draft})
    assert response.status_code == 201
    return response.json()["draft_review"]


def _accept_draft_review(client, draft_review_id: str) -> dict:
    response = client.post(
        f"/sales-workspaces/ws_demo/draft-reviews/{draft_review_id}/review",
        json={
            "decision": "accept",
            "reviewed_by": "android_demo_user",
            "comment": "Looks good for demo apply.",
            "client": "android",
        },
    )
    assert response.status_code == 200
    return response.json()["draft_review"]


def test_draft_review_create_get_accept_apply_flow(client) -> None:
    _build_demo_workspace(client)

    draft_review = _create_draft_review(client)
    assert draft_review["id"] == "draft_review_runtime_v4"
    assert draft_review["status"] == "previewed"
    assert draft_review["base_workspace_version"] == 3
    assert draft_review["draft"]["id"] == "draft_runtime_v4"
    assert draft_review["preview"]["materialized_patch"]["id"] == "patch_runtime_v4"
    assert draft_review["preview"]["preview_workspace_version"] == 4
    assert draft_review["preview"]["would_mutate"] is False
    assert draft_review["preview"]["preview_ranking_board"]["ranked_items"][0]["candidate_id"] == "cand_runtime_001"

    workspace_response = client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    workspace = workspace_response.json()["workspace"]
    assert workspace["workspace_version"] == 3
    assert "cand_runtime_001" not in workspace["company_candidates"]

    get_response = client.get("/sales-workspaces/ws_demo/draft-reviews/draft_review_runtime_v4")
    assert get_response.status_code == 200
    assert get_response.json()["draft_review"]["status"] == "previewed"

    reviewed = _accept_draft_review(client, "draft_review_runtime_v4")
    assert reviewed["status"] == "reviewed"
    assert reviewed["review"]["decision"] == "accept"
    assert reviewed["review"]["client"] == "android"

    apply_response = client.post(
        "/sales-workspaces/ws_demo/draft-reviews/draft_review_runtime_v4/apply",
        json={"requested_by": "android_demo_user"},
    )
    assert apply_response.status_code == 200
    payload = apply_response.json()
    assert payload["draft_review"]["status"] == "applied"
    assert payload["draft_review"]["apply_result"]["status"] == "applied"
    assert payload["draft_review"]["apply_result"]["materialized_patch_id"] == "patch_runtime_v4"
    assert payload["workspace"]["workspace_version"] == 4
    assert payload["commit"]["patch_id"] == "patch_runtime_v4"
    assert payload["ranking_board"]["ranked_items"][0]["candidate_id"] == "cand_runtime_001"


def test_draft_review_reject_is_terminal(client) -> None:
    _build_demo_workspace(client)
    _create_draft_review(client)

    reject_response = client.post(
        "/sales-workspaces/ws_demo/draft-reviews/draft_review_runtime_v4/reject",
        json={"rejected_by": "android_demo_user", "reason": "Not enough source evidence."},
    )
    assert reject_response.status_code == 200
    assert reject_response.json()["draft_review"]["status"] == "rejected"
    assert reject_response.json()["draft_review"]["review"]["decision"] == "reject"

    apply_response = client.post(
        "/sales-workspaces/ws_demo/draft-reviews/draft_review_runtime_v4/apply",
        json={"requested_by": "android_demo_user"},
    )
    assert apply_response.status_code == 409
    assert apply_response.json()["error"]["code"] == "draft_review_state_conflict"

    rereview_response = client.post(
        "/sales-workspaces/ws_demo/draft-reviews/draft_review_runtime_v4/review",
        json={"decision": "accept", "reviewed_by": "android_demo_user"},
    )
    assert rereview_response.status_code == 409
    assert rereview_response.json()["error"]["code"] == "draft_review_state_conflict"


def test_draft_review_previewed_cannot_apply_without_accept(client) -> None:
    _build_demo_workspace(client)
    _create_draft_review(client)

    response = client.post(
        "/sales-workspaces/ws_demo/draft-reviews/draft_review_runtime_v4/apply",
        json={"requested_by": "android_demo_user"},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "draft_review_state_conflict"

    workspace_response = client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    workspace = workspace_response.json()["workspace"]
    assert workspace["workspace_version"] == 3
    assert "cand_runtime_001" not in workspace["company_candidates"]


def test_draft_review_stale_accept_expires_review_without_workspace_mutation(client) -> None:
    _build_demo_workspace(client)
    _create_draft_review(client)

    direct_apply_response = client.post(
        "/sales-workspaces/ws_demo/runtime/patch-drafts/prototype",
        json={"base_workspace_version": 3, "instruction": "advance workspace before review"},
    )
    assert direct_apply_response.status_code == 200
    assert direct_apply_response.json()["workspace"]["workspace_version"] == 4

    accept_response = client.post(
        "/sales-workspaces/ws_demo/draft-reviews/draft_review_runtime_v4/review",
        json={"decision": "accept", "reviewed_by": "android_demo_user"},
    )
    assert accept_response.status_code == 409
    assert accept_response.json()["error"]["code"] == "workspace_version_conflict"

    get_response = client.get("/sales-workspaces/ws_demo/draft-reviews/draft_review_runtime_v4")
    assert get_response.status_code == 200
    assert get_response.json()["draft_review"]["status"] == "expired"

    workspace_response = client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    assert workspace_response.json()["workspace"]["workspace_version"] == 4


def test_draft_review_stale_apply_expires_review_without_second_write(client) -> None:
    _build_demo_workspace(client)
    _create_draft_review(client)
    _accept_draft_review(client, "draft_review_runtime_v4")

    direct_apply_response = client.post(
        "/sales-workspaces/ws_demo/runtime/patch-drafts/prototype",
        json={"base_workspace_version": 3, "instruction": "advance workspace before reviewed apply"},
    )
    assert direct_apply_response.status_code == 200
    assert direct_apply_response.json()["workspace"]["workspace_version"] == 4

    stale_apply_response = client.post(
        "/sales-workspaces/ws_demo/draft-reviews/draft_review_runtime_v4/apply",
        json={"requested_by": "android_demo_user"},
    )
    assert stale_apply_response.status_code == 409
    assert stale_apply_response.json()["error"]["code"] == "workspace_version_conflict"

    get_response = client.get("/sales-workspaces/ws_demo/draft-reviews/draft_review_runtime_v4")
    assert get_response.status_code == 200
    draft_review = get_response.json()["draft_review"]
    assert draft_review["status"] == "expired"
    assert draft_review["apply_result"]["status"] == "failed"
    assert draft_review["apply_result"]["error_code"] == "workspace_version_conflict"

    workspace_response = client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    workspace = workspace_response.json()["workspace"]
    assert workspace["workspace_version"] == 4
    assert len(workspace["commits"]) == 4


def test_draft_review_json_store_survives_app_restart(backend_env, monkeypatch, tmp_path) -> None:
    store_dir = tmp_path / "sales_workspace_store"
    monkeypatch.setenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR", str(store_dir))
    reset_settings_cache()

    with TestClient(create_app()) as first_client:
        _build_demo_workspace(first_client)
        _create_draft_review(first_client)

    review_file = store_dir / "draft_reviews" / "ws_demo" / "draft_review_runtime_v4.json"
    assert review_file.exists()
    assert json.loads(review_file.read_text(encoding="utf-8"))["status"] == "previewed"

    reset_settings_cache()
    with TestClient(create_app()) as second_client:
        get_response = second_client.get("/sales-workspaces/ws_demo/draft-reviews/draft_review_runtime_v4")
        assert get_response.status_code == 200
        assert get_response.json()["draft_review"]["status"] == "previewed"

        reviewed = _accept_draft_review(second_client, "draft_review_runtime_v4")
        assert reviewed["status"] == "reviewed"

        apply_response = second_client.post(
            "/sales-workspaces/ws_demo/draft-reviews/draft_review_runtime_v4/apply",
            json={"requested_by": "android_demo_user"},
        )
        assert apply_response.status_code == 200
        assert apply_response.json()["workspace"]["workspace_version"] == 4
        assert apply_response.json()["ranking_board"]["ranked_items"][0]["candidate_id"] == "cand_runtime_001"


def test_draft_review_path_mismatch_missing_and_invalid_draft(client) -> None:
    _build_demo_workspace(client)
    patch_draft = _runtime_patch_draft(client)

    mismatch_draft = copy.deepcopy(patch_draft)
    mismatch_draft["workspace_id"] = "ws_other"
    mismatch_response = client.post("/sales-workspaces/ws_demo/draft-reviews", json={"patch_draft": mismatch_draft})
    assert mismatch_response.status_code == 422
    assert mismatch_response.json()["error"]["code"] == "validation_error"

    missing_workspace_response = client.post(
        "/sales-workspaces/ws_missing/draft-reviews",
        json={"patch_draft": {**patch_draft, "workspace_id": "ws_missing"}},
    )
    assert missing_workspace_response.status_code == 404
    assert missing_workspace_response.json()["error"]["code"] == "not_found"

    missing_review_response = client.get("/sales-workspaces/ws_demo/draft-reviews/draft_review_missing")
    assert missing_review_response.status_code == 404
    assert missing_review_response.json()["error"]["code"] == "not_found"

    invalid_response = client.post(
        "/sales-workspaces/ws_demo/draft-reviews",
        json={
            "patch_draft": {
                "id": "draft_invalid",
                "workspace_id": "ws_demo",
                "base_workspace_version": 3,
                "operations": [],
            }
        },
    )
    assert invalid_response.status_code == 422
    assert invalid_response.json()["error"]["code"] == "patchdraft_validation_error"
