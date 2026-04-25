from __future__ import annotations

import json
import re

from langgraph.graph import END, START, StateGraph

from backend.api.config import get_settings
from backend.api.product_learning import DEFAULT_DELIVERY_MODEL
from backend.runtime.llm_client import TokenHubClient
from backend.runtime.types import (
    ProductLearningDraft,
    ProductLearningGraphState,
    ProductProfileRuntimePayload,
)


def load_draft_product_profile(
    state: ProductLearningGraphState,
) -> ProductLearningGraphState:
    profile = state["product_profile_payload"]
    if profile.status != "draft":
        raise ValueError("product_learning_requires_draft_product_profile")
    return {"product_profile_id": profile.id}


def normalize_product_profile_context(
    state: ProductLearningGraphState,
) -> ProductLearningGraphState:
    profile = state["product_profile_payload"]
    return {
        "normalized_context": {
            "name": profile.name,
            "one_line_description": profile.one_line_description,
            "source_notes": profile.source_notes or "",
            "target_customers": profile.target_customers,
            "target_industries": profile.target_industries,
            "typical_use_cases": profile.typical_use_cases,
            "pain_points_solved": profile.pain_points_solved,
            "core_advantages": profile.core_advantages,
            "constraints": profile.constraints,
            "delivery_model": profile.delivery_model or DEFAULT_DELIVERY_MODEL,
            "confidence_score": profile.confidence_score or 0,
        }
    }


def _build_product_learning_messages(
    profile: ProductProfileRuntimePayload,
) -> list[dict[str, str]]:
    schema = {
        "target_customers": ["目标客户，字符串数组"],
        "target_industries": ["目标行业，字符串数组"],
        "typical_use_cases": ["典型使用场景，字符串数组"],
        "pain_points_solved": ["解决的痛点，字符串数组"],
        "core_advantages": ["核心优势，字符串数组"],
        "delivery_model": "交付方式，字符串或 null",
        "constraints": ["限制条件，字符串数组"],
        "missing_fields": [],
        "confidence_score": "0 到 100 的整数",
    }
    product_input = {
        "name": profile.name,
        "one_line_description": profile.one_line_description,
        "source_notes": profile.source_notes or "",
        "existing_fields": {
            "target_customers": profile.target_customers,
            "target_industries": profile.target_industries,
            "typical_use_cases": profile.typical_use_cases,
            "pain_points_solved": profile.pain_points_solved,
            "core_advantages": profile.core_advantages,
            "delivery_model": profile.delivery_model,
            "constraints": profile.constraints,
        },
    }
    return [
        {
            "role": "system",
            "content": (
                "你是 AI 销售助手 V1 的产品学习节点。"
                "你的任务是基于用户提供的产品材料生成结构化 ProductLearningDraft。"
                "只根据输入材料做合理归纳，不要编造价格、客户名称、具体案例或未提供事实。"
                "只输出一个 JSON object，不要输出 markdown、解释或额外文本。"
            ),
        },
        {
            "role": "user",
            "content": (
                "请补全以下产品学习草稿。\n"
                "输出必须是单个 JSON object，字段必须严格匹配 output_schema。\n"
                "如果信息不足，数组可为空；missing_fields 固定输出空数组，"
                "正式缺失字段将由后端规则计算。\n\n"
                f"output_schema:\n{json.dumps(schema, ensure_ascii=False)}\n\n"
                f"product_input:\n{json.dumps(product_input, ensure_ascii=False)}"
            ),
        },
    ]


def _strip_thinking_and_fences(content: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE)
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _parse_product_learning_json(content: str) -> dict[str, object]:
    text = _strip_thinking_and_fences(content)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("product_learning_llm_json_object_not_found")
    try:
        parsed = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError("product_learning_llm_json_decode_failed") from exc
    if not isinstance(parsed, dict):
        raise ValueError("product_learning_llm_json_object_required")
    return parsed


def generate_product_learning_draft(
    state: ProductLearningGraphState,
) -> ProductLearningGraphState:
    settings = get_settings()
    profile = state["product_profile_payload"]
    client = TokenHubClient(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        timeout_seconds=settings.llm_timeout_seconds,
    )
    completion = client.complete(_build_product_learning_messages(profile))
    draft = ProductLearningDraft.model_validate(
        _parse_product_learning_json(completion.content)
    )
    return {"draft_output": draft}


def validate_product_learning_draft(
    state: ProductLearningGraphState,
) -> ProductLearningGraphState:
    draft = ProductLearningDraft.model_validate(state["draft_output"])
    return {"draft_output": draft}


def return_draft_payload(
    state: ProductLearningGraphState,
) -> ProductLearningGraphState:
    return {"draft_output": state["draft_output"]}


_builder = StateGraph(ProductLearningGraphState)
_builder.add_node("load_draft_product_profile", load_draft_product_profile)
_builder.add_node("normalize_product_profile_context", normalize_product_profile_context)
_builder.add_node("generate_product_learning_draft", generate_product_learning_draft)
_builder.add_node("validate_product_learning_draft", validate_product_learning_draft)
_builder.add_node("return_draft_payload", return_draft_payload)
_builder.add_edge(START, "load_draft_product_profile")
_builder.add_edge("load_draft_product_profile", "normalize_product_profile_context")
_builder.add_edge("normalize_product_profile_context", "generate_product_learning_draft")
_builder.add_edge("generate_product_learning_draft", "validate_product_learning_draft")
_builder.add_edge("validate_product_learning_draft", "return_draft_payload")
_builder.add_edge("return_draft_payload", END)
PRODUCT_LEARNING_GRAPH = _builder.compile()


def invoke_product_learning_graph(
    *,
    run_id: str,
    product_profile_payload: ProductProfileRuntimePayload,
) -> ProductLearningDraft:
    state = PRODUCT_LEARNING_GRAPH.invoke(
        {
            "run_id": run_id,
            "run_type": "product_learning",
            "product_profile_id": product_profile_payload.id,
            "product_profile_payload": product_profile_payload,
        }
    )
    return ProductLearningDraft.model_validate(state["draft_output"])
