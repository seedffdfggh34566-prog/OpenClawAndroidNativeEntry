from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from backend.api.product_learning import DEFAULT_DELIVERY_MODEL
from backend.runtime.types import (
    ProductLearningDraft,
    ProductLearningGraphState,
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


def _combined_text(profile: ProductProfileRuntimePayload) -> str:
    return " ".join(
        part
        for part in [profile.name, profile.one_line_description, profile.source_notes or ""]
        if part
    ).lower()


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
    text = _combined_text(profile)

    target_customers = profile.target_customers or _compact(
        [
            "销售负责人" if "销售" in text or "获客" in text else "",
            "中小企业负责人" if "企业" in text or "saas" in text else "",
            "业务负责人",
        ]
    )
    target_industries = profile.target_industries or _compact(
        [
            "企业服务" if "saas" in text or "软件" in text or "企业" in text else "",
            "教育培训" if "教育" in text or "培训" in text else "",
            "零售连锁" if "门店" in text or "零售" in text else "",
        ]
    )
    use_cases = profile.typical_use_cases or _compact(
        [
            f"向潜在客户快速说明 {profile.name} 的价值",
            "梳理销售对话中的产品表达",
            "在首轮沟通中明确目标客户和场景",
        ]
    )
    pain_points = profile.pain_points_solved or _compact(
        [
            "产品价值表达不清，影响首轮销售转化",
            "难以快速判断优先行业和目标客户",
            "销售材料缺少可直接复用的结构化表达",
        ]
    )
    advantages = profile.core_advantages or _compact(
        [
            f"{profile.name} 能先帮助团队讲清产品",
            "把分散信息收口成结构化销售输入",
            "为后续获客分析和报告生成提供统一基线",
        ]
    )
    constraints = profile.constraints or _compact(
        [
            "当前仍是 V1 最小闭环，暂不覆盖 CRM 和自动触达",
            "当前输出基于已有产品描述，仍需人工确认",
        ]
    )

    confidence = 40
    if profile.source_notes:
        confidence += 20
    if profile.target_customers:
        confidence += 10
    if profile.typical_use_cases:
        confidence += 10
    if profile.pain_points_solved:
        confidence += 10

    return {
        "normalized_context": {
            "target_customers": target_customers,
            "target_industries": target_industries or ["企业服务"],
            "typical_use_cases": use_cases,
            "pain_points_solved": pain_points,
            "core_advantages": advantages,
            "constraints": constraints,
            "delivery_model": profile.delivery_model or DEFAULT_DELIVERY_MODEL,
            "confidence_score": min(confidence, 85),
        }
    }


def generate_product_learning_draft(
    state: ProductLearningGraphState,
) -> ProductLearningGraphState:
    context = state["normalized_context"]
    draft = ProductLearningDraft(
        target_customers=context["target_customers"],
        target_industries=context["target_industries"],
        typical_use_cases=context["typical_use_cases"],
        pain_points_solved=context["pain_points_solved"],
        core_advantages=context["core_advantages"],
        delivery_model=context["delivery_model"],
        constraints=context["constraints"],
        missing_fields=[],
        confidence_score=context["confidence_score"],
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
