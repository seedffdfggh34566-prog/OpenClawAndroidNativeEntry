from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


ObjectType = Literal["product_profile", "lead_analysis_result", "analysis_report"]
RunType = Literal["lead_analysis", "report_generation"]


class ObjectRef(BaseModel):
    object_type: ObjectType
    object_id: str
    version: int | None = None


class Section(BaseModel):
    title: str
    body: str


class ProductProfileCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    one_line_description: str = Field(min_length=1)
    source_notes: str | None = None


class ProductProfileSummary(BaseModel):
    id: str
    name: str
    one_line_description: str
    status: str
    version: int
    updated_at: datetime


class ProductProfileDetail(BaseModel):
    id: str
    name: str
    one_line_description: str
    status: str
    version: int
    target_customers: list[str]
    target_industries: list[str]
    typical_use_cases: list[str]
    pain_points_solved: list[str]
    core_advantages: list[str]
    delivery_model: str
    constraints: list[str]
    missing_fields: list[str]
    created_at: datetime
    updated_at: datetime


class ProductProfileCreateResponse(BaseModel):
    product_profile: ProductProfileSummary
    current_run: None = None
    links: dict[str, str]


class ProductProfileDetailResponse(BaseModel):
    product_profile: ProductProfileDetail


class ProductProfileConfirmResponse(BaseModel):
    product_profile: ProductProfileSummary


class AnalysisRunCreateRequest(BaseModel):
    run_type: RunType
    product_profile_id: str
    lead_analysis_result_id: str | None = None
    trigger_source: str

    @model_validator(mode="after")
    def validate_report_generation_input(self) -> "AnalysisRunCreateRequest":
        if self.run_type == "report_generation" and not self.lead_analysis_result_id:
            raise ValueError("lead_analysis_result_id is required for report_generation")
        return self


class AgentRunPayload(BaseModel):
    id: str
    run_type: str
    status: str
    triggered_by: str
    trigger_source: str
    input_refs: list[ObjectRef]
    output_refs: list[ObjectRef]
    started_at: datetime | None
    ended_at: datetime | None
    error_message: str | None


class AnalysisRunCreateResponse(BaseModel):
    agent_run: AgentRunPayload


class AnalysisRunDetailResponse(BaseModel):
    agent_run: AgentRunPayload
    result_summary: dict[str, Any] | None


class ReportPayload(BaseModel):
    id: str
    product_profile_id: str
    lead_analysis_result_id: str
    status: str
    title: str
    summary: str
    sections: list[Section]
    version: int
    updated_at: datetime


class ReportDetailResponse(BaseModel):
    report: ReportPayload


class RecentHistoryItem(BaseModel):
    object_type: ObjectType
    id: str
    title: str
    status: str
    updated_at: datetime


class CurrentRunSummary(BaseModel):
    id: str
    run_type: str
    status: str
    trigger_source: str
    started_at: datetime | None
    ended_at: datetime | None
    error_message: str | None


class LatestAnalysisResultSummary(BaseModel):
    id: str
    status: str
    title: str
    updated_at: datetime


class LatestReportSummary(BaseModel):
    id: str
    status: str
    title: str
    updated_at: datetime


class LeadAnalysisResultDetail(BaseModel):
    id: str
    product_profile_id: str
    created_by_agent_run_id: str
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
    status: str
    version: int
    created_at: datetime
    updated_at: datetime


class LeadAnalysisResultDetailResponse(BaseModel):
    lead_analysis_result: LeadAnalysisResultDetail


class HistoryResponse(BaseModel):
    current_run: CurrentRunSummary | None
    latest_product_profile: ProductProfileSummary | None
    latest_analysis_result: LatestAnalysisResultSummary | None
    latest_report: LatestReportSummary | None
    recent_items: list[RecentHistoryItem]
