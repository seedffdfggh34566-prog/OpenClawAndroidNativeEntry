from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from backend.runtime.types import (
    AnalysisReportDraft,
    LeadAnalysisResultRuntimePayload,
    ProductProfileRuntimePayload,
    ReportGenerationGraphState,
)

_SPLIT_PUNCTUATION = ("；", ";", "。")


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


def _shorten_text(value: str, *, max_chars: int) -> str:
    text = value.strip()
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 1].rstrip()}…"


def _split_long_point(value: str, *, max_chars: int = 90) -> list[str]:
    text = value.strip()
    should_split = len(text) > max_chars or any(
        punctuation in text for punctuation in ("；", ";")
    )
    if not should_split:
        return [text] if text else []

    pieces = [text]
    for punctuation in _SPLIT_PUNCTUATION:
        next_pieces: list[str] = []
        for piece in pieces:
            next_pieces.extend(part.strip() for part in piece.split(punctuation))
        pieces = next_pieces

    result = [piece for piece in pieces if piece]
    if len(result) <= 1:
        return [_shorten_text(text, max_chars=max_chars)]
    return result


def _readability_points(values: list[str], *, max_chars: int = 90) -> list[str]:
    points: list[str] = []
    for value in _compact(values):
        points.extend(_split_long_point(value, max_chars=max_chars))
    return _compact(points)


def _join_points(values: list[str], *, fallback: str, max_chars: int = 90) -> str:
    compacted = _readability_points(values, max_chars=max_chars)
    if not compacted:
        return fallback
    return "\n".join(f"- {value}" for value in compacted)


def _contains_any(value: str, needles: list[str]) -> bool:
    return any(needle in value for needle in needles)


def load_product_profile_and_analysis_result(
    state: ReportGenerationGraphState,
) -> ReportGenerationGraphState:
    profile = state["product_profile_payload"]
    analysis_result = state["lead_analysis_result_payload"]
    if profile.status != "confirmed":
        raise ValueError("report_generation_requires_confirmed_product_profile")
    return {
        "product_profile_id": profile.id,
        "lead_analysis_result_id": analysis_result.id,
    }


def build_report_context(
    state: ReportGenerationGraphState,
) -> ReportGenerationGraphState:
    profile = state["product_profile_payload"]
    analysis_result = state["lead_analysis_result_payload"]
    top_industry = (
        analysis_result.priority_industries[0]
        if analysis_result.priority_industries
        else "优先行业待补充"
    )
    top_customer = (
        analysis_result.priority_customer_types[0]
        if analysis_result.priority_customer_types
        else "目标客户待补充"
    )
    top_scenario = (
        analysis_result.scenario_opportunities[0]
        if analysis_result.scenario_opportunities
        else "场景待补充"
    )
    return {
        "normalized_context": {
            "top_industry": top_industry,
            "top_customer": top_customer,
            "top_scenario": top_scenario,
            "recommendations": analysis_result.recommendations,
            "ranking_explanations": analysis_result.ranking_explanations,
            "scenario_opportunities": analysis_result.scenario_opportunities,
            "risks": analysis_result.risks,
            "limitations": analysis_result.limitations,
            "profile_summary": profile.one_line_description,
            "target_customers": profile.target_customers,
            "target_industries": profile.target_industries,
            "pain_points": profile.pain_points_solved,
            "advantages": profile.core_advantages,
        }
    }


def generate_report_draft(
    state: ReportGenerationGraphState,
) -> ReportGenerationGraphState:
    profile = state["product_profile_payload"]
    analysis_result = state["lead_analysis_result_payload"]
    context = state["normalized_context"]
    recommendations = _compact(context["recommendations"]) or ["继续补齐缺失画像并验证首轮销售表达。"]
    ranking_explanations = _compact(context["ranking_explanations"])
    scenario_opportunities = _compact(context["scenario_opportunities"])
    neighbor_opportunities = [
        item
        for item in scenario_opportunities
        if _contains_any(item, ["邻近", "上下游"])
    ]
    core_scenarios = [
        item
        for item in scenario_opportunities
        if item not in neighbor_opportunities
    ]
    validation_recommendations = [
        item
        for item in recommendations
        if _contains_any(item, ["首轮销售验证", "访谈", "试用", "验证"])
    ]
    not_priority_recommendations = [
        item for item in recommendations if item.startswith("不建议优先")
    ]
    action_items = [
        item
        for item in recommendations
        if item not in not_priority_recommendations
    ]
    risks = _compact(context["risks"] + context["limitations"])
    product_understanding = _compact(
        [
            context["profile_summary"],
            f"目标客户：{'、'.join(context['target_customers'])}"
            if context["target_customers"]
            else "",
            f"解决痛点：{'、'.join(context['pain_points'])}"
            if context["pain_points"]
            else "",
            f"核心优势：{'、'.join(context['advantages'])}"
            if context["advantages"]
            else "",
        ]
    )

    draft = AnalysisReportDraft(
        title=f"{profile.name} 获客分析报告",
        summary=(
            _shorten_text(
                f"建议优先面向 {context['top_industry']} 的 {context['top_customer']}，"
                f"用“{context['top_scenario']}”验证购买动因、触达难度和销售表达。",
                max_chars=120,
            )
        ),
        sections=[
            {
                "title": "产品理解",
                "body": _join_points(
                    product_understanding,
                    fallback="当前产品理解仍需继续补齐。",
                    max_chars=120,
                ),
            },
            {
                "title": "优先行业与客户",
                "body": _join_points(
                    [
                        f"优先行业：{context['top_industry']}",
                        f"优先客户：{context['top_customer']}",
                    ]
                    + [f"判断依据：{item}" for item in ranking_explanations],
                    fallback="当前仍需继续补齐行业和客户优先级判断。",
                    max_chars=110,
                ),
            },
            {
                "title": "场景机会",
                "body": _join_points(
                    core_scenarios,
                    fallback="当前仍需继续补齐场景信息。",
                    max_chars=90,
                ),
            },
            {
                "title": "上下游与邻近机会",
                "body": _join_points(
                    neighbor_opportunities,
                    fallback="当前暂未识别出明确的上下游或邻近机会。",
                    max_chars=90,
                ),
            },
            {
                "title": "首轮销售验证计划",
                "body": _join_points(
                    validation_recommendations,
                    fallback="先选取 5 到 10 个目标客户访谈，验证痛点强度、决策角色和替代方案。",
                    max_chars=90,
                ),
            },
            {
                "title": "不建议优先方向",
                "body": _join_points(
                    not_priority_recommendations,
                    fallback="暂不建议同时铺开过多行业、客户角色或销售叙事。",
                    max_chars=90,
                ),
            },
            {
                "title": "风险与限制",
                "body": _join_points(
                    risks,
                    fallback="当前未发现新的高优先级风险。",
                    max_chars=90,
                ),
            },
            {
                "title": "下一步行动清单",
                "body": _join_points(
                    action_items,
                    fallback="继续积累真实客户反馈，验证优先方向。",
                    max_chars=90,
                ),
            },
        ],
    )
    return {"draft_output": draft}


def validate_report_draft(
    state: ReportGenerationGraphState,
) -> ReportGenerationGraphState:
    draft = AnalysisReportDraft.model_validate(state["draft_output"])
    if not draft.sections:
        raise ValueError("analysis_report_sections_required")
    return {"draft_output": draft}


def return_draft_payload(
    state: ReportGenerationGraphState,
) -> ReportGenerationGraphState:
    return {"draft_output": state["draft_output"]}


_builder = StateGraph(ReportGenerationGraphState)
_builder.add_node("load_product_profile_and_analysis_result", load_product_profile_and_analysis_result)
_builder.add_node("build_report_context", build_report_context)
_builder.add_node("generate_report_draft", generate_report_draft)
_builder.add_node("validate_report_draft", validate_report_draft)
_builder.add_node("return_draft_payload", return_draft_payload)
_builder.add_edge(START, "load_product_profile_and_analysis_result")
_builder.add_edge("load_product_profile_and_analysis_result", "build_report_context")
_builder.add_edge("build_report_context", "generate_report_draft")
_builder.add_edge("generate_report_draft", "validate_report_draft")
_builder.add_edge("validate_report_draft", "return_draft_payload")
_builder.add_edge("return_draft_payload", END)
REPORT_GENERATION_GRAPH = _builder.compile()


def invoke_report_generation_graph(
    *,
    run_id: str,
    product_profile_payload: ProductProfileRuntimePayload,
    lead_analysis_result_payload: LeadAnalysisResultRuntimePayload,
) -> AnalysisReportDraft:
    state = REPORT_GENERATION_GRAPH.invoke(
        {
            "run_id": run_id,
            "run_type": "report_generation",
            "product_profile_id": product_profile_payload.id,
            "product_profile_payload": product_profile_payload,
            "lead_analysis_result_id": lead_analysis_result_payload.id,
            "lead_analysis_result_payload": lead_analysis_result_payload,
        }
    )
    return AnalysisReportDraft.model_validate(state["draft_output"])
