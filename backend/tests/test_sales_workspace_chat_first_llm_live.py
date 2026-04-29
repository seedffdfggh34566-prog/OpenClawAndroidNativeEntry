from __future__ import annotations

import json
import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.config import Settings, reset_settings_cache
from backend.api.database import reset_database_state
from backend.api.main import create_app


EXAMPLE_DIR = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "reference"
    / "api"
    / "examples"
    / "sales_workspace_kernel_v0"
)

LIVE_ENV = "OPENCLAW_BACKEND_RUN_LIVE_LLM_SMOKE"


@pytest.fixture
def live_llm_client(monkeypatch, tmp_path) -> Generator[TestClient, None, None]:
    if os.environ.get(LIVE_ENV) != "1":
        pytest.skip(f"set {LIVE_ENV}=1 to run live Tencent TokenHub smoke")

    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE", "llm")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_TIMEOUT_SECONDS", "120")
    monkeypatch.delenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND", raising=False)
    monkeypatch.delenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR", raising=False)
    reset_settings_cache()
    if not Settings().llm_api_key:
        pytest.fail("OPENCLAW_BACKEND_LLM_API_KEY is required for live LLM smoke")

    reset_database_state()
    with TestClient(create_app()) as test_client:
        yield test_client
    reset_database_state()
    reset_settings_cache()


@pytest.mark.parametrize(
    ("workspace_id", "content"),
    [
        (
            "ws_live_maintenance",
            "我们做工业设备维保软件，帮工厂减少停机时间。先看华东制造业，中小企业优先，不要教育行业。",
        ),
        (
            "ws_live_training",
            "我们给本地企业做销售和管理培训，主要是线下课。先找本地 20-300 人企业，HR、老板和销售负责人优先。",
        ),
        (
            "ws_live_tax",
            "我们做中小企业财税 SaaS，帮老板看现金流、发票和税务风险。先找华东中小企业老板和财务负责人。",
        ),
        (
            "ws_live_park",
            "我们帮产业园区做招商运营，想找有扩租和选址需求的企业。先看本地园区主导产业和成长型企业。",
        ),
        (
            "ws_live_outsourcing",
            "我们给制造企业提供外包生产和装配服务，适合小批量、多品种订单。先找华南硬件制造客户。",
        ),
    ],
)
def test_live_llm_mixed_turn_creates_draft_review_for_five_samples(
    live_llm_client: TestClient,
    workspace_id: str,
    content: str,
) -> None:
    _create_workspace(live_llm_client, workspace_id)
    _post_message(
        live_llm_client,
        workspace_id=workspace_id,
        message_id="msg_user_mixed_001",
        message_type="mixed_product_and_direction_update",
        content=content,
    )

    response = live_llm_client.post(
        f"/sales-workspaces/{workspace_id}/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_mixed_001", "base_workspace_version": 0},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["agent_run"]["runtime_metadata"]["mode"] == "real_llm_no_langgraph"
    assert payload["patch_draft"] is not None
    assert payload["draft_review"]["status"] == "previewed"
    operation_types = [operation["type"] for operation in payload["patch_draft"]["operations"]]
    assert "upsert_product_profile_revision" in operation_types
    assert "upsert_lead_direction_version" in operation_types
    assert "set_active_lead_direction" in operation_types

    workspace_response = live_llm_client.get(f"/sales-workspaces/{workspace_id}")
    assert workspace_response.status_code == 200
    assert workspace_response.json()["workspace"]["workspace_version"] == 0


def test_live_llm_clarifying_and_explanation_paths(live_llm_client: TestClient) -> None:
    workspace_id = "ws_live_explain"
    _create_workspace(live_llm_client, workspace_id)
    _post_message(
        live_llm_client,
        workspace_id=workspace_id,
        message_id="msg_user_unclear_001",
        message_type="product_profile_update",
        content="帮我找客户",
    )
    unclear_response = live_llm_client.post(
        f"/sales-workspaces/{workspace_id}/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_unclear_001", "base_workspace_version": 0},
    )
    assert unclear_response.status_code == 200, unclear_response.text
    unclear = unclear_response.json()
    assert unclear["assistant_message"]["message_type"] == "clarifying_question"
    assert unclear["patch_draft"] is None
    assert unclear["draft_review"] is None

    _post_message(
        live_llm_client,
        workspace_id=workspace_id,
        message_id="msg_user_mixed_001",
        message_type="mixed_product_and_direction_update",
        content="我们做工业设备维保软件，帮工厂减少停机时间。先找华东制造业，中小企业优先。",
    )
    mixed_response = live_llm_client.post(
        f"/sales-workspaces/{workspace_id}/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_mixed_001", "base_workspace_version": 0},
    )
    assert mixed_response.status_code == 200, mixed_response.text
    draft_review_id = mixed_response.json()["draft_review"]["id"]
    _accept_and_apply(live_llm_client, workspace_id, draft_review_id, expected_version=1)

    _post_message(
        live_llm_client,
        workspace_id=workspace_id,
        message_id="msg_user_explain_001",
        message_type="workspace_question",
        content="为什么建议这个方向？",
    )
    explanation_response = live_llm_client.post(
        f"/sales-workspaces/{workspace_id}/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_explain_001", "base_workspace_version": 1},
    )
    assert explanation_response.status_code == 200, explanation_response.text
    explanation = explanation_response.json()
    assert explanation["assistant_message"]["message_type"] == "workspace_question"
    assert explanation["patch_draft"] is None
    assert explanation["draft_review"] is None


def _create_workspace(client: TestClient, workspace_id: str) -> None:
    response = client.post(
        "/sales-workspaces",
        json={**_example("01_create_workspace_request.json"), "workspace_id": workspace_id},
    )
    assert response.status_code == 201


def _post_message(
    client: TestClient,
    *,
    workspace_id: str,
    message_id: str,
    message_type: str,
    content: str,
) -> dict:
    response = client.post(
        f"/sales-workspaces/{workspace_id}/messages",
        json={"id": message_id, "message_type": message_type, "content": content},
    )
    assert response.status_code == 201
    return response.json()["message"]


def _accept_and_apply(client: TestClient, workspace_id: str, draft_review_id: str, *, expected_version: int) -> dict:
    review_response = client.post(
        f"/sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/review",
        json={"decision": "accept", "reviewed_by": "llm_smoke_user", "client": "backend_live_smoke"},
    )
    assert review_response.status_code == 200

    apply_response = client.post(
        f"/sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/apply",
        json={"requested_by": "llm_smoke_user"},
    )
    assert apply_response.status_code == 200
    payload = apply_response.json()
    assert payload["workspace"]["workspace_version"] == expected_version
    return payload


def _example(filename: str) -> dict:
    return json.loads((EXAMPLE_DIR / filename).read_text(encoding="utf-8"))
