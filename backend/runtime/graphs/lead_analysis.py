from __future__ import annotations

import json
import re
from typing import Any

from langgraph.graph import END, START, StateGraph

from backend.api.config import get_settings
from backend.runtime.llm_client import TokenHubClient
from backend.runtime.types import (
    LeadAnalysisDraft,
    LeadAnalysisDraftResult,
    LeadAnalysisGraphState,
    ProductProfileRuntimePayload,
)


def _compact(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = value.strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _infer_priority_industries(profile: ProductProfileRuntimePayload) -> list[str]:
    if profile.target_industries:
        return _compact(profile.target_industries)[:3]

    text = f"{profile.name} {profile.one_line_description} {profile.source_notes or ''}".lower()
    inferred: list[str] = []
    keyword_map = [
        ("教育", "教育培训"),
        ("学校", "教育培训"),
        ("saas", "企业服务"),
        ("软件", "企业服务"),
        ("工厂", "制造业"),
        ("制造", "制造业"),
        ("零售", "零售连锁"),
        ("门店", "零售连锁"),
        ("医疗", "医疗健康"),
        ("诊所", "医疗健康"),
        ("物流", "物流供应链"),
    ]
    for keyword, label in keyword_map:
        if keyword in text:
            inferred.append(label)
    if not inferred:
        inferred = ["企业服务", "中小企业数字化", "渠道合作"]
    return _compact(inferred)[:3]


def _infer_customer_types(profile: ProductProfileRuntimePayload) -> list[str]:
    if profile.target_customers:
        return _compact(profile.target_customers)[:3]

    inferred: list[str] = []
    if "销售" in profile.one_line_description or "客户" in profile.one_line_description:
        inferred.append("销售负责人")
    if "老板" in profile.one_line_description or "企业" in profile.one_line_description:
        inferred.append("中小企业老板")
    inferred.extend(["业务负责人", "运营负责人"])
    return _compact(inferred)[:3]


def _infer_scenarios(profile: ProductProfileRuntimePayload) -> list[str]:
    if profile.typical_use_cases:
        return _compact(profile.typical_use_cases)[:4]

    scenarios = [f"围绕 {profile.name} 做产品定位澄清"]
    if profile.pain_points_solved:
        scenarios.append(f"优先验证“{profile.pain_points_solved[0]}”是否能形成明确销售切口")
    scenarios.append("在首次沟通中快速说明产品价值")
    return _compact(scenarios)[:4]


def _build_lead_analysis_messages(
    profile: ProductProfileRuntimePayload,
    context: dict[str, Any],
) -> list[dict[str, str]]:
    schema = {
        "title": "报告标题，字符串",
        "analysis_scope": "固定为：基于已确认产品画像的获客方向分析",
        "summary": "获客分析摘要，字符串",
        "priority_industries": ["优先行业，字符串数组"],
        "priority_customer_types": ["优先客户类型，字符串数组"],
        "scenario_opportunities": ["场景机会，字符串数组"],
        "ranking_explanations": ["优先级判断依据，字符串数组"],
        "recommendations": ["销售验证建议，字符串数组"],
        "risks": ["风险，字符串数组"],
        "limitations": ["限制，字符串数组"],
    }
    product_input = {
        "name": profile.name,
        "one_line_description": profile.one_line_description,
        "source_notes": profile.source_notes or "",
        "target_customers": profile.target_customers,
        "target_industries": profile.target_industries,
        "typical_use_cases": profile.typical_use_cases,
        "pain_points_solved": profile.pain_points_solved,
        "core_advantages": profile.core_advantages,
        "delivery_model": profile.delivery_model,
        "constraints": profile.constraints,
        "missing_fields": profile.missing_fields,
        "inferred_context": {
            "priority_industries": context["industries"],
            "customer_types": context["customer_types"],
            "scenarios": context["scenarios"],
            "primary_pain": context["primary_pain"],
            "primary_advantage": context["primary_advantage"],
        },
    }
    return [
        {
            "role": "system",
            "content": (
                "你是 AI 销售助手 V1 的获客分析节点。"
                "你的任务是基于已确认产品画像生成结构化 LeadAnalysisDraft。"
                "只根据输入材料和合理业务归纳分析，不要编造具体客户名称、真实案例、价格、市场份额或外部事实。"
                "输出必须面向业务用户，不要出现 Phase 1、LangGraph、runtime、v1_langgraph_phase1 等工程词。"
                "只输出一个 JSON object，不要输出 markdown、解释或额外文本。"
            ),
        },
        {
            "role": "user",
            "content": (
                "请生成获客分析草稿。\n"
                "输出必须是单个 JSON object，字段必须严格匹配 output_schema。\n"
                "analysis_scope 固定输出“基于已确认产品画像的获客方向分析”。\n"
                "priority_industries、priority_customer_types、scenario_opportunities、"
                "ranking_explanations、recommendations、risks、limitations 应尽量各输出 2 到 5 条。\n"
                "scenario_opportunities 必须包含至少一条“邻近机会：...”和一条“上下游机会：...”。\n"
                "recommendations 必须包含一条以“首轮销售验证建议：”开头的建议，"
                "也必须包含一条以“不建议优先”开头的建议。\n"
                "ranking_explanations 要说明为什么优先这些行业、客户和场景，不要只复述字段。\n\n"
                "每条数组内容控制在 80 个中文字符以内，避免长篇展开。\n\n"
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


def _parse_lead_analysis_json(content: str) -> dict[str, object]:
    text = _strip_thinking_and_fences(content)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("lead_analysis_llm_json_object_not_found")
    try:
        parsed = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError("lead_analysis_llm_json_decode_failed") from exc
    if not isinstance(parsed, dict):
        raise ValueError("lead_analysis_llm_json_object_required")
    return parsed


def _token_count(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float) and value.is_integer():
        count = int(value)
        return count if count >= 0 else None
    return None


def _normalize_llm_usage(usage: dict[str, Any]) -> dict[str, int]:
    normalized: dict[str, int] = {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        count = _token_count(usage.get(key))
        if count is not None:
            normalized[key] = count

    prompt_details = usage.get("prompt_tokens_details")
    if isinstance(prompt_details, dict):
        cached_tokens = _token_count(prompt_details.get("cached_tokens"))
        if cached_tokens is not None:
            normalized["cached_tokens"] = cached_tokens

    completion_details = usage.get("completion_tokens_details")
    if isinstance(completion_details, dict):
        reasoning_tokens = _token_count(completion_details.get("reasoning_tokens"))
        if reasoning_tokens is not None:
            normalized["reasoning_tokens"] = reasoning_tokens

    for key in ("cached_tokens", "reasoning_tokens"):
        count = _token_count(usage.get(key))
        if count is not None:
            normalized[key] = count

    return normalized


def load_confirmed_product_profile(
    state: LeadAnalysisGraphState,
) -> LeadAnalysisGraphState:
    profile = state["product_profile_payload"]
    if profile.status != "confirmed":
        raise ValueError("lead_analysis_requires_confirmed_product_profile")
    return {"product_profile_id": profile.id}


def normalize_product_profile_context(
    state: LeadAnalysisGraphState,
) -> LeadAnalysisGraphState:
    profile = state["product_profile_payload"]
    industries = _infer_priority_industries(profile)
    customer_types = _infer_customer_types(profile)
    scenarios = _infer_scenarios(profile)
    return {
        "normalized_context": {
            "industries": industries,
            "customer_types": customer_types,
            "scenarios": scenarios,
            "primary_advantage": (profile.core_advantages or ["先帮助用户讲清产品"])[0],
            "primary_pain": (profile.pain_points_solved or ["销售表达仍需继续收口"])[0],
            "missing_fields": profile.missing_fields,
            "constraints": profile.constraints,
        }
    }


def generate_lead_analysis_draft(
    state: LeadAnalysisGraphState,
) -> LeadAnalysisGraphState:
    settings = get_settings()
    profile = state["product_profile_payload"]
    context = state["normalized_context"]
    client = TokenHubClient(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        timeout_seconds=max(settings.llm_timeout_seconds, 60.0),
    )
    completion = client.complete(_build_lead_analysis_messages(profile, context))
    draft = LeadAnalysisDraft.model_validate(_parse_lead_analysis_json(completion.content))
    llm_usage = _normalize_llm_usage(completion.usage)
    return {
        "draft_output": draft,
        "runtime_metadata": {"llm_usage": llm_usage} if llm_usage else {},
    }


def validate_lead_analysis_draft(
    state: LeadAnalysisGraphState,
) -> LeadAnalysisGraphState:
    draft = LeadAnalysisDraft.model_validate(state["draft_output"])
    return {"draft_output": draft}


def return_draft_payload(
    state: LeadAnalysisGraphState,
) -> LeadAnalysisGraphState:
    return {
        "draft_output": state["draft_output"],
        "runtime_metadata": state.get("runtime_metadata", {}),
    }


_builder = StateGraph(LeadAnalysisGraphState)
_builder.add_node("load_confirmed_product_profile", load_confirmed_product_profile)
_builder.add_node("normalize_product_profile_context", normalize_product_profile_context)
_builder.add_node("generate_lead_analysis_draft", generate_lead_analysis_draft)
_builder.add_node("validate_lead_analysis_draft", validate_lead_analysis_draft)
_builder.add_node("return_draft_payload", return_draft_payload)
_builder.add_edge(START, "load_confirmed_product_profile")
_builder.add_edge("load_confirmed_product_profile", "normalize_product_profile_context")
_builder.add_edge("normalize_product_profile_context", "generate_lead_analysis_draft")
_builder.add_edge("generate_lead_analysis_draft", "validate_lead_analysis_draft")
_builder.add_edge("validate_lead_analysis_draft", "return_draft_payload")
_builder.add_edge("return_draft_payload", END)
LEAD_ANALYSIS_GRAPH = _builder.compile()


def invoke_lead_analysis_graph(
    *,
    run_id: str,
    product_profile_payload: ProductProfileRuntimePayload,
) -> LeadAnalysisDraftResult:
    state = LEAD_ANALYSIS_GRAPH.invoke(
        {
            "run_id": run_id,
            "run_type": "lead_analysis",
            "product_profile_id": product_profile_payload.id,
            "product_profile_payload": product_profile_payload,
        }
    )
    return LeadAnalysisDraftResult(
        draft=LeadAnalysisDraft.model_validate(state["draft_output"]),
        runtime_metadata=dict(state.get("runtime_metadata", {})),
    )
