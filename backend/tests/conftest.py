from __future__ import annotations

import json
import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.config import reset_settings_cache
from backend.api.database import get_session_factory, reset_database_state
from backend.runtime.llm_client import TokenHubCompletion


def _mock_product_learning_completion(*args, **kwargs) -> TokenHubCompletion:
    return TokenHubCompletion(
        content=json.dumps(
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
        ),
        usage={
            "prompt_tokens": 40,
            "completion_tokens": 88,
            "total_tokens": 128,
            "prompt_tokens_details": {"cached_tokens": 12},
            "completion_tokens_details": {"reasoning_tokens": 0},
        },
    )


def _mock_lead_analysis_completion(*args, **kwargs) -> TokenHubCompletion:
    return TokenHubCompletion(
        content=json.dumps(
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
                    "首轮销售验证建议：访谈 5 到 10 个销售负责人，确认当前表达和分析结果是否能支持真实跟进。",
                    "不建议优先同时铺开过多行业；先验证企业服务团队的反馈质量。",
                ],
                "risks": ["当前仍需人工确认产品画像。"],
                "limitations": ["当前分析主要基于已确认产品画像，尚未接入外部检索。"],
            },
            ensure_ascii=False,
        ),
        usage={
            "prompt_tokens": 70,
            "completion_tokens": 150,
            "total_tokens": 220,
            "prompt_tokens_details": {"cached_tokens": 8},
            "completion_tokens_details": {"reasoning_tokens": 0},
        },
    )


def _mock_tokenhub_completion(*args, **kwargs) -> TokenHubCompletion:
    messages = next((arg for arg in args if isinstance(arg, list)), None)
    if messages and any("获客分析节点" in item.get("content", "") for item in messages):
        return _mock_lead_analysis_completion()
    return _mock_product_learning_completion()


@pytest.fixture
def backend_env(tmp_path, monkeypatch) -> Generator[str, None, None]:
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", database_url)
    monkeypatch.delenv("OPENCLAW_BACKEND_DATABASE_PATH", raising=False)
    monkeypatch.delenv("OPENCLAW_BACKEND_DEV_LLM_TRACE_ENABLED", raising=False)
    monkeypatch.delenv("OPENCLAW_BACKEND_DEV_LLM_TRACE_DIR", raising=False)
    monkeypatch.delenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR", raising=False)
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete",
        _mock_tokenhub_completion,
    )
    reset_settings_cache()
    reset_database_state()
    yield database_url
    reset_database_state()
    reset_settings_cache()
    os.environ.pop("OPENCLAW_BACKEND_DATABASE_URL", None)


@pytest.fixture
def app(backend_env):
    from backend.api.main import create_app

    return create_app()


@pytest.fixture
def client(app) -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session(app) -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
