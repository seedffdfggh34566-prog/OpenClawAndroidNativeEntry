from __future__ import annotations

import copy
import json
import os
from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.api.config import reset_settings_cache
from backend.api.database import reset_database_state
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
def postgres_sales_workspace_client(monkeypatch) -> Generator[TestClient, None, None]:
    database_url = os.environ.get(POSTGRES_VERIFY_ENV)
    if not database_url:
        pytest.skip(f"set {POSTGRES_VERIFY_ENV} to run Postgres Sales Workspace API verification")

    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", database_url)
    monkeypatch.setenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND", "postgres")
    monkeypatch.delenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR", raising=False)
    reset_settings_cache()
    reset_database_state()
    with TestClient(create_app()) as client:
        yield client
    reset_database_state()
    reset_settings_cache()


def test_sales_workspace_api_uses_postgres_store_for_contract_flow(postgres_sales_workspace_client) -> None:
    workspace_id = _workspace_id()
    _build_demo_workspace(postgres_sales_workspace_client, workspace_id)

    ranking_response = postgres_sales_workspace_client.get(
        f"/sales-workspaces/{workspace_id}/ranking-board/current"
    )
    assert ranking_response.status_code == 200
    assert ranking_response.json()["ranking_board"]["ranked_items"][0]["candidate_id"] == "cand_d"

    projection_response = postgres_sales_workspace_client.get(f"/sales-workspaces/{workspace_id}/projection")
    assert projection_response.status_code == 200
    assert "rankings/current.md" in projection_response.json()["files"]

    context_pack_response = postgres_sales_workspace_client.post(
        f"/sales-workspaces/{workspace_id}/context-packs",
        json={"task_type": "research_round", "token_budget_chars": 6000, "top_n_candidates": 5},
    )
    assert context_pack_response.status_code == 200
    assert context_pack_response.json()["context_pack"]["top_candidates"][0]["candidate_id"] == "cand_d"


def test_sales_workspace_api_postgres_conflict_does_not_mutate(postgres_sales_workspace_client) -> None:
    workspace_id = _workspace_id()
    _build_demo_workspace(postgres_sales_workspace_client, workspace_id)

    conflict_response = postgres_sales_workspace_client.post(
        f"/sales-workspaces/{workspace_id}/patches",
        json=_patch_example("05_patch_round_2_request.json", workspace_id),
    )
    assert conflict_response.status_code == 409
    assert conflict_response.json()["error"]["code"] == "workspace_version_conflict"

    workspace_response = postgres_sales_workspace_client.get(f"/sales-workspaces/{workspace_id}")
    assert workspace_response.status_code == 200
    assert workspace_response.json()["workspace"]["workspace_version"] == 3


def test_sales_workspace_api_postgres_missing_workspace(postgres_sales_workspace_client) -> None:
    response = postgres_sales_workspace_client.get(f"/sales-workspaces/{_workspace_id()}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def _build_demo_workspace(client: TestClient, workspace_id: str) -> None:
    create_response = client.post(
        "/sales-workspaces",
        json={
            **_example("01_create_workspace_request.json"),
            "workspace_id": workspace_id,
        },
    )
    assert create_response.status_code == 201

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


def _workspace_id() -> str:
    return f"ws_api_pg_{uuid4().hex[:12]}"


def _patch_example(filename: str, workspace_id: str) -> dict:
    payload = copy.deepcopy(_example(filename))
    payload["patch"]["workspace_id"] = workspace_id
    payload["patch"]["id"] = f'{payload["patch"]["id"]}_{workspace_id}'
    return payload


def _example(filename: str) -> dict:
    return json.loads((EXAMPLE_DIR / filename).read_text(encoding="utf-8"))
