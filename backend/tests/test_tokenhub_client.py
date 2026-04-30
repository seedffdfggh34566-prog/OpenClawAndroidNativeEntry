from __future__ import annotations

import json

import httpx
import pytest

from backend.runtime.graphs.lead_analysis import _parse_lead_analysis_json
from backend.runtime.graphs.product_learning import _parse_product_learning_json
from backend.runtime.llm_client import TokenHubClient, TokenHubClientError
from backend.runtime.tokenhub_native_fc import tokenhub_native_fc_request_policy


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
    assert completion.tool_calls is None


def test_tokenhub_client_complete_with_tools_sends_tools_and_parses_tool_calls() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert request.headers["Authorization"] == "Bearer test-key"
        assert payload["model"] == "minimax-m2.7"
        assert payload["tools"][0]["function"]["name"] == "upsert_memory"
        assert payload["tool_choice"] == "required"
        assert payload["temperature"] == 0
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "tool_calls",
                        "message": {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "type": "function",
                                    "function": {
                                        "name": "upsert_memory",
                                        "arguments": '{"label":"product","content":"销售培训"}',
                                    },
                                }
                            ],
                        },
                    }
                ],
                "usage": {"total_tokens": 18},
            },
        )

    client = TokenHubClient(
        api_key="test-key",
        base_url="https://tokenhub.tencentmaas.com/v1",
        model="minimax-m2.7",
        timeout_seconds=5,
        transport=httpx.MockTransport(handler),
    )

    completion = client.complete_with_tools(
        [{"role": "user", "content": "记住我们做销售培训"}],
        tools=[_upsert_memory_tool()],
        tool_choice="required",
    )

    assert completion.content == ""
    assert completion.finish_reason == "tool_calls"
    assert completion.usage["total_tokens"] == 18
    assert completion.raw_message is not None
    assert completion.tool_calls is not None
    assert completion.tool_calls[0].id == "call_1"
    assert completion.tool_calls[0].function.name == "upsert_memory"
    assert json.loads(completion.tool_calls[0].function.arguments)["label"] == "product"


def test_tokenhub_client_complete_with_tools_applies_model_policy() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert payload["temperature"] == 0.6
        assert payload["thinking"] == {"type": "disabled"}
        assert payload["reasoning_effort"] == "low"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "tool_calls",
                        "message": {
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "call_policy",
                                    "type": "function",
                                    "function": {"name": "upsert_memory", "arguments": "{}"},
                                }
                            ],
                        },
                    }
                ],
                "usage": {},
            },
        )

    client = TokenHubClient(
        api_key="test-key",
        base_url="https://tokenhub.tencentmaas.com/v1",
        model="kimi-k2.6",
        timeout_seconds=5,
        transport=httpx.MockTransport(handler),
    )

    completion = client.complete_with_tools(
        [{"role": "user", "content": "call tool"}],
        tools=[_upsert_memory_tool()],
        tool_choice={"type": "function", "function": {"name": "upsert_memory"}},
        model_policy={"temperature": 0.6, "thinking": {"type": "disabled"}, "reasoning_effort": "low"},
    )

    assert completion.tool_calls is not None
    assert completion.tool_calls[0].id == "call_policy"


def test_tokenhub_native_fc_model_policy_handles_model_specific_parameters() -> None:
    assert tokenhub_native_fc_request_policy("minimax-m2.7", "required") == {"temperature": 0}
    assert tokenhub_native_fc_request_policy("kimi-k2.6", "auto") == {"temperature": 1}
    assert tokenhub_native_fc_request_policy("kimi-k2.6", "required") == {
        "temperature": 0.6,
        "thinking": {"type": "disabled"},
    }
    assert tokenhub_native_fc_request_policy(
        "deepseek-v4-flash",
        {"type": "function", "function": {"name": "upsert_memory"}},
    ) == {"temperature": 0, "thinking": {"type": "disabled"}}


def test_tokenhub_client_complete_with_tools_rejects_missing_content_and_tool_calls() -> None:
    client = TokenHubClient(
        api_key="test-key",
        base_url="https://tokenhub.tencentmaas.com/v1",
        model="minimax-m2.7",
        timeout_seconds=5,
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"choices": [{"message": {"content": ""}}]})
        ),
    )

    with pytest.raises(TokenHubClientError, match="tokenhub_response_missing_content_and_tool_calls"):
        client.complete_with_tools(
            [{"role": "user", "content": "call tool"}],
            tools=[_upsert_memory_tool()],
        )


def test_tokenhub_client_complete_with_tools_rejects_malformed_tool_calls() -> None:
    client = TokenHubClient(
        api_key="test-key",
        base_url="https://tokenhub.tencentmaas.com/v1",
        model="minimax-m2.7",
        timeout_seconds=5,
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "message": {
                                "content": "",
                                "tool_calls": [
                                    {
                                        "id": "call_bad",
                                        "type": "function",
                                        "function": {"name": "upsert_memory", "arguments": {}},
                                    }
                                ],
                            }
                        }
                    ]
                },
            )
        ),
    )

    with pytest.raises(TokenHubClientError, match="tokenhub_response_tool_call_arguments_not_string"):
        client.complete_with_tools(
            [{"role": "user", "content": "call tool"}],
            tools=[_upsert_memory_tool()],
        )


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


def test_tokenhub_client_complete_with_tools_requires_tools() -> None:
    client = TokenHubClient(
        api_key="test-key",
        base_url="https://tokenhub.tencentmaas.com/v1",
        model="minimax-m2.7",
        timeout_seconds=5,
    )

    with pytest.raises(TokenHubClientError, match="tokenhub_tools_required"):
        client.complete_with_tools([{"role": "user", "content": "hello"}], tools=[])


def _upsert_memory_tool() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "upsert_memory",
            "description": "Create or update a memory block.",
            "parameters": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["label", "content"],
            },
        },
    }


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


def test_parse_lead_analysis_json_strips_thinking_and_markdown() -> None:
    parsed = _parse_lead_analysis_json(
        """
        <think>内部推理不应进入 JSON。</think>

        ```json
        {
          "title": "AI 销售助手 V1 获客分析结果",
          "analysis_scope": "基于已确认产品画像的获客方向分析",
          "summary": "优先验证企业服务团队。",
          "priority_industries": ["企业服务"],
          "priority_customer_types": ["销售负责人"],
          "scenario_opportunities": ["邻近机会：拓展运营负责人", "上下游机会：延伸到市场团队"],
          "ranking_explanations": ["销售负责人更接近转化结果。"],
          "recommendations": ["首轮销售验证建议：访谈销售负责人。", "不建议优先铺开过多行业。"],
          "risks": ["样本有限。"],
          "limitations": ["未接入外部检索。"]
        }
        ```
        """
    )

    assert parsed["analysis_scope"] == "基于已确认产品画像的获客方向分析"
    assert "邻近机会" in parsed["scenario_opportunities"][0]


def test_parse_lead_analysis_json_skips_invalid_prefix_braces() -> None:
    parsed = _parse_lead_analysis_json(
        """
        模型前缀中可能出现非 JSON 花括号：{不是合法 JSON。

        {
          "title": "工厂设备巡检助手获客分析",
          "analysis_scope": "基于已确认产品画像的获客方向分析",
          "summary": "优先验证制造业设备主管。",
          "priority_industries": ["制造业"],
          "priority_customer_types": ["设备主管"],
          "scenario_opportunities": ["邻近机会：拓展维修班组", "上下游机会：延伸到设备维护服务商"],
          "ranking_explanations": ["设备主管直接面对巡检漏项和维修响应问题。"],
          "recommendations": ["首轮销售验证建议：访谈设备主管。", "不建议优先覆盖泛工业客户。"],
          "risks": ["需要验证现场网络和离线同步。"],
          "limitations": ["未接入外部检索。"]
        }
        """
    )

    assert parsed["priority_industries"] == ["制造业"]


def test_parse_lead_analysis_json_repairs_extra_tail_object_brace() -> None:
    parsed = _parse_lead_analysis_json(
        """
        <think>模型没有关闭 think 标签。

        {"title":"门店会员复购助手获客方向分析","analysis_scope":"基于已确认产品画像的获客方向分析","summary":"优先验证本地生活门店。","priority_industries":["美容美发"],"priority_customer_types":["门店老板"],"scenario_opportunities":["邻近机会：拓展社区零售","上下游机会：联动 POS 服务商"],"ranking_explanations":["会员复购痛点明确。"],"recommendations":["首轮销售验证建议：访谈门店老板。","不建议优先覆盖大型连锁。"],"risks":["价格敏感。"],"limitations":["跨区域复制需考虑各地消费习惯"}]}
        """
    )

    assert parsed["limitations"] == ["跨区域复制需考虑各地消费习惯"]


def test_parse_lead_analysis_json_repairs_missing_array_close_at_tail() -> None:
    parsed = _parse_lead_analysis_json(
        """
        {"title":"门店经营异常助手获客方向分析","analysis_scope":"基于已确认产品画像的获客方向分析","summary":"优先验证多门店服务业。","priority_industries":["餐饮服务"],"priority_customer_types":["多店老板"],"scenario_opportunities":["邻近机会：拓展洗衣门店","上下游机会：联动 POS 服务商"],"ranking_explanations":["多门店管理痛点明确。"],"recommendations":["首轮销售验证建议：访谈区域经理。","不建议优先覆盖单店客户。"],"risks":["数据接入成本。"],"limitations":["产品细节功能文档需补充完整"}
        """
    )

    assert parsed["limitations"] == ["产品细节功能文档需补充完整"]


def test_parse_lead_analysis_json_rejects_non_json() -> None:
    with pytest.raises(ValueError, match="lead_analysis_llm_json_object_not_found"):
        _parse_lead_analysis_json("<think>only thinking</think>没有 JSON")
