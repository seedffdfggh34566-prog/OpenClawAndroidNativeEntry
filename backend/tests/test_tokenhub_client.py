from __future__ import annotations

import json

import httpx
import pytest

from backend.runtime.graphs.product_learning import _parse_product_learning_json
from backend.runtime.llm_client import TokenHubClient, TokenHubClientError


def test_tokenhub_client_returns_content_and_usage() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert request.headers["Authorization"] == "Bearer test-key"
        assert payload["model"] == "minimax-m2.5"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": '{"target_customers":["销售负责人"],"confidence_score":80}'
                        }
                    }
                ],
                "usage": {"total_tokens": 32},
            },
        )

    client = TokenHubClient(
        api_key="test-key",
        base_url="https://tokenhub.tencentmaas.com/v1",
        model="minimax-m2.5",
        timeout_seconds=5,
        transport=httpx.MockTransport(handler),
    )

    completion = client.complete([{"role": "user", "content": "hello"}])

    assert "target_customers" in completion.content
    assert completion.usage["total_tokens"] == 32


def test_tokenhub_client_raises_for_http_error() -> None:
    client = TokenHubClient(
        api_key="test-key",
        base_url="https://tokenhub.tencentmaas.com/v1",
        model="minimax-m2.5",
        timeout_seconds=5,
        transport=httpx.MockTransport(lambda request: httpx.Response(403, text="forbidden")),
    )

    with pytest.raises(TokenHubClientError, match="tokenhub_http_error:403"):
        client.complete([{"role": "user", "content": "hello"}])


def test_tokenhub_client_raises_for_server_error() -> None:
    client = TokenHubClient(
        api_key="test-key",
        base_url="https://tokenhub.tencentmaas.com/v1",
        model="minimax-m2.5",
        timeout_seconds=5,
        transport=httpx.MockTransport(
            lambda request: httpx.Response(500, text="server error")
        ),
    )

    with pytest.raises(TokenHubClientError, match="tokenhub_http_error:500"):
        client.complete([{"role": "user", "content": "hello"}])


def test_tokenhub_client_requires_api_key() -> None:
    client = TokenHubClient(
        api_key=None,
        base_url="https://tokenhub.tencentmaas.com/v1",
        model="minimax-m2.5",
        timeout_seconds=5,
    )

    with pytest.raises(TokenHubClientError, match="tokenhub_api_key_missing"):
        client.complete([{"role": "user", "content": "hello"}])


def test_parse_product_learning_json_strips_thinking_and_markdown() -> None:
    parsed = _parse_product_learning_json(
        """
        <think>内部推理不应进入 JSON。</think>

        ```json
        {
          "target_customers": ["销售负责人"],
          "target_industries": ["企业服务"],
          "typical_use_cases": ["梳理产品表达"],
          "pain_points_solved": ["产品价值表达不清"],
          "core_advantages": ["结构化输出"],
          "delivery_model": "mobile_control_entry + local_backend",
          "constraints": ["需要人工确认"],
          "missing_fields": [],
          "confidence_score": 86
        }
        ```
        """
    )

    assert parsed["target_customers"] == ["销售负责人"]
    assert parsed["confidence_score"] == 86


def test_parse_product_learning_json_rejects_non_json() -> None:
    with pytest.raises(ValueError, match="product_learning_llm_json_object_not_found"):
        _parse_product_learning_json("<think>only thinking</think>没有 JSON")
