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
        payload = response.json()
        assert payload["workspace"]["workspace_version"] == expected_version

    return client.get("/sales-workspaces/ws_demo").json()["workspace"]


def test_sales_workspace_contract_examples_flow(client) -> None:
    workspace = _build_demo_workspace(client)
    assert workspace["id"] == "ws_demo"
    assert workspace["workspace_version"] == 3

    duplicate_response = client.post("/sales-workspaces", json=_example("01_create_workspace_request.json"))
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["error"]["code"] == "workspace_already_exists"

    ranking_response = client.get("/sales-workspaces/ws_demo/ranking-board/current")
    assert ranking_response.status_code == 200
    ranking_board = ranking_response.json()["ranking_board"]
    assert ranking_board["ranked_items"][0]["candidate_id"] == "cand_d"

    projection_response = client.get("/sales-workspaces/ws_demo/projection")
    assert projection_response.status_code == 200
    projection = projection_response.json()
    assert projection["workspace_version"] == 3
    assert "rankings/current.md" in projection["files"]
    assert "generated: true" in projection["files"]["rankings/current.md"]

    context_pack_response = client.post(
        "/sales-workspaces/ws_demo/context-packs",
        json={"task_type": "research_round", "token_budget_chars": 6000, "top_n_candidates": 5},
    )
    assert context_pack_response.status_code == 200
    context_pack = context_pack_response.json()["context_pack"]
    assert context_pack["top_candidates"][0]["candidate_id"] == "cand_d"
    assert "Runtime / Product Sales Agent execution layer" in context_pack["kernel_boundary"]


def test_sales_workspace_version_conflict_does_not_mutate(client) -> None:
    _build_demo_workspace(client)

    conflict_request = _example("05_patch_round_2_request.json")
    conflict_response = client.post("/sales-workspaces/ws_demo/patches", json=conflict_request)
    assert conflict_response.status_code == 409

    error = conflict_response.json()["error"]
    expected_error = _example("09_error_workspace_version_conflict.json")["error"]
    assert error["code"] == expected_error["code"]
    assert error["details"]["workspace_id"] == "ws_demo"
    assert error["details"]["current_workspace_version"] == 3
    assert error["details"]["base_workspace_version"] == 2

    workspace_response = client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    assert workspace_response.json()["workspace"]["workspace_version"] == 3


def test_sales_workspace_validation_error_and_unsupported_operation(client) -> None:
    _build_demo_workspace(client)

    validation_request = {
        "patch": {
            "id": "patch_invalid_observation",
            "workspace_id": "ws_demo",
            "base_workspace_version": 3,
            "operations": [
                {
                    "type": "upsert_candidate_observation",
                    "payload": {
                        "id": "obs_invalid",
                        "candidate_id": "cand_d",
                        "source_id": "src_missing",
                        "round_id": "rr_002",
                        "signal_type": "fit",
                        "summary": "This observation references a missing source.",
                    },
                }
            ],
        }
    }
    validation_response = client.post("/sales-workspaces/ws_demo/patches", json=validation_request)
    assert validation_response.status_code == 422
    assert validation_response.json()["error"]["code"] == _example("10_error_validation_error.json")["error"]["code"]

    unsupported_request = copy.deepcopy(validation_request)
    unsupported_request["patch"]["id"] = "patch_unsupported"
    unsupported_request["patch"]["operations"] = [
        {"type": "replace_ranking_board", "payload": {"id": "board_manual"}}
    ]
    unsupported_response = client.post("/sales-workspaces/ws_demo/patches", json=unsupported_request)
    assert unsupported_response.status_code == 400
    assert unsupported_response.json()["error"]["code"] == "unsupported_workspace_operation"


def test_sales_workspace_not_found_and_path_mismatch(client) -> None:
    missing_response = client.get("/sales-workspaces/ws_missing")
    assert missing_response.status_code == 404
    assert missing_response.json()["error"]["code"] == "not_found"

    client.post("/sales-workspaces", json=_example("01_create_workspace_request.json"))
    mismatch_request = _example("03_patch_product_direction_request.json")
    mismatch_response = client.post("/sales-workspaces/ws_other/patches", json=mismatch_request)
    assert mismatch_response.status_code == 422
    assert mismatch_response.json()["error"]["code"] == "validation_error"


def test_sales_workspace_default_store_is_app_local(backend_env, monkeypatch) -> None:
    monkeypatch.delenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR", raising=False)
    reset_settings_cache()

    with TestClient(create_app()) as first_client:
        _build_demo_workspace(first_client)
        assert first_client.get("/sales-workspaces/ws_demo").status_code == 200

    with TestClient(create_app()) as second_client:
        missing_response = second_client.get("/sales-workspaces/ws_demo")
        assert missing_response.status_code == 404
        assert missing_response.json()["error"]["code"] == "not_found"


def test_sales_workspace_json_store_survives_app_restart(backend_env, monkeypatch, tmp_path) -> None:
    store_dir = tmp_path / "sales_workspace_store"
    monkeypatch.setenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR", str(store_dir))
    reset_settings_cache()

    with TestClient(create_app()) as first_client:
        _build_demo_workspace(first_client)

    workspace_file = store_dir / "ws_demo.json"
    assert workspace_file.exists()
    before_conflict = workspace_file.read_text(encoding="utf-8")
    assert json.loads(before_conflict)["workspace_version"] == 3

    with TestClient(create_app()) as second_client:
        workspace_response = second_client.get("/sales-workspaces/ws_demo")
        assert workspace_response.status_code == 200
        assert workspace_response.json()["workspace"]["workspace_version"] == 3

        ranking_response = second_client.get("/sales-workspaces/ws_demo/ranking-board/current")
        assert ranking_response.status_code == 200
        assert ranking_response.json()["ranking_board"]["ranked_items"][0]["candidate_id"] == "cand_d"

        projection_response = second_client.get("/sales-workspaces/ws_demo/projection")
        assert projection_response.status_code == 200
        assert "rankings/current.md" in projection_response.json()["files"]

        context_pack_response = second_client.post(
            "/sales-workspaces/ws_demo/context-packs",
            json={"task_type": "research_round", "token_budget_chars": 6000, "top_n_candidates": 5},
        )
        assert context_pack_response.status_code == 200
        assert context_pack_response.json()["context_pack"]["top_candidates"][0]["candidate_id"] == "cand_d"

        conflict_response = second_client.post(
            "/sales-workspaces/ws_demo/patches",
            json=_example("05_patch_round_2_request.json"),
        )
        assert conflict_response.status_code == 409
        assert conflict_response.json()["error"]["code"] == "workspace_version_conflict"

    assert workspace_file.read_text(encoding="utf-8") == before_conflict
