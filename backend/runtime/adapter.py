from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from backend.api import models


class LeadAnalysisDraft(BaseModel):
    title: str
    analysis_scope: str
    summary: str
    priority_industries: list[str]
    priority_customer_types: list[str]
    scenario_opportunities: list[str]
    ranking_explanations: list[str]
    recommendations: list[str]
    risks: list[str]
    limitations: list[str]


class AnalysisReportDraft(BaseModel):
    title: str
    summary: str
    sections: list[dict[str, str]]


class StubRuntimeAdapter:
    provider_name = "stub"

    def generate_lead_analysis_draft(
        self,
        profile: models.ProductProfile,
    ) -> LeadAnalysisDraft:
        return LeadAnalysisDraft(
            title=f"{profile.name} 第一版获客分析结果",
            analysis_scope="v1_stub",
            summary=f"基于 {profile.name} 的最小占位获客分析结果，当前用于验证正式对象写回链路。",
            priority_industries=["企业服务", "教育培训"],
            priority_customer_types=["中小企业老板", "销售负责人"],
            scenario_opportunities=["产品定位梳理", "获客方向澄清"],
            ranking_explanations=[
                "优先选择更容易快速说明产品价值的行业方向。",
                "优先选择决策链更短、试用门槛更低的目标客群。",
            ],
            recommendations=[
                "先验证企业服务方向的需求表达是否足够清晰。",
                "继续补充价格区间与销售区域等缺失信息。",
            ],
            risks=["当前为 stub 结果，尚未接入真实 OpenClaw runtime。"],
            limitations=["分析深度受限于固定模板与本地占位逻辑。"],
        )

    def generate_report_draft(
        self,
        profile: models.ProductProfile,
        analysis_result: models.LeadAnalysisResult,
    ) -> AnalysisReportDraft:
        return AnalysisReportDraft(
            title=f"{profile.name} 获客分析报告",
            summary=f"该报告基于 {profile.name} 的最小分析结果整理，用于验证报告对象与历史聚合链路。",
            sections=[
                {
                    "title": "产品理解摘要",
                    "body": profile.one_line_description,
                },
                {
                    "title": "优先方向",
                    "body": "、".join(analysis_result.priority_industries) or "当前暂无优先方向。",
                },
                {
                    "title": "下一步建议",
                    "body": "；".join(analysis_result.recommendations) or "继续完善产品画像。",
                },
            ],
        )

    def runtime_metadata(self) -> dict[str, Any]:
        return {"adapter": self.provider_name, "mode": "predictable_stub"}
