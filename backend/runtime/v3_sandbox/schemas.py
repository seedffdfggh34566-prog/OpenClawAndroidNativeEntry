from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


MemoryStatus = Literal["observed", "inferred", "hypothesis", "confirmed", "rejected", "superseded"]
AgentActionType = Literal[
    "write_memory",
    "update_memory_status",
    "update_working_state",
    "update_customer_intelligence",
    "no_op",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class V3SandboxModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MemoryItem(V3SandboxModel):
    id: str
    status: MemoryStatus
    content: str = Field(min_length=1)
    source: str = Field(default="agent")
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)
    supersedes: list[str] = Field(default_factory=list)
    superseded_by: str | None = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("evidence", "supersedes", "tags")
    @classmethod
    def _compact_strings(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in value:
            text = item.strip()
            if not text or text in seen:
                continue
            seen.add(text)
            result.append(text)
        return result


class SandboxWorkingState(V3SandboxModel):
    product_understanding: list[str] = Field(default_factory=list)
    sales_strategy: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    current_hypotheses: list[str] = Field(default_factory=list)
    correction_summary: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=utc_now)


class CustomerCandidateDraft(V3SandboxModel):
    id: str
    name: str = Field(min_length=1)
    segment: str = ""
    target_roles: list[str] = Field(default_factory=list)
    ranking_reason: str = ""
    score: int = Field(default=0, ge=0, le=100)
    validation_signals: list[str] = Field(default_factory=list)


class CustomerIntelligenceDraft(V3SandboxModel):
    target_industries: list[str] = Field(default_factory=list)
    target_roles: list[str] = Field(default_factory=list)
    candidates: list[CustomerCandidateDraft] = Field(default_factory=list)
    ranking_reasons: list[str] = Field(default_factory=list)
    scoring_draft: dict[str, int] = Field(default_factory=dict)
    validation_signals: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=utc_now)


class AgentAction(V3SandboxModel):
    type: AgentActionType
    payload: dict[str, Any] = Field(default_factory=dict)


class V3SandboxMessage(V3SandboxModel):
    id: str
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=utc_now)


class V3SandboxTraceEvent(V3SandboxModel):
    id: str
    session_id: str
    turn_id: str
    event_type: str
    runtime_metadata: dict[str, Any] = Field(default_factory=dict)
    actions: list[AgentAction] = Field(default_factory=list)
    parsed_output: dict[str, Any] | None = None
    error: dict[str, str] | None = None
    created_at: datetime = Field(default_factory=utc_now)


class V3SandboxSession(V3SandboxModel):
    id: str
    title: str = "V3 Sandbox Session"
    memory_items: dict[str, MemoryItem] = Field(default_factory=dict)
    working_state: SandboxWorkingState = Field(default_factory=SandboxWorkingState)
    customer_intelligence: CustomerIntelligenceDraft = Field(default_factory=CustomerIntelligenceDraft)
    messages: list[V3SandboxMessage] = Field(default_factory=list)
    trace: list[V3SandboxTraceEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class V3SandboxTurnOutput(V3SandboxModel):
    assistant_message: str = Field(min_length=1)
    actions: list[AgentAction] = Field(default_factory=list)
    reasoning_summary: str = ""
    confidence: float = Field(default=0.5, ge=0, le=1)


class V3SandboxTurnResult(V3SandboxModel):
    session: V3SandboxSession
    assistant_message: V3SandboxMessage
    actions: list[AgentAction]
    trace_event: V3SandboxTraceEvent
