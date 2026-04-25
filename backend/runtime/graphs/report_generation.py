from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from backend.runtime.types import (
    AnalysisReportDraft,
    LeadAnalysisResultRuntimePayload,
    ProductProfileRuntimePayload,
    ReportGenerationGraphState,
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
            "risks": analysis_result.risks,
            "limitations": analysis_result.limitations,
            "profile_summary": profile.one_line_description,
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
    risks = _compact(context["risks"] + context["limitations"])

    draft = AnalysisReportDraft(
        title=f"{profile.name} 获客分析报告",
        summary=(
            f"当前建议围绕 {context['top_industry']} 的 {context['top_customer']} 推进，"
            f"优先场景是“{context['top_scenario']}”。"
        ),
        sections=[
            {
                "title": "产品理解摘要",
                "body": context["profile_summary"],
            },
            {
                "title": "优先行业与客户",
                "body": (
                    f"优先从 {context['top_industry']} 切入，首先面向 {context['top_customer']} 展开验证。"
                    + (
                        f" 判断依据：{'；'.join(ranking_explanations)}"
                        if ranking_explanations
                        else ""
                    )
                ),
            },
            {
                "title": "关键场景机会",
                "body": "；".join(analysis_result.scenario_opportunities)
                if analysis_result.scenario_opportunities
                else "当前仍需继续补齐场景信息。",
            },
            {
                "title": "下一步建议",
                "body": "；".join(recommendations),
            },
            {
                "title": "风险与限制",
                "body": "；".join(risks) if risks else "当前未发现新的高优先级风险。",
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
