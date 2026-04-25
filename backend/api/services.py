from __future__ import annotations

from dataclasses import dataclass
from datetime import timezone
import logging
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.api import models, schemas, serializers
from backend.api.config import get_settings
from backend.api.database import get_session_factory
from backend.api.product_learning import (
    DEFAULT_DELIVERY_MODEL,
    canonical_missing_fields,
    derive_learning_stage,
)
from backend.runtime.adapter import RuntimeProvider, get_runtime_provider

logger = logging.getLogger(__name__)


DEFAULT_RUNTIME_PROVIDER = get_runtime_provider()


@dataclass
class ProductProfileCreationResult:
    product_profile: models.ProductProfile
    current_run: models.AgentRun


def generate_prefixed_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


def _build_runtime_metadata(run_type: str, *, round_index: int = 0) -> dict[str, object]:
    return DEFAULT_RUNTIME_PROVIDER.runtime_metadata(run_type, round_index=round_index)


def _merge_runtime_metadata(
    agent_run: models.AgentRun,
    runtime_metadata: dict[str, object],
) -> None:
    if not runtime_metadata:
        return
    merged = dict(agent_run.runtime_metadata or {})
    merged.update(runtime_metadata)
    agent_run.runtime_metadata = merged


def _product_learning_round_index(
    session: Session,
    product_profile_id: str,
) -> int:
    product_learning_runs = session.scalars(
        select(models.AgentRun).where(models.AgentRun.run_type == "product_learning")
    ).all()
    return sum(
        1
        for run in product_learning_runs
        if any(
            ref.get("object_type") == "product_profile"
            and ref.get("object_id") == product_profile_id
            for ref in run.input_refs
        )
    )


def _create_product_learning_agent_run(
    session: Session,
    product_profile: models.ProductProfile,
    *,
    trigger_source: str,
    round_index: int,
) -> models.AgentRun:
    agent_run = models.AgentRun(
        id=generate_prefixed_id("run"),
        run_type="product_learning",
        triggered_by="user",
        trigger_source=trigger_source,
        input_refs=[
            {
                "object_type": "product_profile",
                "object_id": product_profile.id,
                "version": product_profile.version,
            }
        ],
        output_refs=[],
        status="queued",
        runtime_provider=DEFAULT_RUNTIME_PROVIDER.provider_name,
        runtime_metadata=_build_runtime_metadata("product_learning", round_index=round_index),
    )
    session.add(agent_run)
    return agent_run


def create_product_profile(
    session: Session,
    payload: schemas.ProductProfileCreateRequest,
) -> ProductProfileCreationResult:
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
        delivery_model=DEFAULT_DELIVERY_MODEL,
        constraints=[],
        missing_fields=[],
        confidence_score=20,
        status="draft",
        version=1,
    )
    session.add(profile)
    session.flush()

    profile.missing_fields = canonical_missing_fields(profile)

    agent_run = _create_product_learning_agent_run(
        session,
        profile,
        trigger_source="android_product_learning",
        round_index=0,
    )
    session.commit()
    session.refresh(profile)
    session.refresh(agent_run)
    logger.info(
        "product_profile.created",
        extra={
            "event": "product_profile.created",
            "product_profile_id": profile.id,
            "status": profile.status,
            "learning_stage": derive_learning_stage(profile),
            "current_run_id": agent_run.id,
        },
    )
    return ProductProfileCreationResult(product_profile=profile, current_run=agent_run)


def enrich_product_profile(
    session: Session,
    product_profile_id: str,
    payload: schemas.ProductProfileEnrichRequest,
) -> models.AgentRun:
    product_profile = get_product_profile_or_404(session, product_profile_id)
    if product_profile.status != "draft":
        raise HTTPException(status_code=409, detail="product_profile_enrich_requires_draft")

    existing_notes = (product_profile.source_notes or "").strip()
    supplemental_notes = payload.supplemental_notes.strip()
    product_profile.source_notes = (
        f"{existing_notes}\n{supplemental_notes}" if existing_notes else supplemental_notes
    )

    round_index = _product_learning_round_index(session, product_profile.id)
    agent_run = _create_product_learning_agent_run(
        session,
        product_profile,
        trigger_source=payload.trigger_source,
        round_index=round_index,
    )
    session.commit()
    session.refresh(agent_run)
    logger.info(
        "product_profile.enrich_queued",
        extra={
            "event": "product_profile.enrich_queued",
            "product_profile_id": product_profile.id,
            "agent_run_id": agent_run.id,
            "round_index": round_index,
        },
    )
    return agent_run


def get_product_profile_or_404(session: Session, product_profile_id: str) -> models.ProductProfile:
    product_profile = session.get(models.ProductProfile, product_profile_id)
    if product_profile is None:
        raise HTTPException(status_code=404, detail="product_profile_not_found")
    return product_profile


def confirm_product_profile(session: Session, product_profile_id: str) -> models.ProductProfile:
    product_profile = get_product_profile_or_404(session, product_profile_id)
    if product_profile.status == "draft":
        if derive_learning_stage(product_profile) != "ready_for_confirmation":
            raise HTTPException(
                status_code=409,
                detail="product_profile_not_ready_for_confirmation",
            )
        product_profile.status = "confirmed"
        product_profile.version += 1
        product_profile.missing_fields = canonical_missing_fields(product_profile)
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
        runtime_metadata=_build_runtime_metadata(payload.run_type, round_index=0),
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
        existing_metadata = dict(agent_run.runtime_metadata or {})
        agent_run.runtime_metadata = runtime_provider.runtime_metadata(
            agent_run.run_type,
            round_index=int(existing_metadata.get("round_index", 0)),
            trace_id=existing_metadata.get("trace_id"),
        )
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
        elif agent_run.run_type == "product_learning":
            _process_product_learning(session, agent_run, runtime_provider)
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

    draft_result = runtime_provider.generate_lead_analysis_draft(
        product_profile,
        run_id=agent_run.id,
    )
    draft = draft_result.draft
    _merge_runtime_metadata(agent_run, draft_result.runtime_metadata)
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


def _prefer_existing_list(existing: list[str], generated: list[str]) -> list[str]:
    return existing if existing else generated


def _prefer_existing_value(existing: str | None, generated: str | None) -> str | None:
    if existing and existing.strip() and existing != DEFAULT_DELIVERY_MODEL:
        return existing
    if existing == DEFAULT_DELIVERY_MODEL and not generated:
        return existing
    return generated or existing


def _process_product_learning(
    session: Session,
    agent_run: models.AgentRun,
    runtime_provider: RuntimeProvider,
) -> None:
    profile_ref = next(
        ref for ref in agent_run.input_refs if ref["object_type"] == "product_profile"
    )
    product_profile = get_product_profile_or_404(session, str(profile_ref["object_id"]))

    draft_result = runtime_provider.generate_product_learning_draft(
        product_profile,
        run_id=agent_run.id,
    )
    draft = draft_result.draft
    _merge_runtime_metadata(agent_run, draft_result.runtime_metadata)
    product_profile.target_customers = _prefer_existing_list(
        product_profile.target_customers,
        draft.target_customers,
    )
    product_profile.target_industries = _prefer_existing_list(
        product_profile.target_industries,
        draft.target_industries,
    )
    product_profile.typical_use_cases = _prefer_existing_list(
        product_profile.typical_use_cases,
        draft.typical_use_cases,
    )
    product_profile.pain_points_solved = _prefer_existing_list(
        product_profile.pain_points_solved,
        draft.pain_points_solved,
    )
    product_profile.core_advantages = _prefer_existing_list(
        product_profile.core_advantages,
        draft.core_advantages,
    )
    product_profile.constraints = _prefer_existing_list(
        product_profile.constraints,
        draft.constraints,
    )
    product_profile.delivery_model = (
        _prefer_existing_value(product_profile.delivery_model, draft.delivery_model)
        or DEFAULT_DELIVERY_MODEL
    )
    product_profile.confidence_score = max(0, min(draft.confidence_score, 100))
    product_profile.missing_fields = canonical_missing_fields(product_profile)
    product_profile.version += 1
    session.flush()
    agent_run.output_refs = [
        {
            "object_type": "product_profile",
            "object_id": product_profile.id,
            "version": product_profile.version,
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

    if object_type == "product_profile":
        product_profile = get_product_profile_or_404(session, object_id)
        return {
            "product_profile_id": product_profile.id,
            "learning_stage": derive_learning_stage(product_profile),
            "status": product_profile.status,
            "updated_at": product_profile.updated_at.astimezone(timezone.utc),
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
            serializers.product_profile_summary(latest_product_profile)
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
