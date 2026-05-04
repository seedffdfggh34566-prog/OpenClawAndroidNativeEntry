from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


CoreMemoryBlockLabel = Literal["persona", "human", "product", "sales_strategy", "customer_intelligence"]
CoreMemoryToolName = Literal["core_memory_append", "memory_insert", "memory_replace", "memory_rethink", "send_message"]
CoreMemoryToolEventStatus = Literal["applied", "error"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class V3SandboxModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CoreMemoryBlock(V3SandboxModel):
    label: CoreMemoryBlockLabel
    description: str
    limit: int = Field(default=2000, ge=1, le=100000)
    value: str = ""
    read_only: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def _value_fits_limit(self) -> "CoreMemoryBlock":
        if len(self.value) > self.limit:
            raise ValueError("core_memory_block_value_exceeds_limit")
        return self


def default_core_memory_blocks() -> dict[str, CoreMemoryBlock]:
    return {
        "persona": CoreMemoryBlock(
            label="persona",
            description="Sales Agent 自身的工作风格、语气与边界。修改要保守，避免与用户冲突。",
            limit=2000,
            value=(
                "You are OpenClaw V3 Product Sales Agent. Maintain concise, editable core memory, "
                "help the user clarify product positioning and sales strategy, and never claim CRM/outreach actions were executed."
            ),
        ),
        "human": CoreMemoryBlock(
            label="human",
            description="当前对话用户的角色、所属公司、关注点、偏好与已知约束。用户主动纠正后必须更新。",
            limit=5000,
            value="",
        ),
        "product": CoreMemoryBlock(
            label="product",
            description=(
                "Agent 对所销售产品的理解：能力、定位、典型用户、限制与常见反对意见。"
                "基于用户输入和 agent 推断同时维护，写明状态（observed / inferred）。"
            ),
            limit=10000,
            value="",
        ),
        "sales_strategy": CoreMemoryBlock(
            label="sales_strategy",
            description="针对当前对话和客户画像的销售策略：当前阶段、下一步动作、需要验证的假设。",
            limit=5000,
            value="",
        ),
        "customer_intelligence": CoreMemoryBlock(
            label="customer_intelligence",
            description=(
                "正在跟进的潜在客户/线索的草稿信息：行业、角色、关键信号、排序理由。"
                "仅 sandbox 草稿，不代表已写入 CRM 或对外触达。"
            ),
            limit=20000,
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
    tool_events: list[CoreMemoryToolEvent] = Field(default_factory=list)
    parsed_output: dict[str, Any] | None = None
    debug_trace: dict[str, Any] | None = None
    error: dict[str, str] | None = None
    created_at: datetime = Field(default_factory=utc_now)


class V3SandboxSession(V3SandboxModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str = "V3 Sandbox Session"
    core_memory_blocks: dict[str, CoreMemoryBlock] = Field(default_factory=default_core_memory_blocks)
    messages: list[V3SandboxMessage] = Field(default_factory=list)
    trace: list[V3SandboxTraceEvent] = Field(default_factory=list)
    context_summary: str | None = None
    summary_cursor_message_id: str | None = None
    summary_recursion_count: int = 0
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class V3SandboxTurnResult(V3SandboxModel):
    session: V3SandboxSession
    assistant_message: V3SandboxMessage
    trace_event: V3SandboxTraceEvent


class V3SandboxReplayReport(V3SandboxModel):
    status: Literal["completed", "failed"]
    source_session_id: str
    replay_session_id: str
    replayed_turns: int = 0
    failed_turn_index: int | None = None
    error: dict[str, str] | None = None
