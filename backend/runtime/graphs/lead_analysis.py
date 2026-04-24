from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from backend.runtime.types import (
    LeadAnalysisDraft,
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
    profile = state["product_profile_payload"]
    context = state["normalized_context"]
    industries = context["industries"]
    customer_types = context["customer_types"]
    scenarios = context["scenarios"]
    primary_advantage = context["primary_advantage"]
    primary_pain = context["primary_pain"]
    missing_fields = context["missing_fields"]
    constraints = context["constraints"]

    ranking_explanations = _compact(
        [
            f"优先从 {industries[0]} 切入，因为它更容易直接验证“{primary_pain}”这一购买动因。",
            f"优先面对 {customer_types[0]}，因为该角色更容易感知“{primary_advantage}”带来的价值。",
            "Phase 1 已切到 LangGraph 编排，后续可继续接入外部搜索与更丰富证据。",
        ]
    )
    recommendations = _compact(
        [
            f"先围绕 {industries[0]} + {customer_types[0]} 组合验证第一轮销售表达。",
            f"把场景说明收口到“{scenarios[0]}”，避免首轮叙事过宽。",
            f"继续补齐缺失信息：{', '.join(missing_fields)}。" if missing_fields else "继续积累更多真实客户反馈，验证优先方向。",
        ]
    )
    risks = _compact(
        constraints[:2]
        + (
            [f"当前仍缺少 {', '.join(missing_fields)}，会影响行业和客户优先级判断。"] if missing_fields else []
        )
    )
    limitations = _compact(
        [
            "当前 Phase 1 以 LangGraph direct runtime 替换 stub，尚未引入外部检索和长期记忆。",
            "分析结果仍依赖现有 ProductProfile 的完整度和当前已知上下文。",
        ]
    )

    draft = LeadAnalysisDraft(
        title=f"{profile.name} 获客分析结果",
        analysis_scope="v1_langgraph_phase1",
        summary=(
            f"基于 {profile.name} 的当前画像，优先建议从 {industries[0]} 的 "
            f"{customer_types[0]} 入手，围绕“{primary_pain}”组织第一轮销售表达。"
        ),
        priority_industries=industries,
        priority_customer_types=customer_types,
        scenario_opportunities=scenarios,
        ranking_explanations=ranking_explanations,
        recommendations=recommendations,
        risks=risks,
        limitations=limitations,
    )
    return {"draft_output": draft}


def validate_lead_analysis_draft(
    state: LeadAnalysisGraphState,
) -> LeadAnalysisGraphState:
    draft = LeadAnalysisDraft.model_validate(state["draft_output"])
    return {"draft_output": draft}


def return_draft_payload(
    state: LeadAnalysisGraphState,
) -> LeadAnalysisGraphState:
    return {"draft_output": state["draft_output"]}


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
) -> LeadAnalysisDraft:
    state = LEAD_ANALYSIS_GRAPH.invoke(
        {
            "run_id": run_id,
            "run_type": "lead_analysis",
            "product_profile_id": product_profile_payload.id,
            "product_profile_payload": product_profile_payload,
        }
    )
    return LeadAnalysisDraft.model_validate(state["draft_output"])
