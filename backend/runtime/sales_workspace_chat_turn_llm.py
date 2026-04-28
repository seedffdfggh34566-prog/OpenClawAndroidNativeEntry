from __future__ import annotations

import json
import re
from time import perf_counter
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from backend.api.config import Settings
from backend.runtime.llm_client import TokenHubClient, TokenHubClientError
from backend.runtime.llm_trace import record_llm_trace, utc_now_iso
from backend.runtime.sales_workspace_patchdraft import WorkspacePatchDraft, WorkspacePatchDraftOperation
from backend.sales_workspace.chat_first import ConversationMessage, SalesAgentTurnContextPack, SalesAgentTurnRun
from backend.sales_workspace.schemas import SalesWorkspace


class SalesAgentTurnLlmError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class SalesAgentTurnLlmModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SalesAgentTurnLlmOutput(SalesAgentTurnLlmModel):
    message_type: Literal["clarifying_question", "workspace_question", "draft_summary", "out_of_scope_v2_2"]
    assistant_message: str = Field(min_length=1)
    clarifying_questions: list[str] = Field(default_factory=list)
    patch_operations: list[WorkspacePatchDraftOperation] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)
    missing_fields: list[str] = Field(default_factory=list)
    reasoning_summary: str = ""

    @model_validator(mode="after")
    def validate_runtime_output(self) -> SalesAgentTurnLlmOutput:
        if self.message_type == "clarifying_question":
            if not 3 <= len(self.clarifying_questions) <= 5:
                raise ValueError("clarifying_question requires 3 to 5 questions")
            if self.patch_operations:
                raise ValueError("clarifying_question must not include patch operations")
        if self.message_type in {"workspace_question", "out_of_scope_v2_2"} and self.patch_operations:
            raise ValueError(f"{self.message_type} must not include patch operations")
        if self.message_type == "draft_summary" and not self.patch_operations:
            raise ValueError("draft_summary requires patch operations")
        return self


class SalesAgentTurnLlmResult(SalesAgentTurnLlmModel):
    output: SalesAgentTurnLlmOutput
    patch_draft: WorkspacePatchDraft | None = None
    runtime_metadata: dict[str, Any] = Field(default_factory=dict)


def generate_sales_agent_turn_llm_result(
    *,
    settings: Settings,
    workspace: SalesWorkspace,
    source_message: ConversationMessage,
    agent_run: SalesAgentTurnRun,
    context_pack: SalesAgentTurnContextPack,
    base_workspace_version: int,
    instruction: str,
    client: TokenHubClient | None = None,
) -> SalesAgentTurnLlmResult:
    llm_client = client or TokenHubClient(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        timeout_seconds=max(settings.llm_timeout_seconds, 90.0),
    )
    messages = _build_sales_agent_turn_messages(
        source_message=source_message,
        context_pack=context_pack,
        workspace=workspace,
    )
    started_at = utc_now_iso()
    started_perf = perf_counter()
    raw_content: str | None = None
    parsed_json: dict[str, Any] | None = None
    usage: dict[str, Any] = {}
    try:
        last_validation_error: ValueError | ValidationError | None = None
        output: SalesAgentTurnLlmOutput | None = None
        patch_draft: WorkspacePatchDraft | None = None
        for attempt in range(2):
            completion = llm_client.complete(messages)
            raw_content = completion.content
            usage = completion.usage
            try:
                parsed_json = _normalize_raw_output(
                    parse_sales_agent_turn_llm_json(completion.content),
                    source_message=source_message,
                )
                output = SalesAgentTurnLlmOutput.model_validate(parsed_json)
                patch_draft = _build_patch_draft(
                    workspace=workspace,
                    source_message=source_message,
                    agent_run=agent_run,
                    context_pack=context_pack,
                    output=output,
                    base_workspace_version=base_workspace_version,
                    instruction=instruction,
                    settings=settings,
                    usage=usage,
                )
                break
            except (ValueError, ValidationError) as exc:
                last_validation_error = exc
                if attempt == 0:
                    messages = [
                        *messages,
                        {
                            "role": "user",
                            "content": (
                                "上一次输出没有通过后端 JSON/schema 校验。"
                                "请只重新输出一个完整 JSON object，必须包含 message_type、assistant_message、"
                                "clarifying_questions、patch_operations、confidence、missing_fields、reasoning_summary。"
                                "不要输出 markdown、注释、空对象或额外文本。"
                            ),
                        },
                    ]
                    continue
                raise
        if output is None:
            raise last_validation_error or ValueError("sales_agent_turn_llm_output_missing")
    except TokenHubClientError as exc:
        _record_trace(
            settings=settings,
            agent_run=agent_run,
            started_at=started_at,
            started_perf=started_perf,
            raw_content=raw_content,
            parsed_json=parsed_json,
            usage=usage,
            parse_status="request_failed" if raw_content is None else "failed",
            error=exc,
        )
        raise SalesAgentTurnLlmError("llm_runtime_unavailable", str(exc)) from exc
    except (ValueError, ValidationError) as exc:
        if raw_content is not None and source_message.message_type == "workspace_question":
            output = SalesAgentTurnLlmOutput(
                message_type="workspace_question",
                assistant_message=_strip_thinking_and_fences(raw_content)[:2000],
                clarifying_questions=[],
                patch_operations=[],
                confidence=0.5,
                missing_fields=[],
                reasoning_summary="LLM returned text explanation instead of structured JSON; backend kept non-mutating answer.",
            )
            _record_trace(
                settings=settings,
                agent_run=agent_run,
                started_at=started_at,
                started_perf=started_perf,
                raw_content=raw_content,
                parsed_json=output.model_dump(mode="json"),
                usage=usage,
                parse_status="text_fallback",
                error=exc,
            )
            return SalesAgentTurnLlmResult(
                output=output,
                patch_draft=None,
                runtime_metadata={
                    "provider": settings.llm_provider,
                    "model": settings.llm_model,
                    "prompt_version": settings.sales_agent_llm_prompt_version,
                    "mode": "real_llm_no_langgraph",
                    "intent": source_message.message_type,
                    "llm_usage": _normalize_llm_usage(usage),
                    "structured_output_fallback": "workspace_question_text",
                },
            )
        _record_trace(
            settings=settings,
            agent_run=agent_run,
            started_at=started_at,
            started_perf=started_perf,
            raw_content=raw_content,
            parsed_json=parsed_json,
            usage=usage,
            parse_status="failed",
            error=exc,
        )
        raise SalesAgentTurnLlmError("llm_structured_output_invalid", str(exc)) from exc

    _record_trace(
        settings=settings,
        agent_run=agent_run,
        started_at=started_at,
        started_perf=started_perf,
        raw_content=raw_content,
        parsed_json=output.model_dump(mode="json"),
        usage=usage,
        parse_status="succeeded",
        error=None,
    )
    return SalesAgentTurnLlmResult(
        output=output,
        patch_draft=patch_draft,
        runtime_metadata={
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "prompt_version": settings.sales_agent_llm_prompt_version,
            "mode": "real_llm_no_langgraph",
            "intent": source_message.message_type,
            "llm_usage": _normalize_llm_usage(usage),
            "confidence": output.confidence,
            "missing_fields": output.missing_fields,
        },
    )


def parse_sales_agent_turn_llm_json(content: str) -> dict[str, Any]:
    text = _strip_thinking_and_fences(content)
    decoder = json.JSONDecoder()
    saw_json_start = False
    last_error: json.JSONDecodeError | None = None
    first_object: dict[str, Any] | None = None
    for index, char in enumerate(text):
        if char != "{":
            continue
        saw_json_start = True
        for candidate in _sales_agent_turn_json_candidates(text[index:]):
            try:
                parsed, _ = decoder.raw_decode(candidate)
            except json.JSONDecodeError as exc:
                last_error = exc
                continue
            if not isinstance(parsed, dict):
                raise ValueError("sales_agent_turn_llm_json_object_required")
            if first_object is None:
                first_object = parsed
            if "message_type" in parsed:
                return parsed
    if first_object is not None:
        return first_object
    if saw_json_start:
        raise ValueError("sales_agent_turn_llm_json_decode_failed") from last_error
    raise ValueError("sales_agent_turn_llm_json_object_not_found")


def _sales_agent_turn_json_candidates(candidate: str) -> list[str]:
    text = candidate.strip()
    candidates = [text]

    repaired_extra_object_brace = re.sub(r'"\}\]\}\s*$', r'"]}', text)
    if repaired_extra_object_brace != text:
        candidates.append(repaired_extra_object_brace)

    if text.count("[") > text.count("]"):
        repaired_missing_array_close = re.sub(r'"\}\s*$', r'"]}', text)
        if repaired_missing_array_close != text:
            candidates.append(repaired_missing_array_close)

    return candidates


def _normalize_raw_output(
    parsed: dict[str, Any],
    *,
    source_message: ConversationMessage,
) -> dict[str, Any]:
    normalized = _normalize_top_level_fields(parsed)
    operations = normalized.get("patch_operations")
    if source_message.message_type == "workspace_question":
        normalized["message_type"] = "workspace_question"
        normalized["patch_operations"] = []
        return normalized
    if source_message.message_type == "out_of_scope_v2_2":
        normalized["message_type"] = "out_of_scope_v2_2"
        normalized["patch_operations"] = []
        return normalized
    if (
        isinstance(operations, list)
        and operations
        and source_message.message_type
        in {"product_profile_update", "lead_direction_update", "mixed_product_and_direction_update"}
    ):
        normalized["message_type"] = "draft_summary"
    if normalized.get("message_type") == "draft_summary":
        normalized["patch_operations"] = _ensure_required_operations(
            normalized.get("patch_operations"),
            source_message=source_message,
        )
    return normalized


def _normalize_top_level_fields(parsed: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(parsed)
    if "reasoning_summary" not in normalized and "reasoning_sumary" in normalized:
        normalized["reasoning_summary"] = normalized["reasoning_sumary"]
    allowed = {
        "message_type",
        "assistant_message",
        "clarifying_questions",
        "patch_operations",
        "confidence",
        "missing_fields",
        "reasoning_summary",
    }
    return {key: value for key, value in normalized.items() if key in allowed}


def _ensure_required_operations(
    operations: Any,
    *,
    source_message: ConversationMessage,
) -> list[dict[str, Any]]:
    if not isinstance(operations, list):
        operations = []
    normalized_operations = [
        operation
        for operation in operations
        if isinstance(operation, dict) and isinstance(operation.get("type"), str)
    ]
    operation_types = {operation["type"] for operation in normalized_operations}
    if (
        source_message.message_type in {"product_profile_update", "mixed_product_and_direction_update"}
        and "upsert_product_profile_revision" not in operation_types
    ):
        normalized_operations.append(_fallback_product_operation(source_message))
    if (
        source_message.message_type in {"lead_direction_update", "mixed_product_and_direction_update"}
        and "upsert_lead_direction_version" not in operation_types
    ):
        normalized_operations.append(_fallback_direction_operation(source_message))
    return normalized_operations


def _fallback_product_operation(source_message: ConversationMessage) -> dict[str, Any]:
    return {
        "type": "upsert_product_profile_revision",
        "payload": {
            "product_name": "待确认产品或服务",
            "one_liner": source_message.content[:80],
            "target_customers": ["待确认目标客户"],
            "target_industries": ["待确认行业"],
            "pain_points": ["待确认痛点"],
            "value_props": ["待确认价值主张"],
            "constraints": ["LLM output omitted product operation; backend kept a reviewable placeholder."],
        },
    }


def _fallback_direction_operation(source_message: ConversationMessage) -> dict[str, Any]:
    return {
        "type": "upsert_lead_direction_version",
        "payload": {
            "priority_industries": ["待确认优先行业"],
            "target_customer_types": ["待确认目标客户类型"],
            "regions": ["待确认地区"],
            "company_sizes": ["待确认规模"],
            "priority_constraints": ["需要继续确认优先约束"],
            "excluded_industries": [],
            "excluded_customer_types": [],
            "change_reason": (
                "LLM output omitted lead direction operation; backend kept a reviewable placeholder "
                f"from message {source_message.id}: {source_message.content[:120]}"
            ),
        },
    }


def _build_sales_agent_turn_messages(
    *,
    source_message: ConversationMessage,
    context_pack: SalesAgentTurnContextPack,
    workspace: SalesWorkspace,
) -> list[dict[str, str]]:
    output_schema = {
        "message_type": "clarifying_question | workspace_question | draft_summary | out_of_scope_v2_2",
        "assistant_message": "中文回复，简洁说明本轮结果",
        "clarifying_questions": ["信息不足时输出 3 到 5 个中文追问"],
        "patch_operations": [
            {
                "type": "upsert_product_profile_revision | upsert_lead_direction_version",
                "payload": {
                    "product_name": "产品名，仅 product profile 需要",
                    "one_liner": "一句话产品理解",
                    "target_customers": ["目标客户"],
                    "target_industries": ["目标行业"],
                    "pain_points": ["客户痛点"],
                    "value_props": ["价值主张"],
                    "constraints": ["限制或待确认事项"],
                    "priority_industries": ["优先行业，仅 lead direction 需要"],
                    "target_customer_types": ["目标客户类型"],
                    "regions": ["地区"],
                    "company_sizes": ["规模"],
                    "priority_constraints": ["优先约束"],
                    "excluded_industries": ["排除行业"],
                    "excluded_customer_types": ["排除客户类型"],
                    "change_reason": "方向变化原因",
                },
            }
        ],
        "confidence": "0 到 1",
        "missing_fields": ["仍缺失的信息"],
        "reasoning_summary": "短摘要，不要输出 chain-of-thought",
    }
    context = {
        "workspace": {
            "id": workspace.id,
            "name": workspace.name,
            "goal": workspace.goal,
            "workspace_version": workspace.workspace_version,
            "current_product_profile_revision_id": workspace.current_product_profile_revision_id,
            "current_lead_direction_version_id": workspace.current_lead_direction_version_id,
        },
        "context_pack": context_pack.model_dump(mode="json"),
        "user_message": source_message.model_dump(mode="json"),
    }
    return [
        {
            "role": "system",
            "content": (
                "你是 OpenClaw V2.1 的 Product Sales Agent Runtime。"
                "你只能基于输入的 workspace context 回答或生成可审阅草稿。"
                "不要联网搜索，不要生成公司名单、联系人、CRM 或自动触达内容。"
                "如果用户信息不足，输出 3 到 5 个中文追问，不要生成 patch_operations。"
                "如果用户问当前方向原因，基于 context_pack 解释，不要生成 patch_operations。"
                "如果用户提供产品理解或获客方向，输出 patch_operations，backend 会补齐 id/version/workspace_id。"
                "如果 user_message.message_type 是 mixed_product_and_direction_update，patch_operations 必须同时包含"
                "一个 upsert_product_profile_revision 和一个 upsert_lead_direction_version。"
                "不要输出空 JSON，不要省略 message_type、assistant_message、clarifying_questions、patch_operations、"
                "confidence、missing_fields、reasoning_summary。"
                "只输出单个 JSON object，不要输出 markdown、解释或额外文本。"
            ),
        },
        {
            "role": "user",
            "content": (
                "请处理这轮 sales-agent-turn。\n"
                "输出字段必须严格匹配 output_schema。\n"
                "Allowed operations: upsert_product_profile_revision, upsert_lead_direction_version。\n"
                "不要输出 set_active_lead_direction，backend 会在方向更新时补齐。\n\n"
                f"output_schema:\n{json.dumps(output_schema, ensure_ascii=False)}\n\n"
                f"runtime_input:\n{json.dumps(context, ensure_ascii=False)}"
            ),
        },
    ]


def _build_patch_draft(
    *,
    workspace: SalesWorkspace,
    source_message: ConversationMessage,
    agent_run: SalesAgentTurnRun,
    context_pack: SalesAgentTurnContextPack,
    output: SalesAgentTurnLlmOutput,
    base_workspace_version: int,
    instruction: str,
    settings: Settings,
    usage: dict[str, Any],
) -> WorkspacePatchDraft | None:
    if output.message_type != "draft_summary":
        return None

    next_workspace_version = workspace.workspace_version + 1
    operations: list[WorkspacePatchDraftOperation] = []
    current_product = (
        workspace.product_profile_revisions.get(workspace.current_product_profile_revision_id)
        if workspace.current_product_profile_revision_id
        else None
    )
    current_direction = (
        workspace.lead_direction_versions.get(workspace.current_lead_direction_version_id)
        if workspace.current_lead_direction_version_id
        else None
    )
    product_version = (current_product.version + 1) if current_product else 1
    direction_version = (current_direction.version + 1) if current_direction else 1
    direction_id: str | None = None

    for operation in output.patch_operations:
        payload = _sanitize_operation_payload(operation.type, operation.payload)
        if operation.type == "upsert_product_profile_revision":
            payload["id"] = payload.get("id") or f"ppr_llm_v{next_workspace_version}"
            payload["version"] = payload.get("version") or product_version
            payload["constraints"] = [
                *list(payload.get("constraints") or []),
                f"derived from message {source_message.id}",
            ]
        elif operation.type == "upsert_lead_direction_version":
            direction_id = str(payload.get("id") or f"dir_llm_v{next_workspace_version}")
            payload["id"] = direction_id
            payload["version"] = payload.get("version") or direction_version
            payload["change_reason"] = payload.get("change_reason") or (
                f"LLM runtime generated direction draft from message {source_message.id}: "
                f"{source_message.content[:120]}"
            )
        operations.append(WorkspacePatchDraftOperation(type=operation.type, payload=payload))

    if direction_id is not None:
        operations.append(
            WorkspacePatchDraftOperation(
                type="set_active_lead_direction",
                payload={"lead_direction_version_id": direction_id},
            )
        )

    return WorkspacePatchDraft(
        id=f"draft_sales_turn_llm_v{next_workspace_version}",
        workspace_id=workspace.id,
        base_workspace_version=base_workspace_version,
        author="sales_agent_turn_llm_runtime",
        instruction=instruction or f"LLM chat-first {source_message.message_type}",
        runtime_metadata={
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "prompt_version": settings.sales_agent_llm_prompt_version,
            "mode": "real_llm_no_langgraph",
            "intent": source_message.message_type,
            "agent_run_id": agent_run.id,
            "context_pack_id": context_pack.id,
            "source_message_ids": [source_message.id],
            "llm_usage": _normalize_llm_usage(usage),
            "confidence": output.confidence,
            "missing_fields": output.missing_fields,
            "kernel_boundary": (
                "Runtime returns WorkspacePatchDraft; Sales Workspace Kernel validates and writes formal objects."
            ),
        },
        operations=operations,
    )


def _sanitize_operation_payload(operation_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    product_fields = {
        "id",
        "workspace_id",
        "version",
        "product_name",
        "one_liner",
        "target_customers",
        "target_industries",
        "pain_points",
        "value_props",
        "constraints",
    }
    direction_fields = {
        "id",
        "workspace_id",
        "version",
        "priority_industries",
        "target_customer_types",
        "regions",
        "company_sizes",
        "priority_constraints",
        "excluded_industries",
        "excluded_customer_types",
        "change_reason",
    }
    if operation_type == "upsert_product_profile_revision":
        allowed = product_fields
    elif operation_type == "upsert_lead_direction_version":
        allowed = direction_fields
    else:
        return dict(payload)
    return {key: value for key, value in payload.items() if key in allowed}


def _record_trace(
    *,
    settings: Settings,
    agent_run: SalesAgentTurnRun,
    started_at: str,
    started_perf: float,
    raw_content: str | None,
    parsed_json: dict[str, Any] | None,
    usage: dict[str, Any],
    parse_status: str,
    error: Exception | None,
) -> None:
    record_llm_trace(
        settings,
        run_id=agent_run.id,
        run_type="sales_agent_turn",
        provider=settings.llm_provider,
        model=settings.llm_model,
        prompt_version=settings.sales_agent_llm_prompt_version,
        started_at=started_at,
        ended_at=utc_now_iso(),
        duration_ms=round((perf_counter() - started_perf) * 1000, 3),
        raw_content=raw_content,
        parsed_draft=parsed_json,
        usage=usage,
        parse_status=parse_status,
        error_type=type(error).__name__ if error else None,
        error_message=str(error) if error else None,
    )


def _strip_thinking_and_fences(content: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE)
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _token_count(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float) and value.is_integer():
        count = int(value)
        return count if count >= 0 else None
    return None


def _normalize_llm_usage(usage: dict[str, Any]) -> dict[str, int]:
    normalized: dict[str, int] = {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        count = _token_count(usage.get(key))
        if count is not None:
            normalized[key] = count
    prompt_details = usage.get("prompt_tokens_details")
    if isinstance(prompt_details, dict):
        cached_tokens = _token_count(prompt_details.get("cached_tokens"))
        if cached_tokens is not None:
            normalized["cached_tokens"] = cached_tokens
    completion_details = usage.get("completion_tokens_details")
    if isinstance(completion_details, dict):
        reasoning_tokens = _token_count(completion_details.get("reasoning_tokens"))
        if reasoning_tokens is not None:
            normalized["reasoning_tokens"] = reasoning_tokens
    return normalized
