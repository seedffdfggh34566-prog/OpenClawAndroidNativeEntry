from __future__ import annotations

from datetime import timezone
import logging
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.api import models, schemas
from backend.api.config import get_settings
from backend.api.database import get_session_factory
from backend.runtime.adapter import RuntimeProvider, get_runtime_provider

logger = logging.getLogger(__name__)


DEFAULT_RUNTIME_PROVIDER = get_runtime_provider()


def generate_prefixed_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


def create_product_profile(
    session: Session,
    payload: schemas.ProductProfileCreateRequest,
) -> models.ProductProfile:
    profile = models.ProductProfile(
        id=generate_prefixed_id("pp"),
        name=payload.name,
        one_line_description=payload.one_line_description,
        source_notes=payload.source_notes,
        target_customers=[],
        target_industries=[],
        typical_use_cases=[],
        pain_points_solved=[],
        core_advantages=[],
        constraints=["当前仍是 V1 最小闭环"],
        missing_fields=["价格区间", "销售区域"],
        status="draft",
        version=1,
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)
    logger.info(
        "product_profile.created",
        extra={
            "event": "product_profile.created",
            "status": profile.status,
        },
    )
    return profile


def get_product_profile_or_404(session: Session, product_profile_id: str) -> models.ProductProfile:
    product_profile = session.get(models.ProductProfile, product_profile_id)
    if product_profile is None:
        raise HTTPException(status_code=404, detail="product_profile_not_found")
    return product_profile


def confirm_product_profile(session: Session, product_profile_id: str) -> models.ProductProfile:
    product_profile = get_product_profile_or_404(session, product_profile_id)
    if product_profile.status == "draft":
        product_profile.status = "confirmed"
        product_profile.version += 1
        session.commit()
        session.refresh(product_profile)
        logger.info(
            "product_profile.confirmed",
            extra={
                "event": "product_profile.confirmed",
                "product_profile_id": product_profile.id,
                "version": product_profile.version,
            },
        )
    return product_profile


def get_lead_analysis_result_or_404(
    session: Session,
    lead_analysis_result_id: str,
) -> models.LeadAnalysisResult:
    lead_analysis_result = session.get(models.LeadAnalysisResult, lead_analysis_result_id)
    if lead_analysis_result is None:
        raise HTTPException(status_code=404, detail="lead_analysis_result_not_found")
    return lead_analysis_result


def get_report_or_404(session: Session, report_id: str) -> models.AnalysisReport:
    report = session.get(models.AnalysisReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="report_not_found")
    return report


def get_agent_run_or_404(session: Session, run_id: str) -> models.AgentRun:
    agent_run = session.get(models.AgentRun, run_id)
    if agent_run is None:
        raise HTTPException(status_code=404, detail="agent_run_not_found")
    return agent_run


def create_analysis_run(
    session: Session,
    payload: schemas.AnalysisRunCreateRequest,
) -> models.AgentRun:
    product_profile = get_product_profile_or_404(session, payload.product_profile_id)

    input_refs: list[dict[str, object]] = [
        {
            "object_type": "product_profile",
            "object_id": product_profile.id,
            "version": product_profile.version,
        }
    ]

    if payload.run_type == "lead_analysis":
        if product_profile.status != "confirmed":
            raise HTTPException(
                status_code=409,
                detail="lead_analysis_requires_confirmed_product_profile",
            )

    if payload.run_type == "report_generation":
        if not payload.lead_analysis_result_id:
            raise HTTPException(status_code=422, detail="lead_analysis_result_id_required")
        lead_analysis_result = get_lead_analysis_result_or_404(
            session,
            payload.lead_analysis_result_id,
        )
        input_refs.append(
            {
                "object_type": "lead_analysis_result",
                "object_id": lead_analysis_result.id,
                "version": lead_analysis_result.version,
            }
        )

    agent_run = models.AgentRun(
        id=generate_prefixed_id("run"),
        run_type=payload.run_type,
        triggered_by="user",
        trigger_source=payload.trigger_source,
        input_refs=input_refs,
        output_refs=[],
        status="queued",
        runtime_provider=DEFAULT_RUNTIME_PROVIDER.provider_name,
        runtime_metadata={
            "provider": DEFAULT_RUNTIME_PROVIDER.provider_name,
            "mode": "backend_direct_langgraph",
            "phase": "phase1",
            "status": "queued",
        },
    )
    session.add(agent_run)
    session.commit()
    session.refresh(agent_run)
    logger.info(
        "analysis_run.created",
        extra={
            "event": "analysis_run.created",
            "agent_run_id": agent_run.id,
            "run_type": agent_run.run_type,
            "status": agent_run.status,
            "runtime_provider": agent_run.runtime_provider,
        },
    )
    return agent_run


def process_agent_run(run_id: str) -> None:
    runtime_provider = get_runtime_provider()
    session = get_session_factory()()

    try:
        agent_run = session.get(models.AgentRun, run_id)
        if agent_run is None:
            return

        agent_run.status = "running"
        agent_run.started_at = models.utcnow()
        agent_run.runtime_provider = runtime_provider.provider_name
        agent_run.runtime_metadata = runtime_provider.runtime_metadata(agent_run.run_type)
        session.commit()
        logger.info(
            "analysis_run.started",
            extra={
                "event": "analysis_run.started",
                "agent_run_id": agent_run.id,
                "run_type": agent_run.run_type,
                "status": agent_run.status,
                "runtime_provider": agent_run.runtime_provider,
                "trace_id": agent_run.runtime_metadata.get("trace_id"),
            },
        )

        if agent_run.run_type == "lead_analysis":
            _process_lead_analysis(session, agent_run, runtime_provider)
        elif agent_run.run_type == "report_generation":
            _process_report_generation(session, agent_run, runtime_provider)
        else:
            raise ValueError(f"unsupported_run_type: {agent_run.run_type}")

        agent_run.status = "succeeded"
        agent_run.ended_at = models.utcnow()
        session.commit()
        logger.info(
            "analysis_run.succeeded",
            extra={
                "event": "analysis_run.succeeded",
                "agent_run_id": agent_run.id,
                "run_type": agent_run.run_type,
                "status": agent_run.status,
                "runtime_provider": agent_run.runtime_provider,
                "trace_id": agent_run.runtime_metadata.get("trace_id"),
            },
        )
    except Exception as exc:  # noqa: BLE001
        session.rollback()
        failed_run = session.get(models.AgentRun, run_id)
        if failed_run is not None:
            runtime_metadata = dict(failed_run.runtime_metadata or {})
            runtime_metadata["error_type"] = type(exc).__name__
            failed_run.status = "failed"
            failed_run.error_message = str(exc)
            failed_run.runtime_metadata = runtime_metadata
            if failed_run.started_at is None:
                failed_run.started_at = models.utcnow()
            failed_run.ended_at = models.utcnow()
            session.commit()
            logger.exception(
                "analysis_run.failed",
                extra={
                    "event": "analysis_run.failed",
                    "agent_run_id": failed_run.id,
                    "run_type": failed_run.run_type,
                    "status": failed_run.status,
                    "runtime_provider": failed_run.runtime_provider,
                    "trace_id": failed_run.runtime_metadata.get("trace_id")
                    if failed_run.runtime_metadata
                    else None,
                    "error": str(exc),
                },
            )
    finally:
        session.close()


def _process_lead_analysis(
    session: Session,
    agent_run: models.AgentRun,
    runtime_provider: RuntimeProvider,
) -> None:
    profile_ref = next(
        ref for ref in agent_run.input_refs if ref["object_type"] == "product_profile"
    )
    product_profile = get_product_profile_or_404(session, str(profile_ref["object_id"]))

    if product_profile.status != "confirmed":
        raise ValueError("lead_analysis_requires_confirmed_product_profile")

    draft = runtime_provider.generate_lead_analysis_draft(
        product_profile,
        run_id=agent_run.id,
    )
    analysis_result = models.LeadAnalysisResult(
        id=generate_prefixed_id("lar"),
        product_profile_id=product_profile.id,
        created_by_agent_run_id=agent_run.id,
        title=draft.title,
        analysis_scope=draft.analysis_scope,
        summary=draft.summary,
        priority_industries=draft.priority_industries,
        priority_customer_types=draft.priority_customer_types,
        scenario_opportunities=draft.scenario_opportunities,
        ranking_explanations=draft.ranking_explanations,
        recommendations=draft.recommendations,
        risks=draft.risks,
        limitations=draft.limitations,
        status="published",
        version=1,
    )
    session.add(analysis_result)
    session.flush()
    agent_run.output_refs = [
        {
            "object_type": "lead_analysis_result",
            "object_id": analysis_result.id,
            "version": analysis_result.version,
        }
    ]


def _process_report_generation(
    session: Session,
    agent_run: models.AgentRun,
    runtime_provider: RuntimeProvider,
) -> None:
    profile_ref = next(
        ref for ref in agent_run.input_refs if ref["object_type"] == "product_profile"
    )
    analysis_ref = next(
        ref for ref in agent_run.input_refs if ref["object_type"] == "lead_analysis_result"
    )

    product_profile = get_product_profile_or_404(session, str(profile_ref["object_id"]))
    analysis_result = get_lead_analysis_result_or_404(session, str(analysis_ref["object_id"]))

    draft = runtime_provider.generate_report_draft(
        product_profile,
        analysis_result,
        run_id=agent_run.id,
    )
    report = models.AnalysisReport(
        id=generate_prefixed_id("rep"),
        product_profile_id=product_profile.id,
        lead_analysis_result_id=analysis_result.id,
        title=draft.title,
        summary=draft.summary,
        sections=draft.sections,
        body_markdown="\n\n".join(
            f"## {section['title']}\n{section['body']}" for section in draft.sections
        ),
        export_status=None,
        export_refs=[],
        status="published",
        version=1,
    )
    session.add(report)
    session.flush()
    agent_run.output_refs = [
        {
            "object_type": "analysis_report",
            "object_id": report.id,
            "version": report.version,
        }
    ]


def build_result_summary(session: Session, agent_run: models.AgentRun) -> dict[str, object] | None:
    if agent_run.status != "succeeded" or not agent_run.output_refs:
        return None

    output_ref = agent_run.output_refs[0]
    object_type = output_ref["object_type"]
    object_id = str(output_ref["object_id"])

    if object_type == "lead_analysis_result":
        result = get_lead_analysis_result_or_404(session, object_id)
        return {
            "lead_analysis_result_id": result.id,
            "status": result.status,
            "updated_at": result.updated_at.astimezone(timezone.utc),
        }

    if object_type == "analysis_report":
        report = get_report_or_404(session, object_id)
        return {
            "report_id": report.id,
            "status": report.status,
            "updated_at": report.updated_at.astimezone(timezone.utc),
        }

    return None


def build_history(session: Session) -> schemas.HistoryResponse:
    current_run = session.scalar(
        select(models.AgentRun)
        .where(models.AgentRun.status.in_(["queued", "running"]))
        .order_by(models.AgentRun.created_at.desc())
    )
    latest_product_profile = session.scalar(
        select(models.ProductProfile).order_by(models.ProductProfile.updated_at.desc())
    )
    latest_analysis_result = session.scalar(
        select(models.LeadAnalysisResult).order_by(models.LeadAnalysisResult.updated_at.desc())
    )
    latest_report = session.scalar(
        select(models.AnalysisReport).order_by(models.AnalysisReport.updated_at.desc())
    )

    recent_items: list[schemas.RecentHistoryItem] = []
    for profile in session.scalars(select(models.ProductProfile)).all():
        recent_items.append(
            schemas.RecentHistoryItem(
                object_type="product_profile",
                id=profile.id,
                title=profile.name,
                status=profile.status,
                updated_at=profile.updated_at,
            )
        )
    for result in session.scalars(select(models.LeadAnalysisResult)).all():
        recent_items.append(
            schemas.RecentHistoryItem(
                object_type="lead_analysis_result",
                id=result.id,
                title=result.title,
                status=result.status,
                updated_at=result.updated_at,
            )
        )
    for report in session.scalars(select(models.AnalysisReport)).all():
        recent_items.append(
            schemas.RecentHistoryItem(
                object_type="analysis_report",
                id=report.id,
                title=report.title,
                status=report.status,
                updated_at=report.updated_at,
            )
        )

    recent_items.sort(key=lambda item: item.updated_at, reverse=True)
    settings = get_settings()

    return schemas.HistoryResponse(
        current_run=(
            schemas.CurrentRunSummary(
                id=current_run.id,
                run_type=current_run.run_type,
                status=current_run.status,
                trigger_source=current_run.trigger_source,
                started_at=current_run.started_at,
                ended_at=current_run.ended_at,
                error_message=current_run.error_message,
            )
            if current_run
            else None
        ),
        latest_product_profile=(
            schemas.ProductProfileSummary(
                id=latest_product_profile.id,
                name=latest_product_profile.name,
                one_line_description=latest_product_profile.one_line_description,
                status=latest_product_profile.status,
                version=latest_product_profile.version,
                updated_at=latest_product_profile.updated_at,
            )
            if latest_product_profile
            else None
        ),
        latest_analysis_result=(
            schemas.LatestAnalysisResultSummary(
                id=latest_analysis_result.id,
                status=latest_analysis_result.status,
                title=latest_analysis_result.title,
                updated_at=latest_analysis_result.updated_at,
            )
            if latest_analysis_result
            else None
        ),
        latest_report=(
            schemas.LatestReportSummary(
                id=latest_report.id,
                status=latest_report.status,
                title=latest_report.title,
                updated_at=latest_report.updated_at,
            )
            if latest_report
            else None
        ),
        recent_items=recent_items[: settings.recent_items_limit],
    )
