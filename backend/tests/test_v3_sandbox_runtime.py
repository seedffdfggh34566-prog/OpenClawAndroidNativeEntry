from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.api.config import reset_settings_cache
from backend.api.database import reset_database_state
from backend.runtime.llm_client import TokenHubClientError, TokenHubCompletion
from backend.runtime.v3_sandbox import JsonFileV3SandboxStore, run_v3_sandbox_turn
from backend.runtime.v3_sandbox.schemas import MemoryItem, V3SandboxMessage, V3SandboxSession


def test_memory_item_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        MemoryItem(id="mem_bad", status="draft", content="bad status")


def test_json_store_round_trips_session(tmp_path: Path) -> None:
    store = JsonFileV3SandboxStore(tmp_path)
    session = V3SandboxSession(
        id="v3s_json",
        memory_items={
            "mem_product": MemoryItem(
                id="mem_product",
                status="observed",
                content="产品是销售助手。",
                source="user",
            )
        },
    )

    store.create_session(session)
    reloaded = JsonFileV3SandboxStore(tmp_path).get_session("v3s_json")

    assert reloaded.id == session.id
    assert reloaded.memory_items["mem_product"].content == "产品是销售助手。"


def test_langgraph_runtime_applies_actions_with_mocked_llm(backend_env, monkeypatch) -> None:
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    client = _SequenceLlmClient([_product_turn_output()])
    result = run_v3_sandbox_turn(
        settings=get_settings(),
        session=V3SandboxSession(id="v3s_runtime"),
        user_message=V3SandboxMessage(id="msg_user_1", role="user", content="我们做中小企业财税 SaaS。"),
        client=client,
    )

    assert result.session.memory_items["mem_product"].status == "observed"
    assert result.trace_event.runtime_metadata["graph_name"] == "v3_sandbox_runtime_poc"
    assert result.actions[0].type == "write_memory"


def test_langgraph_runtime_accepts_action_type_nested_payload(backend_env, monkeypatch) -> None:
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    output = _product_turn_output()
    output["actions"][0]["payload"] = {"write_memory": output["actions"][0]["payload"]}
    client = _SequenceLlmClient([output])
    result = run_v3_sandbox_turn(
        settings=get_settings(),
        session=V3SandboxSession(id="v3s_runtime_nested"),
        user_message=V3SandboxMessage(id="msg_user_1", role="user", content="我们做中小企业财税 SaaS。"),
        client=client,
    )

    assert result.session.memory_items["mem_product"].content == "产品是中小企业财税 SaaS"


def test_v3_sandbox_api_runs_memory_correction_loop(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    monkeypatch.delenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_DIR", raising=False)
    reset_settings_cache()
    reset_database_state()
    outputs = [
        _product_turn_output(),
        _hypothesis_turn_output(),
        _correction_turn_output(),
        _followup_turn_output(),
    ]
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete",
        _SequenceLlmClient(outputs).complete,
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        create_response = client.post("/v3/sandbox/sessions", json={"session_id": "v3s_demo", "title": "Demo"})
        assert create_response.status_code == 201

        first = client.post("/v3/sandbox/sessions/v3s_demo/turns", json={"content": "我们做中小企业财税 SaaS。"})
        assert first.status_code == 200
        assert first.json()["session"]["memory_items"]["mem_product"]["status"] == "observed"

        second = client.post("/v3/sandbox/sessions/v3s_demo/turns", json={"content": "我的客户是谁？"})
        assert second.status_code == 200
        second_payload = second.json()
        assert second_payload["session"]["memory_items"]["mem_target_hypothesis"]["status"] == "hypothesis"
        assert second_payload["session"]["customer_intelligence"]["candidates"][0]["id"] == "cand_sme_owner"

        third = client.post(
            "/v3/sandbox/sessions/v3s_demo/turns",
            json={"content": "纠正一下，不是财务负责人，是老板本人。"},
        )
        assert third.status_code == 200
        third_payload = third.json()
        assert third_payload["session"]["memory_items"]["mem_target_hypothesis"]["status"] == "superseded"
        assert third_payload["session"]["memory_items"]["mem_target_corrected"]["status"] == "confirmed"

        fourth = client.post("/v3/sandbox/sessions/v3s_demo/turns", json={"content": "那下一步怎么做？"})
        assert fourth.status_code == 200
        assert "老板本人" in fourth.json()["assistant_message"]["content"]
        assert "财务负责人" not in fourth.json()["assistant_message"]["content"]

        trace_response = client.get("/v3/sandbox/sessions/v3s_demo/trace")
        assert trace_response.status_code == 200
        assert len(trace_response.json()["trace"]) == 4

        session_response = client.get("/v3/sandbox/sessions/v3s_demo")
        assert session_response.status_code == 200
        session = session_response.json()["session"]
        assert session["working_state"]["correction_summary"] == ["目标联系人已从财务负责人纠正为老板本人"]

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_api_returns_unavailable_when_llm_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "")
    reset_settings_cache()
    reset_database_state()

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        assert client.post("/v3/sandbox/sessions", json={"session_id": "v3s_missing_key"}).status_code == 201
        response = client.post("/v3/sandbox/sessions/v3s_missing_key/turns", json={"content": "你好"})
        trace = client.get("/v3/sandbox/sessions/v3s_missing_key/trace").json()["trace"]

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "llm_runtime_unavailable"
    assert trace[0]["error"]["code"] == "llm_runtime_unavailable"
    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_api_returns_structured_error_for_bad_llm_json(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete",
        lambda *args, **kwargs: TokenHubCompletion(content="not json", usage={}),
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        assert client.post("/v3/sandbox/sessions", json={"session_id": "v3s_bad_json"}).status_code == 201
        response = client.post("/v3/sandbox/sessions/v3s_bad_json/turns", json={"content": "你好"})
        trace = client.get("/v3/sandbox/sessions/v3s_bad_json/trace").json()["trace"]

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "llm_structured_output_invalid"
    assert trace[0]["error"]["code"] == "llm_structured_output_invalid"
    reset_database_state()
    reset_settings_cache()


class _SequenceLlmClient:
    def __init__(self, outputs: list[dict[str, object]]) -> None:
        self.outputs = list(outputs)

    def complete(self, messages) -> TokenHubCompletion:
        if not self.outputs:
            raise TokenHubClientError("no_more_mock_outputs")
        return TokenHubCompletion(
            content=json.dumps(self.outputs.pop(0), ensure_ascii=False),
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        )


def _product_turn_output() -> dict[str, object]:
    return {
        "assistant_message": "我已记录产品理解：你们做中小企业财税 SaaS。",
        "actions": [
            {
                "type": "write_memory",
                "payload": {
                    "id": "mem_product",
                    "status": "observed",
                    "content": "产品是中小企业财税 SaaS",
                    "source": "user",
                    "evidence": ["我们做中小企业财税 SaaS。"],
                    "confidence": 0.95,
                    "tags": ["product"],
                },
            },
            {
                "type": "update_working_state",
                "payload": {"product_understanding": ["产品是中小企业财税 SaaS"]},
            },
        ],
        "reasoning_summary": "用户给出产品信息。",
        "confidence": 0.95,
    }


def _hypothesis_turn_output() -> dict[str, object]:
    return {
        "assistant_message": "当前假设是先找中小企业老板和财务负责人验证需求。",
        "actions": [
            {
                "type": "write_memory",
                "payload": {
                    "id": "mem_target_hypothesis",
                    "status": "hypothesis",
                    "content": "可能优先找中小企业老板和财务负责人",
                    "source": "agent",
                    "confidence": 0.62,
                    "tags": ["customer_intelligence"],
                },
            },
            {
                "type": "update_working_state",
                "payload": {"current_hypotheses": ["可能优先找中小企业老板和财务负责人"]},
            },
            {
                "type": "update_customer_intelligence",
                "payload": {
                    "target_industries": ["中小企业服务"],
                    "target_roles": ["老板", "财务负责人"],
                    "candidates": [
                        {
                            "id": "cand_sme_owner",
                            "name": "华东中小企业老板",
                            "segment": "中小企业",
                            "target_roles": ["老板", "财务负责人"],
                            "ranking_reason": "直接感知财税 SaaS 的经营价值",
                            "score": 70,
                            "validation_signals": ["是否有财税合规压力"],
                        }
                    ],
                    "ranking_reasons": ["老板和财务负责人可能共同参与财税软件决策"],
                    "scoring_draft": {"cand_sme_owner": 70},
                    "validation_signals": ["是否有财税合规压力"],
                },
            },
        ],
        "reasoning_summary": "形成客户情报假设。",
        "confidence": 0.7,
    }


def _correction_turn_output() -> dict[str, object]:
    return {
        "assistant_message": "收到，目标联系人改为老板本人，旧的财务负责人假设已废弃。",
        "actions": [
            {
                "type": "write_memory",
                "payload": {
                    "id": "mem_target_corrected",
                    "status": "confirmed",
                    "content": "目标联系人是老板本人，不是财务负责人",
                    "source": "user",
                    "evidence": ["纠正一下，不是财务负责人，是老板本人。"],
                    "confidence": 0.98,
                    "supersedes": ["mem_target_hypothesis"],
                    "tags": ["correction", "customer_intelligence"],
                },
            },
            {
                "type": "update_working_state",
                "payload": {"correction_summary": ["目标联系人已从财务负责人纠正为老板本人"]},
            },
            {
                "type": "update_customer_intelligence",
                "payload": {
                    "target_roles": ["老板本人"],
                    "ranking_reasons": ["用户纠正后优先围绕老板本人验证"],
                    "validation_signals": ["老板是否直接负责财税 SaaS 采购"],
                },
            },
        ],
        "reasoning_summary": "用户纠正目标联系人。",
        "confidence": 0.98,
    }


def _followup_turn_output() -> dict[str, object]:
    return {
        "assistant_message": "下一步建议只围绕老板本人设计首轮访谈，先验证采购触发点和预算判断。",
        "actions": [{"type": "no_op", "payload": {}}],
        "reasoning_summary": "根据纠错后的 active memory 给出建议。",
        "confidence": 0.86,
    }
