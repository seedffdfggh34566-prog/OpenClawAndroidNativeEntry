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


@pytest.fixture
def backend_env(tmp_path, monkeypatch) -> Generator[str, None, None]:
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", database_url)
    monkeypatch.delenv("OPENCLAW_BACKEND_DATABASE_PATH", raising=False)
    monkeypatch.setattr(
        "backend.runtime.graphs.product_learning.TokenHubClient.complete",
        _mock_product_learning_completion,
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
