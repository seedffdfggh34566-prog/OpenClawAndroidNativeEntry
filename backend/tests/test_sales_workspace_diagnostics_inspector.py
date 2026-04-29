from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.config import reset_settings_cache
from backend.api.database import reset_database_state


EXAMPLE_DIR = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "reference"
    / "api"
    / "examples"
    / "sales_workspace_kernel_v0"
)

SECRET_SENTINEL = "sk-openclaw-diagnostics-secret-should-not-leak"


@pytest.fixture
def diagnostics_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    def _build(*, enabled: bool) -> TestClient:
        monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
        monkeypatch.delenv("OPENCLAW_BACKEND_DATABASE_PATH", raising=False)
        monkeypatch.delenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND", raising=False)
        monkeypatch.delenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR", raising=False)
        monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", SECRET_SENTINEL)
        monkeypatch.setenv("OPENCLAW_BACKEND_LANGFUSE_SECRET_KEY", SECRET_SENTINEL)
        monkeypatch.setenv("OPENCLAW_BACKEND_DIAGNOSTICS_TEST_SECRET", SECRET_SENTINEL)
        if enabled:
            monkeypatch.setenv("OPENCLAW_BACKEND_DEV_SALES_WORKSPACE_DIAGNOSTICS_ENABLED", "true")
        else:
            monkeypatch.delenv("OPENCLAW_BACKEND_DEV_SALES_WORKSPACE_DIAGNOSTICS_ENABLED", raising=False)
        reset_settings_cache()
        reset_database_state()
        from backend.api.main import create_app

        return TestClient(create_app())

    yield _build

    reset_database_state()
    reset_settings_cache()


def test_sales_workspace_diagnostics_routes_are_disabled_by_default(diagnostics_client) -> None:
    with diagnostics_client(enabled=False) as client:
        assert client.get("/dev/sales-workspace-inspector").status_code == 404
        assert client.get("/dev/sales-workspaces").status_code == 404
        assert client.get("/dev/sales-workspaces/ws_demo/diagnostics").status_code == 404


def test_sales_workspace_diagnostics_inspector_reads_workspace_without_mutation(diagnostics_client) -> None:
    with diagnostics_client(enabled=True) as client:
        _build_diagnostics_demo_state(client)
        workspace_before = _get_workspace(client, "ws_demo")

        html_response = client.get("/dev/sales-workspace-inspector")
        assert html_response.status_code == 200
        assert "text/html" in html_response.headers["content-type"]
        assert "Sales Workspace" in html_response.text
        assert "diagnostics" in html_response.text.lower()

        list_response = client.get("/dev/sales-workspaces")
        assert list_response.status_code == 200
        list_payload = list_response.json()
        assert _contains_text(list_payload, "ws_demo")
        assert _contains_text(list_payload, "FactoryOps")

        diagnostics_response = client.get("/dev/sales-workspaces/ws_demo/diagnostics")
        assert diagnostics_response.status_code == 200
        diagnostics_payload = diagnostics_response.json()
        assert _contains_text(diagnostics_payload, "ws_demo")
        assert _contains_text(diagnostics_payload, "msg_user_product_001")
        assert _contains_text(diagnostics_payload, "run_sales_turn_product_001")
        assert _contains_text(diagnostics_payload, "draft_review_sales_turn_product_profile_update_v1")

        workspace_after = _get_workspace(client, "ws_demo")
        assert workspace_after == workspace_before

        combined_text = "\n".join(
            [
                html_response.text,
                json.dumps(list_payload, ensure_ascii=False, sort_keys=True),
                json.dumps(diagnostics_payload, ensure_ascii=False, sort_keys=True),
            ]
        )
        assert SECRET_SENTINEL not in combined_text
        assert "OPENCLAW_BACKEND_LLM_API_KEY" not in combined_text
        assert "OPENCLAW_BACKEND_LANGFUSE_SECRET_KEY" not in combined_text
        assert "Authorization" not in combined_text


def test_sales_workspace_diagnostics_missing_workspace_returns_404(diagnostics_client) -> None:
    with diagnostics_client(enabled=True) as client:
        _create_workspace(client, "ws_demo")

        response = client.get("/dev/sales-workspaces/ws_missing/diagnostics")

        assert response.status_code == 404


def _build_diagnostics_demo_state(client: TestClient) -> None:
    _create_workspace(client, "ws_demo")
    thread_response = client.post(
        "/sales-workspaces/ws_demo/threads",
        json={"id": "thread_factory", "title": "FactoryOps first pass"},
    )
    assert thread_response.status_code == 201

    message_response = client.post(
        "/sales-workspaces/ws_demo/threads/thread_factory/messages",
        json={
            "id": "msg_user_product_001",
            "message_type": "product_profile_update",
            "content": "FactoryOps AI 帮助制造企业协同排产、库存和 ERP。",
        },
    )
    assert message_response.status_code == 201

    turn_response = client.post(
        "/sales-workspaces/ws_demo/threads/thread_factory/agent-runs/sales-agent-turns",
        json={
            "message_id": "msg_user_product_001",
            "base_workspace_version": 0,
            "instruction": "update product profile from chat",
        },
    )
    assert turn_response.status_code == 200
    turn_payload = turn_response.json()
    assert turn_payload["agent_run"]["id"] == "run_sales_turn_product_001"
    assert turn_payload["draft_review"]["id"] == "draft_review_sales_turn_product_profile_update_v1"
    assert turn_payload["draft_review"]["preview"]["would_mutate"] is False

    review_response = client.post(
        "/sales-workspaces/ws_demo/draft-reviews/draft_review_sales_turn_product_profile_update_v1/review",
        json={
            "decision": "accept",
            "reviewed_by": "diagnostics_test_user",
            "comment": "Readable in diagnostics.",
            "client": "pytest",
        },
    )
    assert review_response.status_code == 200
    assert review_response.json()["draft_review"]["status"] == "reviewed"


def _create_workspace(client: TestClient, workspace_id: str) -> None:
    response = client.post(
        "/sales-workspaces",
        json={
            **_example("01_create_workspace_request.json"),
            "workspace_id": workspace_id,
        },
    )
    assert response.status_code == 201


def _get_workspace(client: TestClient, workspace_id: str) -> dict:
    response = client.get(f"/sales-workspaces/{workspace_id}")
    assert response.status_code == 200
    return copy.deepcopy(response.json()["workspace"])


def _example(filename: str) -> dict:
    return json.loads((EXAMPLE_DIR / filename).read_text(encoding="utf-8"))


def _contains_text(payload: object, expected: str) -> bool:
    return expected in json.dumps(payload, ensure_ascii=False, sort_keys=True)
