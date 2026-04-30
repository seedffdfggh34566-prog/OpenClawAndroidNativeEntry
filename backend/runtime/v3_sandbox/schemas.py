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
CoreMemoryBlockLabel = Literal["persona", "human", "product", "sales_strategy", "customer_intelligence"]
CoreMemoryToolName = Literal["core_memory_append", "memory_insert", "memory_replace", "send_message"]
CoreMemoryToolEventStatus = Literal["applied", "error"]


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


class CoreMemoryBlock(V3SandboxModel):
    label: CoreMemoryBlockLabel
    description: str
    limit: int = Field(default=2000, ge=1, le=20000)
    value: str = ""
    read_only: bool = False
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("value")
    @classmethod
    def _value_fits_limit(cls, value: str, info) -> str:
        limit = 2000
        if info.data and isinstance(info.data.get("limit"), int):
            limit = info.data["limit"]
        if len(value) > limit:
            raise ValueError("core_memory_block_value_exceeds_limit")
        return value


def default_core_memory_blocks() -> dict[str, CoreMemoryBlock]:
    return {
        "persona": CoreMemoryBlock(
            label="persona",
            description="Agent identity, behavior preferences, and standing instructions for this sales-agent session.",
            value=(
                "You are OpenClaw V3 Product Sales Agent. Maintain concise, editable core memory, "
                "help the user clarify product positioning and sales strategy, and never claim CRM/outreach actions were executed."
            ),
        ),
        "human": CoreMemoryBlock(
            label="human",
            description="What is known about the user, their preferences, constraints, and corrections in this session.",
            value="",
        ),
        "product": CoreMemoryBlock(
            label="product",
            description="Current understanding of the user's product, market, delivery model, and constraints.",
            value="",
        ),
        "sales_strategy": CoreMemoryBlock(
            label="sales_strategy",
            description="Current sales strategy, positioning, outreach hypotheses, and open sales questions.",
            value="",
        ),
        "customer_intelligence": CoreMemoryBlock(
            label="customer_intelligence",
            description="Draft target customer, buyer role, ranking reason, score, and validation signal memory.",
            value="",
        ),
    }


class CoreMemoryToolEvent(V3SandboxModel):
    id: str
    tool_call_id: str
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    status: CoreMemoryToolEventStatus
    result: dict[str, Any] = Field(default_factory=dict)
    error: dict[str, str] | None = None
    block_label: str | None = None
    before_value: str | None = None
    after_value: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class V3SandboxDebugTraceOptions(V3SandboxModel):
    verbose: bool = False
    include_prompt: bool = False
    include_raw_llm_output: bool = False
    include_repair_attempts: bool = False
    include_node_io: bool = False
    include_state_diff: bool = False
    max_bytes: int = Field(default=80_000, ge=8_000, le=500_000)


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
    tool_events: list[CoreMemoryToolEvent] = Field(default_factory=list)
    parsed_output: dict[str, Any] | None = None
    debug_trace: dict[str, Any] | None = None
    error: dict[str, str] | None = None
    created_at: datetime = Field(default_factory=utc_now)


class V3SandboxSession(V3SandboxModel):
    id: str
    title: str = "V3 Sandbox Session"
    core_memory_blocks: dict[str, CoreMemoryBlock] = Field(default_factory=default_core_memory_blocks)
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


class V3SandboxReplayReport(V3SandboxModel):
    status: Literal["completed", "failed"]
    source_session_id: str
    replay_session_id: str
    replayed_turns: int = 0
    failed_turn_index: int | None = None
    error: dict[str, str] | None = None
