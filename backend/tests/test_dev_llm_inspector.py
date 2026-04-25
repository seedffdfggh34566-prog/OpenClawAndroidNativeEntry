from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.config import reset_settings_cache
from backend.api.database import reset_database_state
from backend.runtime.llm_client import TokenHubClientError, TokenHubCompletion


def _product_learning_content() -> str:
    return json.dumps(
        {
            "target_customers": ["销售负责人", "创始人"],
            "target_industries": ["企业服务"],
            "typical_use_cases": ["梳理产品表达", "生成获客分析输入"],
            "pain_points_solved": ["产品价值表达不清"],
            "core_advantages": ["先讲清产品再做销售分析"],
            "delivery_model": "mobile_control_entry + local_backend",
            "constraints": ["当前仍需人工确认"],
            "missing_fields": [],
            "confidence_score": 82,
        },
        ensure_ascii=False,
    )


def _lead_analysis_content() -> str:
    return json.dumps(
        {
            "title": "AI 销售助手 V1 获客分析结果",
            "analysis_scope": "基于已确认产品画像的获客方向分析",
            "summary": "优先面向企业服务团队验证产品表达和获客分析价值。",
            "priority_industries": ["企业服务", "中小企业数字化"],
            "priority_customer_types": ["销售负责人", "创始人"],
            "scenario_opportunities": [
                "围绕梳理产品表达验证首轮销售转化",
                "邻近机会：拓展到同样需要结构化销售表达的运营负责人",
                "上下游机会：从销售负责人延伸到市场获客和客户成功团队",
            ],
            "ranking_explanations": [
                "企业服务团队通常更容易感知产品价值表达不清带来的获客损失。",
                "销售负责人更接近转化结果，能快速反馈分析是否可执行。",
            ],
            "recommendations": [
                "首轮销售验证建议：访谈 5 到 10 个销售负责人，确认分析结果是否能支持跟进。",
                "不建议优先同时铺开过多行业；先验证企业服务团队的反馈质量。",
            ],
            "risks": ["当前仍需人工确认产品画像。"],
            "limitations": ["当前分析主要基于已确认产品画像，尚未接入外部检索。"],
        },
        ensure_ascii=False,
    )


def _mock_tokenhub_completion(*args, **kwargs) -> TokenHubCompletion:
    messages = next((arg for arg in args if isinstance(arg, list)), None)
    if messages and any("获客分析节点" in item.get("content", "") for item in messages):
        return TokenHubCompletion(
            content=_lead_analysis_content(),
            usage={"prompt_tokens": 70, "completion_tokens": 150, "total_tokens": 220},
        )
    return TokenHubCompletion(
        content=f"<think>先分析输入。</think>\n```json\n{_product_learning_content()}\n```",
        usage={"prompt_tokens": 40, "completion_tokens": 88, "total_tokens": 128},
    )


def _create_trace_client(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    completion: Callable[..., TokenHubCompletion],
) -> tuple[TestClient, Path]:
    trace_dir = tmp_path / "llm-traces"
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", database_url)
    monkeypatch.delenv("OPENCLAW_BACKEND_DATABASE_PATH", raising=False)
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-secret-key")
    monkeypatch.setenv("OPENCLAW_BACKEND_DEV_LLM_TRACE_ENABLED", "true")
    monkeypatch.setenv("OPENCLAW_BACKEND_DEV_LLM_TRACE_DIR", str(trace_dir))
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete",
        completion,
    )
    reset_settings_cache()
    reset_database_state()

    from backend.api.main import create_app

    return TestClient(create_app()), trace_dir


def test_dev_llm_inspector_routes_are_disabled_by_default(client) -> None:
    assert client.get("/dev/llm-runs").status_code == 404
    assert client.get("/dev/llm-runs/run_missing").status_code == 404
    assert client.get("/dev/llm-inspector").status_code == 404


def test_product_learning_trace_records_raw_content_and_parsed_draft(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, trace_dir = _create_trace_client(tmp_path, monkeypatch, _mock_tokenhub_completion)
    with client:
        response = client.post(
            "/product-profiles",
            json={
                "name": "AI 销售助手 V1",
                "one_line_description": "帮助用户先讲清产品，再生成获客分析结果。",
                "source_notes": "用于 inspector 测试。",
            },
        )
        assert response.status_code == 200
        run_id = response.json()["current_run"]["id"]

        detail_response = client.get(f"/dev/llm-runs/{run_id}")
        assert detail_response.status_code == 200
        trace = detail_response.json()
        assert trace["run_id"] == run_id
        assert trace["run_type"] == "product_learning"
        assert trace["parse_status"] == "succeeded"
        assert "<think>" in trace["raw_content"]
        assert trace["parsed_draft"]["target_customers"] == ["销售负责人", "创始人"]
        assert trace["usage"]["total_tokens"] == 128
        assert trace["duration_ms"] >= 0
        assert trace_dir.exists()

        list_response = client.get("/dev/llm-runs")
        assert list_response.status_code == 200
        summaries = list_response.json()["llm_runs"]
        assert summaries[0]["run_id"] == run_id
        assert summaries[0]["total_tokens"] == 128

        inspector_response = client.get("/dev/llm-inspector")
        assert inspector_response.status_code == 200
        assert "OpenClaw LLM Run Inspector" in inspector_response.text
        assert "Raw content" in inspector_response.text
        assert "Parsed draft" in inspector_response.text
        assert "Full trace JSON" in inspector_response.text
        assert "test-secret-key" not in json.dumps(trace, ensure_ascii=False)


def test_lead_analysis_trace_records_llm_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _ = _create_trace_client(tmp_path, monkeypatch, _mock_tokenhub_completion)
    with client:
        create_response = client.post(
            "/product-profiles",
            json={
                "name": "AI 销售助手 V1",
                "one_line_description": "帮助用户先讲清产品，再生成获客分析结果。",
                "source_notes": "用于 inspector 测试。",
            },
        )
        assert create_response.status_code == 200
        product_profile_id = create_response.json()["product_profile"]["id"]
        assert client.post(f"/product-profiles/{product_profile_id}/confirm").status_code == 200

        run_response = client.post(
            "/analysis-runs",
            json={
                "run_type": "lead_analysis",
                "product_profile_id": product_profile_id,
                "lead_analysis_result_id": None,
                "trigger_source": "test_dev_llm_inspector",
            },
        )
        assert run_response.status_code == 200
        run_id = run_response.json()["agent_run"]["id"]

        detail_response = client.get(f"/dev/llm-runs/{run_id}")
        assert detail_response.status_code == 200
        trace = detail_response.json()
        assert trace["run_type"] == "lead_analysis"
        assert trace["prompt_version"] == "lead_analysis_llm_v1"
        assert trace["parse_status"] == "succeeded"
        assert trace["parsed_draft"]["analysis_scope"] == "基于已确认产品画像的获客方向分析"
        assert trace["usage"]["total_tokens"] == 220


def test_trace_records_parse_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def invalid_json_completion(*args, **kwargs) -> TokenHubCompletion:
        return TokenHubCompletion(
            content="<think>无法输出 JSON</think>不是 JSON",
            usage={"total_tokens": 8},
        )

    client, _ = _create_trace_client(tmp_path, monkeypatch, invalid_json_completion)
    with client:
        response = client.post(
            "/product-profiles",
            json={
                "name": "AI 销售助手 V1",
                "one_line_description": "帮助用户先讲清产品，再生成获客分析结果。",
                "source_notes": "用于 inspector 失败测试。",
            },
        )
        assert response.status_code == 200
        run_id = response.json()["current_run"]["id"]
        run_response = client.get(f"/analysis-runs/{run_id}")
        assert run_response.json()["agent_run"]["status"] == "failed"

        detail_response = client.get(f"/dev/llm-runs/{run_id}")
        assert detail_response.status_code == 200
        trace = detail_response.json()
        assert trace["parse_status"] == "failed"
        assert trace["error_type"] == "ValueError"
        assert "product_learning_llm_json_object_not_found" in trace["error_message"]
        assert trace["raw_content"] == "<think>无法输出 JSON</think>不是 JSON"


def test_trace_records_request_failure_without_secret(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def timeout_completion(*args, **kwargs) -> TokenHubCompletion:
        raise TokenHubClientError("tokenhub_request_timeout")

    client, _ = _create_trace_client(tmp_path, monkeypatch, timeout_completion)
    with client:
        response = client.post(
            "/product-profiles",
            json={
                "name": "AI 销售助手 V1",
                "one_line_description": "帮助用户先讲清产品，再生成获客分析结果。",
                "source_notes": "用于 inspector request failure 测试。",
            },
        )
        assert response.status_code == 200
        run_id = response.json()["current_run"]["id"]

        detail_response = client.get(f"/dev/llm-runs/{run_id}")
        assert detail_response.status_code == 200
        trace = detail_response.json()
        assert trace["parse_status"] == "request_failed"
        assert trace["raw_content"] is None
        assert trace["parsed_draft"] is None
        assert trace["usage"] == {}
        assert trace["error_type"] == "TokenHubClientError"
        trace_text = json.dumps(trace, ensure_ascii=False)
        assert "test-secret-key" not in trace_text
        assert "Authorization" not in trace_text
