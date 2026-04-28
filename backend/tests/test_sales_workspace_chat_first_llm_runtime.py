from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.config import reset_settings_cache
from backend.api.database import reset_database_state
from backend.api.main import create_app
from backend.runtime.llm_client import TokenHubCompletion
from backend.runtime.sales_workspace_chat_turn_llm import parse_sales_agent_turn_llm_json


EXAMPLE_DIR = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "reference"
    / "api"
    / "examples"
    / "sales_workspace_kernel_v0"
)


@pytest.fixture
def llm_client(monkeypatch, tmp_path) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE", "llm")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    monkeypatch.delenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND", raising=False)
    monkeypatch.delenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR", raising=False)
    reset_settings_cache()
    reset_database_state()
    with TestClient(create_app()) as test_client:
        yield test_client
    reset_database_state()
    reset_settings_cache()


def test_parse_sales_agent_turn_llm_json_strips_thinking_and_fences() -> None:
    parsed = parse_sales_agent_turn_llm_json(
        """
        <think>不要记录内部推理。</think>
        ```json
        {
          "message_type": "clarifying_question",
          "assistant_message": "我需要先确认几个问题。",
          "clarifying_questions": ["客户是谁？", "行业是什么？", "地区在哪？"],
          "patch_operations": [],
          "confidence": 0.6,
          "missing_fields": ["target_customer"],
          "reasoning_summary": "输入不足。"
        }
        ```
        """
    )
    assert parsed["message_type"] == "clarifying_question"
    assert len(parsed["clarifying_questions"]) == 3


def test_llm_runtime_product_turn_creates_draft_review_without_mutation(llm_client, monkeypatch) -> None:
    _mock_llm(monkeypatch, _product_draft_output())
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_product_001",
        message_type="product_profile_update",
        content="我们做工业设备维保软件，帮工厂减少停机时间。",
    )

    response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_product_001", "base_workspace_version": 0},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["agent_run"]["runtime_metadata"]["mode"] == "real_llm_no_langgraph"
    assert payload["agent_run"]["runtime_metadata"]["provider"] == "tencent_tokenhub"
    assert payload["patch_draft"]["author"] == "sales_agent_turn_llm_runtime"
    assert payload["patch_draft"]["operations"][0]["type"] == "upsert_product_profile_revision"
    assert payload["patch_draft"]["operations"][0]["payload"]["id"] == "ppr_llm_v1"
    assert payload["draft_review"]["status"] == "previewed"
    assert payload["assistant_message"]["message_type"] == "draft_summary"

    workspace_response = llm_client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    workspace = workspace_response.json()["workspace"]
    assert workspace["workspace_version"] == 0
    assert workspace["product_profile_revisions"] == {}


def test_llm_runtime_clarifying_question_does_not_create_draft(llm_client, monkeypatch) -> None:
    _mock_llm(monkeypatch, _clarifying_output())
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_unclear_001",
        message_type="product_profile_update",
        content="帮我找客户",
    )

    response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_unclear_001", "base_workspace_version": 0},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["assistant_message"]["message_type"] == "clarifying_question"
    assert payload["patch_draft"] is None
    assert payload["draft_review"] is None
    assert "1. 你的产品主要解决什么问题？" in payload["assistant_message"]["content"]


def test_llm_runtime_invalid_output_fails_run_without_mutation(llm_client, monkeypatch) -> None:
    _mock_llm(monkeypatch, {"message_type": "draft_summary", "assistant_message": "bad"})
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_product_001",
        message_type="product_profile_update",
        content="我们做工业设备维保软件，帮工厂减少停机时间。",
    )

    response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_product_001", "base_workspace_version": 0},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "llm_structured_output_invalid"
    run_response = llm_client.get("/sales-workspaces/ws_demo/agent-runs/run_sales_turn_product_001")
    assert run_response.status_code == 200
    assert run_response.json()["agent_run"]["status"] == "failed"

    workspace_response = llm_client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    assert workspace_response.json()["workspace"]["workspace_version"] == 0


def test_llm_runtime_version_conflict_does_not_mutate(llm_client, monkeypatch) -> None:
    _mock_llm(monkeypatch, _product_draft_output())
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_product_001",
        message_type="product_profile_update",
        content="我们做工业设备维保软件，帮工厂减少停机时间。",
    )

    response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_product_001", "base_workspace_version": 1},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "workspace_version_conflict"
    workspace_response = llm_client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    assert workspace_response.json()["workspace"]["workspace_version"] == 0


def _mock_llm(monkeypatch, output: dict) -> None:
    def complete(self, messages):  # noqa: ANN001, ARG001
        return TokenHubCompletion(
            content=json.dumps(output, ensure_ascii=False),
            usage={"prompt_tokens": 100, "completion_tokens": 80, "total_tokens": 180},
        )

    monkeypatch.setattr("backend.runtime.llm_client.TokenHubClient.complete", complete)


def _product_draft_output() -> dict:
    return {
        "message_type": "draft_summary",
        "assistant_message": "我已整理出一版产品理解草稿，请审阅后应用。",
        "clarifying_questions": [],
        "patch_operations": [
            {
                "type": "upsert_product_profile_revision",
                "payload": {
                    "product_name": "工业设备维保软件",
                    "one_liner": "帮助工厂降低停机时间的设备维保软件。",
                    "target_customers": ["制造业工厂设备部"],
                    "target_industries": ["制造业"],
                    "pain_points": ["停机损失"],
                    "value_props": ["降低停机时间"],
                    "constraints": ["需要确认设备类型和地区"],
                },
            }
        ],
        "confidence": 0.82,
        "missing_fields": [],
        "reasoning_summary": "用户提供了产品和痛点。",
    }


def _clarifying_output() -> dict:
    return {
        "message_type": "clarifying_question",
        "assistant_message": "我需要先确认几个关键信息。",
        "clarifying_questions": [
            "你的产品主要解决什么问题？",
            "最适合的目标客户是谁？",
            "客户现在最痛的场景是什么？",
            "你希望优先覆盖哪个地区？",
            "哪些行业暂时不想做？",
        ],
        "patch_operations": [],
        "confidence": 0.4,
        "missing_fields": ["product", "target_customer"],
        "reasoning_summary": "用户输入不足。",
    }


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
        json={
            "id": message_id,
            "message_type": message_type,
            "content": content,
        },
    )
    assert response.status_code == 201
    return response.json()["message"]


def _example(filename: str) -> dict:
    return json.loads((EXAMPLE_DIR / filename).read_text(encoding="utf-8"))
