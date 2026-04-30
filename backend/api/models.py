from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )


class ProductProfile(Base, TimestampMixin):
    __tablename__ = "product_profiles"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    one_line_description: Mapped[str] = mapped_column(String(500))
    source_notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_customers: Mapped[list[str]] = mapped_column(JSON, default=list)
    target_industries: Mapped[list[str]] = mapped_column(JSON, default=list)
    typical_use_cases: Mapped[list[str]] = mapped_column(JSON, default=list)
    pain_points_solved: Mapped[list[str]] = mapped_column(JSON, default=list)
    core_advantages: Mapped[list[str]] = mapped_column(JSON, default=list)
    delivery_model: Mapped[str] = mapped_column(String(255), default="mobile_control_entry + local_backend")
    constraints: Mapped[list[str]] = mapped_column(JSON, default=list)
    missing_fields: Mapped[list[str]] = mapped_column(JSON, default=list)
    confidence_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    version: Mapped[int] = mapped_column(Integer, default=1)


class LeadAnalysisResult(Base, TimestampMixin):
    __tablename__ = "lead_analysis_results"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    product_profile_id: Mapped[str] = mapped_column(String(32), index=True)
    created_by_agent_run_id: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(255))
    analysis_scope: Mapped[str] = mapped_column(String(255), default="v1_stub")
    summary: Mapped[str] = mapped_column(Text())
    priority_industries: Mapped[list[str]] = mapped_column(JSON, default=list)
    priority_customer_types: Mapped[list[str]] = mapped_column(JSON, default=list)
    scenario_opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    ranking_explanations: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommendations: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    limitations: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    version: Mapped[int] = mapped_column(Integer, default=1)


class AnalysisReport(Base, TimestampMixin):
    __tablename__ = "analysis_reports"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    product_profile_id: Mapped[str] = mapped_column(String(32), index=True)
    lead_analysis_result_id: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text())
    sections: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)
    body_markdown: Mapped[str | None] = mapped_column(Text(), nullable=True)
    export_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    export_refs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    version: Mapped[int] = mapped_column(Integer, default=1)


class AgentRun(Base, TimestampMixin):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    run_type: Mapped[str] = mapped_column(String(64), index=True)
    triggered_by: Mapped[str] = mapped_column(String(64), default="user")
    trigger_source: Mapped[str] = mapped_column(String(64))
    input_refs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    output_refs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="queued")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text(), nullable=True)
    runtime_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    runtime_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class V3SandboxSessionRecord(Base):
    __tablename__ = "v3_sandbox_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(Text())
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class V3SandboxMessageRecord(Base):
    __tablename__ = "v3_sandbox_messages"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    message_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    role: Mapped[str] = mapped_column(String(32), index=True)
    content: Mapped[str] = mapped_column(Text())
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class V3SandboxTraceEventRecord(Base):
    __tablename__ = "v3_sandbox_trace_events"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    trace_event_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    turn_id: Mapped[str] = mapped_column(String(96), index=True)
    event_type: Mapped[str] = mapped_column(String(96), index=True)
    runtime_metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    parsed_output_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class V3SandboxActionEventRecord(Base):
    __tablename__ = "v3_sandbox_action_events"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    trace_event_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    action_index: Mapped[int] = mapped_column(Integer, primary_key=True)
    turn_id: Mapped[str] = mapped_column(String(96), index=True)
    action_type: Mapped[str] = mapped_column(String(64), index=True)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class V3SandboxMemoryItemRecord(Base):
    __tablename__ = "v3_sandbox_memory_items"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    memory_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    source: Mapped[str] = mapped_column(String(64), index=True)
    content: Mapped[str] = mapped_column(Text())
    confidence: Mapped[float] = mapped_column(Float())
    superseded_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tags_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    evidence_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class V3SandboxMemoryTransitionEventRecord(Base):
    __tablename__ = "v3_sandbox_memory_transition_events"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    transition_event_id: Mapped[str] = mapped_column(String(192), primary_key=True)
    trace_event_id: Mapped[str | None] = mapped_column(String(96), nullable=True, index=True)
    turn_id: Mapped[str | None] = mapped_column(String(96), nullable=True, index=True)
    action_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    transition_type: Mapped[str] = mapped_column(String(64), index=True)
    memory_id: Mapped[str] = mapped_column(String(128), index=True)
    before_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    after_status: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    superseded_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class V3SandboxCoreMemoryBlockTransitionEventRecord(Base):
    __tablename__ = "v3_sandbox_core_memory_block_transition_events"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    transition_event_id: Mapped[str] = mapped_column(String(192), primary_key=True)
    trace_event_id: Mapped[str | None] = mapped_column(String(96), nullable=True, index=True)
    turn_id: Mapped[str | None] = mapped_column(String(96), nullable=True, index=True)
    tool_event_id: Mapped[str | None] = mapped_column(String(96), nullable=True, index=True)
    tool_call_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tool_name: Mapped[str] = mapped_column(String(64), index=True)
    block_label: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    before_value: Mapped[str | None] = mapped_column(Text(), nullable=True)
    after_value: Mapped[str | None] = mapped_column(Text(), nullable=True)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
