from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.config import reset_settings_cache
from backend.api.database import reset_database_state
from backend.api.main import create_app
from backend.runtime.llm_client import TokenHubClientError, TokenHubCompletion
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


def test_llm_runtime_product_turn_auto_applies_product_profile(llm_client, monkeypatch) -> None:
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
    assert payload["agent_run"]["runtime_metadata"]["mode"] == "real_llm_memory_decision_no_langgraph"
    assert payload["agent_run"]["runtime_metadata"]["provider"] == "tencent_tokenhub"
    assert payload["patch_draft"]["author"] == "sales_agent_turn_memory_pipeline"
    assert payload["patch_draft"]["operations"][0]["type"] == "upsert_product_profile_revision"
    assert payload["patch_draft"]["operations"][0]["payload"]["id"] == "ppr_memory_v1"
    assert payload["draft_review"]["status"] == "applied"
    assert payload["draft_review"]["apply_result"]["workspace_version"] == 1
    assert payload["assistant_message"]["message_type"] == "draft_summary"
    assert "沉淀到工作区" in payload["assistant_message"]["content"]
    assert "还需要补充" not in payload["assistant_message"]["content"]

    workspace_response = llm_client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    workspace = workspace_response.json()["workspace"]
    assert workspace["workspace_version"] == 1
    assert workspace["current_product_profile_revision_id"] == "ppr_memory_v1"
    assert workspace["product_profile_revisions"]["ppr_memory_v1"]["product_name"] == "工业设备维保软件"


def test_llm_runtime_draft_summary_appends_missing_fields(llm_client, monkeypatch) -> None:
    _mock_llm(monkeypatch, _dangling_missing_fields_draft_output())
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_product_001",
        message_type="product_profile_update",
        content="产品是 sales agent，帮助中小企业主自动找客户。",
    )

    response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_product_001", "base_workspace_version": 0},
    )

    assert response.status_code == 200
    payload = response.json()
    content = payload["assistant_message"]["content"]
    assert payload["assistant_message"]["message_type"] == "draft_summary"
    assert "还需要补充" in content
    assert "1. 目标行业" in content
    assert "2. 目标公司规模" in content
    assert "3. 目标地区" in content
    assert "沉淀到工作区" in content
    assert not content.rstrip().endswith("以下内容以完善资料。")


def test_llm_runtime_sanitizes_internal_terms_from_assistant_content(llm_client, monkeypatch) -> None:
    _mock_llm(monkeypatch, _internal_workspace_question_output())
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_boundary_001",
        message_type="workspace_question",
        content="为什么不能直接给我联系人？",
    )

    response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_boundary_001", "base_workspace_version": 0},
    )

    assert response.status_code == 200
    content = response.json()["assistant_message"]["content"]
    assert "patch_operations" not in content
    assert "revision_id" not in content
    assert "current_product_profile_revision_id" not in content
    assert "workspace_goal" not in content
    assert "blocked_capabilities" not in content
    assert "V2.2 runtime" not in content
    assert "当前版本不能直接生成真实公司名单" in content
    assert "筛选标准" in content


def test_llm_runtime_product_clarifying_output_still_creates_minimum_product_draft(llm_client, monkeypatch) -> None:
    _mock_llm(monkeypatch, _product_clarifying_without_patch_output())
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_product_002",
        message_type="product_profile_update",
        content="我们做本地企业销售和管理培训，主要是线下课。",
    )

    response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_product_002", "base_workspace_version": 0},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["assistant_message"]["message_type"] == "draft_summary"
    assert payload["patch_draft"]["operations"][0]["type"] == "upsert_product_profile_revision"
    assert payload["patch_draft"]["operations"][0]["payload"]["one_liner"].startswith("我们做本地企业销售")
    assert payload["draft_review"]["status"] == "applied"
    assert "沉淀到工作区" in payload["assistant_message"]["content"]


def test_llm_runtime_mixed_turn_creates_product_and_direction_review(llm_client, monkeypatch) -> None:
    _mock_llm(monkeypatch, _mixed_draft_output())
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_mixed_001",
        message_type="mixed_product_and_direction_update",
        content="我们做中小企业财税 SaaS，先找华东中小企业老板和财务负责人。",
    )

    response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_mixed_001", "base_workspace_version": 0},
    )

    assert response.status_code == 200
    payload = response.json()
    operation_types = [operation["type"] for operation in payload["patch_draft"]["operations"]]
    assert operation_types == [
        "upsert_product_profile_revision",
        "upsert_lead_direction_version",
        "set_active_lead_direction",
    ]
    assert payload["draft_review"]["status"] == "applied"
    assert payload["assistant_message"]["message_type"] == "draft_summary"

    workspace_response = llm_client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    workspace = workspace_response.json()["workspace"]
    assert workspace["workspace_version"] == 1
    assert workspace["current_product_profile_revision_id"] == "ppr_memory_v1"
    assert workspace["current_lead_direction_version_id"] == "dir_memory_v1"


def test_llm_runtime_lead_direction_gives_customer_finding_advice_and_draft(llm_client, monkeypatch) -> None:
    _mock_llm(monkeypatch, _lead_direction_advice_output())
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_lead_001",
        message_type="lead_direction_update",
        content="我的客户是什么？我现在应该怎么找第一批客户？",
    )

    response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_lead_001", "base_workspace_version": 0},
    )

    assert response.status_code == 200
    payload = response.json()
    content = payload["assistant_message"]["content"]
    assert payload["assistant_message"]["message_type"] == "draft_summary"
    assert "1-20 人小企业老板" in content
    assert "筛选信号" in content
    assert "关键词" in content
    assert "写入前不会改变正式工作区" in content
    operation_types = [operation["type"] for operation in payload["patch_draft"]["operations"]]
    assert operation_types == ["upsert_lead_direction_version", "set_active_lead_direction"]
    assert payload["draft_review"]["status"] == "previewed"
    workspace = llm_client.get("/sales-workspaces/ws_demo").json()["workspace"]
    assert workspace["workspace_version"] == 0
    assert workspace["current_lead_direction_version_id"] is None


def test_llm_runtime_draft_summary_rewrites_pending_draft_language(llm_client, monkeypatch) -> None:
    _mock_llm(monkeypatch, _lead_direction_pending_draft_language_output())
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_lead_002",
        message_type="lead_direction_update",
        content="给我第一周怎么做",
    )

    response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_lead_002", "base_workspace_version": 0},
    )

    assert response.status_code == 200
    payload = response.json()
    content = payload["assistant_message"]["content"]
    assert payload["draft_review"]["status"] == "previewed"
    assert "如果你确认" not in content
    assert "可以输出正式的 lead_direction_version" not in content
    assert "我已经把这版判断整理成下方可保存到工作区的更新" in content
    assert "写入前不会改变正式工作区" in content
    workspace = llm_client.get("/sales-workspaces/ws_demo").json()["workspace"]
    assert workspace["workspace_version"] == 0
    assert workspace["current_lead_direction_version_id"] is None


def test_llm_runtime_lead_direction_clarifying_output_still_creates_draft(llm_client, monkeypatch) -> None:
    _mock_llm(monkeypatch, _lead_direction_clarifying_without_patch_output())
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_lead_001",
        message_type="lead_direction_update",
        content="我没有行业方向，你直接建议",
    )

    response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_lead_001", "base_workspace_version": 0},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["assistant_message"]["message_type"] == "draft_summary"
    assert payload["patch_draft"] is None
    assert payload["draft_review"] is None


def test_llm_runtime_lead_direction_does_not_degrade_current_product_profile(llm_client, monkeypatch) -> None:
    _mock_llm_sequence(
        monkeypatch,
        [
            _product_draft_output(),
            _lead_direction_with_low_quality_product_output(),
        ],
    )
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_product_001",
        message_type="product_profile_update",
        content="产品是拓客 AI，帮助 1-20 人小企业老板自动找客户。",
    )
    first_response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_product_001", "base_workspace_version": 0},
    )
    assert first_response.status_code == 200

    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_lead_003",
        message_type="lead_direction_update",
        content="我该怎么找客户？",
    )
    second_response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_lead_003", "base_workspace_version": 1},
    )

    assert second_response.status_code == 200
    workspace = llm_client.get("/sales-workspaces/ws_demo").json()["workspace"]
    current_product = workspace["product_profile_revisions"][workspace["current_product_profile_revision_id"]]
    assert workspace["workspace_version"] == 1
    assert current_product["product_name"] == "工业设备维保软件"
    assert current_product["one_liner"] == "帮助工厂降低停机时间的设备维保软件。"
    assert "待确认目标客户" not in current_product["target_customers"]
    assert workspace["current_lead_direction_version_id"] is None


def test_llm_runtime_product_update_merges_new_info_without_clearing_existing(llm_client, monkeypatch) -> None:
    _mock_llm_sequence(
        monkeypatch,
        [
            _product_draft_output(),
            _product_incremental_output(),
        ],
    )
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_product_001",
        message_type="product_profile_update",
        content="我们做工业设备维保软件，帮工厂减少停机时间。",
    )
    assert llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_product_001", "base_workspace_version": 0},
    ).status_code == 200

    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_product_002",
        message_type="product_profile_update",
        content="补充：客单价 3000-8000，目标是小企业老板。",
    )
    response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_product_002", "base_workspace_version": 1},
    )

    assert response.status_code == 200
    workspace = llm_client.get("/sales-workspaces/ws_demo").json()["workspace"]
    current_product = workspace["product_profile_revisions"][workspace["current_product_profile_revision_id"]]
    assert workspace["workspace_version"] == 2
    assert current_product["one_liner"] == "帮助工厂降低停机时间的设备维保软件。"
    assert "制造业工厂设备部" in current_product["target_customers"]
    assert "小企业老板" in current_product["target_customers"]
    assert "客单价 3000-8000" in current_product["constraints"]
    assert "待确认行业" not in current_product["target_industries"]


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


def test_llm_runtime_workspace_question_explains_without_mutation(llm_client, monkeypatch) -> None:
    _mock_llm(monkeypatch, _workspace_question_output())
    _create_workspace(llm_client, "ws_demo")
    _post_message(
        llm_client,
        workspace_id="ws_demo",
        message_id="msg_user_explain_001",
        message_type="workspace_question",
        content="为什么建议这个方向？",
    )

    response = llm_client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_explain_001", "base_workspace_version": 0},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["assistant_message"]["message_type"] == "workspace_question"
    assert "当前 workspace 信息仍不足" in payload["assistant_message"]["content"]
    assert payload["patch_draft"] is None
    assert payload["draft_review"] is None
    workspace_response = llm_client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    assert workspace_response.json()["workspace"]["workspace_version"] == 0


def test_llm_runtime_invalid_output_fails_run_without_mutation(llm_client, monkeypatch) -> None:
    _mock_llm(
        monkeypatch,
        {
            "message_type": "clarifying_question",
            "assistant_message": "bad",
            "clarifying_questions": ["问题太少"],
            "patch_operations": [],
        },
    )
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


def test_llm_runtime_invalid_json_fails_run_without_mutation(llm_client, monkeypatch) -> None:
    _mock_llm_content(monkeypatch, "not json")
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


def test_llm_runtime_unsupported_operation_is_blocked_by_kernel_gate(llm_client, monkeypatch) -> None:
    _mock_llm(monkeypatch, _unsupported_operation_output())
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
    assert response.json()["patch_draft"] is None
    run_response = llm_client.get("/sales-workspaces/ws_demo/agent-runs/run_sales_turn_product_001")
    assert run_response.status_code == 200
    run = run_response.json()["agent_run"]
    assert run["status"] == "succeeded"
    assert run["runtime_metadata"]["memory_gate"]["decision"] == "reject"
    workspace_response = llm_client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    assert workspace_response.json()["workspace"]["workspace_version"] == 0


def test_llm_runtime_client_failure_records_failed_run_without_mutation(llm_client, monkeypatch) -> None:
    def fail_complete(self, messages):  # noqa: ANN001, ARG001
        raise TokenHubClientError("tokenhub_request_timeout")

    monkeypatch.setattr("backend.runtime.llm_client.TokenHubClient.complete", fail_complete)
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

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "llm_runtime_unavailable"
    run_response = llm_client.get("/sales-workspaces/ws_demo/agent-runs/run_sales_turn_product_001")
    assert run_response.status_code == 200
    assert run_response.json()["agent_run"]["status"] == "failed"
    workspace_response = llm_client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    assert workspace_response.json()["workspace"]["workspace_version"] == 0


def test_llm_runtime_retries_transient_timeout_once(llm_client, monkeypatch) -> None:
    attempts = {"count": 0}
    output = json.dumps(_product_draft_output(), ensure_ascii=False)

    def complete(self, messages):  # noqa: ANN001, ARG001
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise TokenHubClientError("tokenhub_request_timeout")
        if _is_memory_evaluator_call(messages):
            decision = _memory_decision_for_output(
                _product_draft_output(),
                _user_message_from_memory_messages(messages),
            )
            return TokenHubCompletion(
                content=json.dumps(decision, ensure_ascii=False),
                usage={"prompt_tokens": 60, "completion_tokens": 40, "total_tokens": 100},
            )
        return TokenHubCompletion(
            content=output,
            usage={"prompt_tokens": 100, "completion_tokens": 80, "total_tokens": 180},
        )

    monkeypatch.setattr("backend.runtime.llm_client.TokenHubClient.complete", complete)
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
    assert attempts["count"] == 3
    payload = response.json()
    assert payload["agent_run"]["runtime_metadata"]["llm_request_attempts"] == 2
    assert payload["draft_review"]["status"] == "applied"


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
    _mock_llm_content(monkeypatch, json.dumps(output, ensure_ascii=False))


def _mock_llm_sequence(monkeypatch, outputs: list[dict]) -> None:
    serialized = [json.dumps(output, ensure_ascii=False) for output in outputs]
    attempts = {"index": 0}
    pending_output: dict[str, object] = {}

    def complete(self, messages):  # noqa: ANN001, ARG001
        if _is_memory_evaluator_call(messages):
            output = pending_output.get("output")
            decision = _memory_decision_for_output(
                output if isinstance(output, dict) else {},
                _user_message_from_memory_messages(messages),
            )
            return TokenHubCompletion(
                content=json.dumps(decision, ensure_ascii=False),
                usage={"prompt_tokens": 60, "completion_tokens": 40, "total_tokens": 100},
            )
        index = min(attempts["index"], len(serialized) - 1)
        attempts["index"] += 1
        pending_output["output"] = outputs[index]
        return TokenHubCompletion(
            content=serialized[index],
            usage={"prompt_tokens": 100, "completion_tokens": 80, "total_tokens": 180},
        )

    monkeypatch.setattr("backend.runtime.llm_client.TokenHubClient.complete", complete)


def _mock_llm_content(monkeypatch, content: str) -> None:
    output: dict[str, object] = {}
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            output = parsed
    except ValueError:
        output = {}

    def complete(self, messages):  # noqa: ANN001, ARG001
        if _is_memory_evaluator_call(messages):
            decision = _memory_decision_for_output(
                output,
                _user_message_from_memory_messages(messages),
            )
            return TokenHubCompletion(
                content=json.dumps(decision, ensure_ascii=False),
                usage={"prompt_tokens": 60, "completion_tokens": 40, "total_tokens": 100},
            )
        return TokenHubCompletion(
            content=content,
            usage={"prompt_tokens": 100, "completion_tokens": 80, "total_tokens": 180},
        )

    monkeypatch.setattr("backend.runtime.llm_client.TokenHubClient.complete", complete)


def _is_memory_evaluator_call(messages: list[dict[str, str]]) -> bool:
    if not messages:
        return False
    content = messages[0].get("content", "")
    return content.startswith("你是 OpenClaw V2.1 的 MemoryEvaluator。")


def _user_message_from_memory_messages(messages: list[dict[str, str]]) -> dict:
    runtime_input = _runtime_input_from_memory_messages(messages)
    user_message = runtime_input.get("user_message")
    if isinstance(user_message, dict):
        return user_message
    return {}


def _runtime_input_from_memory_messages(messages: list[dict[str, str]]) -> dict:
    content = messages[1]["content"]
    _, raw = content.split("runtime_input:\n", 1)
    parsed = json.loads(raw)
    return parsed if isinstance(parsed, dict) else {}


def _memory_decision_for_output(output: dict, user_message: dict) -> dict:
    user_content = user_message.get("content") if isinstance(user_message.get("content"), str) else ""
    user_message_type = user_message.get("message_type") if isinstance(user_message.get("message_type"), str) else ""
    user_message_id = user_message.get("id") if isinstance(user_message.get("id"), str) else ""
    operations = output.get("patch_operations")
    if not isinstance(operations, list) or not operations:
        if user_message_type == "product_profile_update" and "我们做" in user_content:
            return {
                "decision": "auto_apply",
                "proposals": [
                    {
                        "object_type": "product_profile",
                        "intent": "enrich",
                        "field_updates": {},
                        "remove_or_supersede": [],
                        "source_evidence": [{"message_id": user_message_id, "quote": user_content}],
                        "confidence": output.get("confidence", 0.7),
                        "risk_flags": [],
                    }
                ],
                "reasoning_summary": "test memory evaluator extracted user-supported product fact",
            }
        return {"decision": "reject", "proposals": [], "reasoning_summary": "no memory proposal"}
    proposals = []
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        operation_type = operation.get("type")
        payload = operation.get("payload") if isinstance(operation.get("payload"), dict) else {}
        if operation_type == "upsert_product_profile_revision":
            proposals.append(
                {
                    "object_type": "product_profile",
                    "intent": "enrich",
                    "field_updates": _field_updates_from_payload(payload),
                    "remove_or_supersede": [],
                    "source_evidence": [{"message_id": user_message_id, "quote": user_content}],
                    "confidence": output.get("confidence", 0.7),
                    "risk_flags": [],
                }
            )
        if operation_type == "upsert_lead_direction_version":
            proposals.append(
                {
                    "object_type": "lead_direction",
                    "intent": "enrich",
                    "field_updates": _field_updates_from_payload(payload),
                    "remove_or_supersede": [],
                    "source_evidence": [{"message_id": user_message_id, "quote": user_content}],
                    "confidence": output.get("confidence", 0.7),
                    "risk_flags": ["inferred_from_assistant_advice"] if user_message_type == "lead_direction_update" else [],
                }
            )
    decision = "review_required" if user_message_type == "lead_direction_update" else "auto_apply"
    if not proposals:
        decision = "reject"
    return {"decision": decision, "proposals": proposals, "reasoning_summary": "test memory evaluator"}


def _field_updates_from_payload(payload: dict) -> dict:
    updates = {}
    for key, value in payload.items():
        if key in {"id", "workspace_id", "version"}:
            continue
        if isinstance(value, list):
            updates[key] = {"add": value}
        elif isinstance(value, str) and value:
            updates[key] = {"set": value}
    return updates


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


def _dangling_missing_fields_draft_output() -> dict:
    output = _product_draft_output()
    output["assistant_message"] = "已收到您的产品描述。基于您提供的信息，我为您生成了产品 profile 草稿。部分信息仍需完善，请补充以下内容以完善资料。"
    output["missing_fields"] = ["target_industries", "company_sizes", "regions"]
    return output


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


def _product_clarifying_without_patch_output() -> dict:
    return {
        "message_type": "clarifying_question",
        "assistant_message": "我理解你提供了本地培训服务信息，我会先整理一版产品档案，再继续确认细节。",
        "clarifying_questions": [
            "主要面向哪些行业？",
            "客户最核心的销售痛点是什么？",
            "课程的核心价值主张是什么？",
        ],
        "patch_operations": [],
        "confidence": 0.55,
        "missing_fields": ["target_industries", "pain_points", "value_props"],
        "reasoning_summary": "用户已经提供了产品和服务形态。",
    }


def _product_incremental_output() -> dict:
    return {
        "message_type": "draft_summary",
        "assistant_message": "我已把客单价和目标客户补充到产品理解中。",
        "clarifying_questions": [],
        "patch_operations": [
            {
                "type": "upsert_product_profile_revision",
                "payload": {
                    "product_name": "待确认产品或服务",
                    "one_liner": "待确认",
                    "target_customers": ["小企业老板"],
                    "target_industries": ["待确认行业"],
                    "pain_points": ["待确认痛点"],
                    "value_props": [],
                    "constraints": ["客单价 3000-8000"],
                },
            }
        ],
        "confidence": 0.7,
        "missing_fields": [],
        "reasoning_summary": "用户补充了价格和客户。",
    }


def _mixed_draft_output() -> dict:
    return {
        "message_type": "draft_summary",
        "assistant_message": "我已整理出产品和获客方向草稿，请审阅后应用。",
        "clarifying_questions": [],
        "patch_operations": [
            {
                "type": "upsert_product_profile_revision",
                "payload": {
                    "product_name": "中小企业财税 SaaS",
                    "one_liner": "帮助老板看现金流、发票和税务风险。",
                    "target_customers": ["中小企业老板", "财务负责人"],
                    "target_industries": ["财税数字化"],
                    "pain_points": ["现金流不透明", "发票和税务风险"],
                    "value_props": ["提升经营风险可见性"],
                    "constraints": ["需要确认可接入数据类型"],
                },
            },
            {
                "type": "upsert_lead_direction_version",
                "payload": {
                    "priority_industries": ["财税数字化"],
                    "target_customer_types": ["中小企业老板", "财务负责人"],
                    "regions": ["华东"],
                    "company_sizes": ["中小企业"],
                    "priority_constraints": ["有发票或流水数据"],
                    "excluded_industries": ["大型集团"],
                    "excluded_customer_types": ["无数字化意愿客户"],
                    "change_reason": "用户同时提供产品和方向。",
                },
            },
        ],
        "confidence": 0.84,
        "missing_fields": [],
        "reasoning_summary": "输入包含产品、客户和地区方向。",
    }


def _lead_direction_advice_output() -> dict:
    return {
        "message_type": "draft_summary",
        "assistant_message": (
            "我建议先找 1-20 人小企业老板，尤其是老板亲自负责销售、没有专职增长团队的小团队。"
            "优先场景可以从本地生活服务、B2B 服务商和小型制造/贸易公司开始。"
            "筛选信号：正在招销售、公开留有老板微信/手机号、近期有获客活动但转化弱。"
            "第一批可以用关键词“老板 获客 难”“小企业 销售 线索”“本地服务 拓客”做线索验证。"
            "暂不建议先找大型集团或已有成熟销售自动化团队的企业。"
        ),
        "clarifying_questions": [],
        "patch_operations": [
            {
                "type": "upsert_lead_direction_version",
                "payload": {
                    "priority_industries": ["本地生活服务", "B2B 服务商", "小型制造或贸易公司"],
                    "target_customer_types": ["1-20 人小企业老板", "老板亲自负责销售或获客的小团队"],
                    "regions": ["待确认地区"],
                    "company_sizes": ["1-20 人小微企业"],
                    "priority_constraints": ["先验证获客痛点强、没有专职增长团队、愿意尝试 AI 的客户"],
                    "excluded_industries": ["大型集团"],
                    "excluded_customer_types": ["已有成熟销售自动化团队的企业"],
                    "change_reason": "用户询问客户是谁和第一批客户怎么找。",
                },
            }
        ],
        "confidence": 0.74,
        "missing_fields": ["regions", "priority_industries"],
        "reasoning_summary": "用户需要找客户执行建议。",
    }


def _lead_direction_pending_draft_language_output() -> dict:
    output = _lead_direction_advice_output()
    output["assistant_message"] = (
        "第一周建议每天访谈 5 个 1-20 人小企业老板，重点验证获客痛点、触达渠道和付费意愿。"
        "如果你确认以上方向，我可以输出正式的 lead_direction_version 供你审阅。"
    )
    output["missing_fields"] = []
    return output


def _lead_direction_clarifying_without_patch_output() -> dict:
    return {
        "message_type": "clarifying_question",
        "assistant_message": "我会先给一版方向，再继续确认细节。",
        "clarifying_questions": [
            "你优先做哪个地区？",
            "你希望先找线上客户还是本地客户？",
            "你能接受的客单价区间是多少？",
        ],
        "patch_operations": [],
        "confidence": 0.48,
        "missing_fields": ["regions", "priority_industries", "priority_constraints"],
        "reasoning_summary": "用户要求直接建议。",
    }


def _lead_direction_with_low_quality_product_output() -> dict:
    output = _lead_direction_advice_output()
    output["patch_operations"] = [
        {
            "type": "upsert_product_profile_revision",
            "payload": {
                "product_name": "待确认产品或服务",
                "one_liner": "待确认",
                "target_customers": ["待确认目标客户"],
                "target_industries": ["待确认行业"],
                "pain_points": ["用户未说明"],
                "value_props": ["未知"],
                "constraints": ["用户这轮在问怎么找客户"],
            },
        },
        *output["patch_operations"],
    ]
    return output


def _workspace_question_output() -> dict:
    return {
        "message_type": "workspace_question",
        "assistant_message": "当前 workspace 信息仍不足，建议先补充产品、目标客户和地区。",
        "clarifying_questions": [],
        "patch_operations": [],
        "confidence": 0.65,
        "missing_fields": ["product_profile", "lead_direction"],
        "reasoning_summary": "当前 workspace 缺少结构化对象。",
    }


def _internal_workspace_question_output() -> dict:
    return {
        "message_type": "workspace_question",
        "assistant_message": (
            "根据 workspace_goal 和 V2.2 runtime 的 blocked_capabilities，当前不能生成公司名单、联系人、CRM 或自动触达。"
            "当前 current_product_profile_revision_id=null，revision_id 缺失。"
            "如果以上信息你觉得够用，我可以生成 patch_operations 正式保存方向和确认产品 profile。"
            "你可以先用筛选标准和关键词手动查找。"
        ),
        "clarifying_questions": [],
        "patch_operations": [],
        "confidence": 0.6,
        "missing_fields": [],
        "reasoning_summary": "边界解释。",
    }


def _unsupported_operation_output() -> dict:
    return {
        "message_type": "draft_summary",
        "assistant_message": "错误地尝试写入不支持对象。",
        "clarifying_questions": [],
        "patch_operations": [
            {
                "type": "create_contact_point",
                "payload": {
                    "name": "张三",
                    "phone": "13800000000",
                },
            }
        ],
        "confidence": 0.7,
        "missing_fields": [],
        "reasoning_summary": "该操作应被后端 gate 阻止。",
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
