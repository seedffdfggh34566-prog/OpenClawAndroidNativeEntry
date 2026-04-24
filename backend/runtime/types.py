from __future__ import annotations

from typing import Any, TypedDict

from pydantic import BaseModel, Field

from backend.api import models


class ProductProfileRuntimePayload(BaseModel):
    id: str
    name: str
    one_line_description: str
    source_notes: str | None = None
    target_customers: list[str] = Field(default_factory=list)
    target_industries: list[str] = Field(default_factory=list)
    typical_use_cases: list[str] = Field(default_factory=list)
    pain_points_solved: list[str] = Field(default_factory=list)
    core_advantages: list[str] = Field(default_factory=list)
    delivery_model: str
    constraints: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    status: str
    version: int

    @classmethod
    def from_model(cls, profile: models.ProductProfile) -> "ProductProfileRuntimePayload":
        return cls(
            id=profile.id,
            name=profile.name,
            one_line_description=profile.one_line_description,
            source_notes=profile.source_notes,
            target_customers=profile.target_customers,
            target_industries=profile.target_industries,
            typical_use_cases=profile.typical_use_cases,
            pain_points_solved=profile.pain_points_solved,
            core_advantages=profile.core_advantages,
            delivery_model=profile.delivery_model,
            constraints=profile.constraints,
            missing_fields=profile.missing_fields,
            status=profile.status,
            version=profile.version,
        )


class LeadAnalysisResultRuntimePayload(BaseModel):
    id: str
    product_profile_id: str
    title: str
    analysis_scope: str
    summary: str
    priority_industries: list[str] = Field(default_factory=list)
    priority_customer_types: list[str] = Field(default_factory=list)
    scenario_opportunities: list[str] = Field(default_factory=list)
    ranking_explanations: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    status: str
    version: int

    @classmethod
    def from_model(
        cls,
        analysis_result: models.LeadAnalysisResult,
    ) -> "LeadAnalysisResultRuntimePayload":
        return cls(
            id=analysis_result.id,
            product_profile_id=analysis_result.product_profile_id,
            title=analysis_result.title,
            analysis_scope=analysis_result.analysis_scope,
            summary=analysis_result.summary,
            priority_industries=analysis_result.priority_industries,
            priority_customer_types=analysis_result.priority_customer_types,
            scenario_opportunities=analysis_result.scenario_opportunities,
            ranking_explanations=analysis_result.ranking_explanations,
            recommendations=analysis_result.recommendations,
            risks=analysis_result.risks,
            limitations=analysis_result.limitations,
            status=analysis_result.status,
            version=analysis_result.version,
        )


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


class LeadAnalysisGraphState(TypedDict, total=False):
    run_id: str
    run_type: str
    product_profile_id: str
    product_profile_payload: ProductProfileRuntimePayload
    normalized_context: dict[str, Any]
    draft_output: LeadAnalysisDraft
    error: str | None
    runtime_metadata: dict[str, Any]


class ReportGenerationGraphState(TypedDict, total=False):
    run_id: str
    run_type: str
    product_profile_id: str
    product_profile_payload: ProductProfileRuntimePayload
    lead_analysis_result_id: str
    lead_analysis_result_payload: LeadAnalysisResultRuntimePayload
    normalized_context: dict[str, Any]
    draft_output: AnalysisReportDraft
    error: str | None
    runtime_metadata: dict[str, Any]
