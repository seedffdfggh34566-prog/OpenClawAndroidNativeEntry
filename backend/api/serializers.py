from __future__ import annotations

from backend.api import models, schemas
from backend.api.product_learning import derive_learning_stage


def to_object_ref(payload: dict[str, object]) -> schemas.ObjectRef:
    return schemas.ObjectRef.model_validate(payload)


def product_profile_summary(model: models.ProductProfile) -> schemas.ProductProfileSummary:
    return schemas.ProductProfileSummary(
        id=model.id,
        name=model.name,
        one_line_description=model.one_line_description,
        status=model.status,
        learning_stage=derive_learning_stage(model),
        version=model.version,
        updated_at=model.updated_at,
    )


def product_profile_detail(model: models.ProductProfile) -> schemas.ProductProfileDetail:
    return schemas.ProductProfileDetail(
        id=model.id,
        name=model.name,
        one_line_description=model.one_line_description,
        status=model.status,
        learning_stage=derive_learning_stage(model),
        version=model.version,
        target_customers=model.target_customers,
        target_industries=model.target_industries,
        typical_use_cases=model.typical_use_cases,
        pain_points_solved=model.pain_points_solved,
        core_advantages=model.core_advantages,
        delivery_model=model.delivery_model,
        constraints=model.constraints,
        missing_fields=model.missing_fields,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def agent_run_payload(model: models.AgentRun) -> schemas.AgentRunPayload:
    return schemas.AgentRunPayload(
        id=model.id,
        run_type=model.run_type,
        status=model.status,
        triggered_by=model.triggered_by,
        trigger_source=model.trigger_source,
        input_refs=[to_object_ref(item) for item in model.input_refs],
        output_refs=[to_object_ref(item) for item in model.output_refs],
        started_at=model.started_at,
        ended_at=model.ended_at,
        error_message=model.error_message,
        runtime_metadata=dict(model.runtime_metadata or {}),
    )


def report_payload(model: models.AnalysisReport) -> schemas.ReportPayload:
    return schemas.ReportPayload(
        id=model.id,
        product_profile_id=model.product_profile_id,
        lead_analysis_result_id=model.lead_analysis_result_id,
        status=model.status,
        title=model.title,
        summary=model.summary,
        sections=[schemas.Section.model_validate(item) for item in model.sections],
        version=model.version,
        updated_at=model.updated_at,
    )


def latest_analysis_result_summary(
    model: models.LeadAnalysisResult,
) -> schemas.LatestAnalysisResultSummary:
    return schemas.LatestAnalysisResultSummary(
        id=model.id,
        status=model.status,
        title=model.title,
        updated_at=model.updated_at,
    )


def lead_analysis_result_detail(
    model: models.LeadAnalysisResult,
) -> schemas.LeadAnalysisResultDetail:
    return schemas.LeadAnalysisResultDetail(
        id=model.id,
        product_profile_id=model.product_profile_id,
        created_by_agent_run_id=model.created_by_agent_run_id,
        title=model.title,
        analysis_scope=model.analysis_scope,
        summary=model.summary,
        priority_industries=model.priority_industries,
        priority_customer_types=model.priority_customer_types,
        scenario_opportunities=model.scenario_opportunities,
        ranking_explanations=model.ranking_explanations,
        recommendations=model.recommendations,
        risks=model.risks,
        limitations=model.limitations,
        status=model.status,
        version=model.version,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def latest_report_summary(model: models.AnalysisReport) -> schemas.LatestReportSummary:
    return schemas.LatestReportSummary(
        id=model.id,
        status=model.status,
        title=model.title,
        updated_at=model.updated_at,
    )
