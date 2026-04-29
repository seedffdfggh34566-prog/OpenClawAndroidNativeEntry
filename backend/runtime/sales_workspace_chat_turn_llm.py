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
from backend.runtime.sales_workspace_memory_decision import (
    MemoryDecision,
    MemoryGateResult,
    build_memory_decision_messages,
    build_memory_patch_draft,
    parse_memory_decision_json,
)
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
        return self


class SalesAgentTurnLlmResult(SalesAgentTurnLlmModel):
    output: SalesAgentTurnLlmOutput
    patch_draft: WorkspacePatchDraft | None = None
    memory_decision: MemoryDecision | None = None
    memory_gate: MemoryGateResult | None = None
    runtime_metadata: dict[str, Any] = Field(default_factory=dict)


class SalesAgentTurnMemoryPipelineResult(SalesAgentTurnLlmModel):
    patch_draft: WorkspacePatchDraft | None = None
    memory_decision: MemoryDecision | None = None
    memory_gate: MemoryGateResult | None = None


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
    llm_request_attempts = 0
    try:
        last_validation_error: ValueError | ValidationError | None = None
        output: SalesAgentTurnLlmOutput | None = None
        memory_patch_result: Any | None = None
        for attempt in range(2):
            completion: Any | None = None
            for request_attempt in range(2):
                llm_request_attempts += 1
                try:
                    completion = llm_client.complete(messages)
                    break
                except TokenHubClientError as exc:
                    if request_attempt == 0 and _is_transient_llm_request_error(exc):
                        continue
                    raise
            if completion is None:
                raise SalesAgentTurnLlmError("llm_runtime_unavailable", "LLM request did not return a completion")
            raw_content = completion.content
            usage = completion.usage
            try:
                parsed_json = _normalize_raw_output(
                    parse_sales_agent_turn_llm_json(completion.content),
                    source_message=source_message,
                )
                output = SalesAgentTurnLlmOutput.model_validate(parsed_json)
                memory_patch_result = _build_memory_patch_draft(
                    llm_client=llm_client,
                    settings=settings,
                    workspace=workspace,
                    source_message=source_message,
                    agent_run=agent_run,
                    context_pack=context_pack,
                    output=output,
                    base_workspace_version=base_workspace_version,
                    instruction=instruction,
                    usage=usage,
                    llm_request_attempts=llm_request_attempts,
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
                memory_decision=None,
                memory_gate=None,
                runtime_metadata={
                    "provider": settings.llm_provider,
                    "model": settings.llm_model,
                    "prompt_version": settings.sales_agent_llm_prompt_version,
                    "mode": "real_llm_no_langgraph",
                    "intent": source_message.message_type,
                    "llm_usage": _normalize_llm_usage(usage),
                    "llm_request_attempts": llm_request_attempts,
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
        patch_draft=memory_patch_result.patch_draft if memory_patch_result is not None else None,
        memory_decision=memory_patch_result.memory_decision if memory_patch_result is not None else None,
        memory_gate=memory_patch_result.memory_gate if memory_patch_result is not None else None,
        runtime_metadata={
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "prompt_version": settings.sales_agent_llm_prompt_version,
            "mode": "real_llm_memory_decision_no_langgraph",
            "intent": source_message.message_type,
            "llm_usage": _normalize_llm_usage(usage),
            "llm_request_attempts": llm_request_attempts,
            "confidence": output.confidence,
            "missing_fields": output.missing_fields,
            "memory_decision": (
                memory_patch_result.memory_decision.model_dump(mode="json")
                if memory_patch_result is not None and memory_patch_result.memory_decision is not None
                else None
            ),
            "memory_gate": (
                memory_patch_result.memory_gate.model_dump(mode="json")
                if memory_patch_result is not None and memory_patch_result.memory_gate is not None
                else None
            ),
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


def _build_memory_patch_draft(
    *,
    llm_client: TokenHubClient,
    settings: Settings,
    workspace: SalesWorkspace,
    source_message: ConversationMessage,
    agent_run: SalesAgentTurnRun,
    context_pack: SalesAgentTurnContextPack,
    output: SalesAgentTurnLlmOutput,
    base_workspace_version: int,
    instruction: str,
    usage: dict[str, Any],
    llm_request_attempts: int,
) -> SalesAgentTurnMemoryPipelineResult:
    if source_message.message_type in {"workspace_question", "out_of_scope_v2_2"}:
        return SalesAgentTurnMemoryPipelineResult()
    if output.message_type in {"clarifying_question", "workspace_question", "out_of_scope_v2_2"}:
        return SalesAgentTurnMemoryPipelineResult()

    evaluator_messages = build_memory_decision_messages(
        source_message=source_message,
        assistant_output=output.model_dump(mode="json"),
        context_pack=context_pack,
        workspace=workspace,
    )
    evaluator_usage: dict[str, Any] = {}
    try:
        completion = llm_client.complete(evaluator_messages)
        evaluator_usage = completion.usage
        memory_decision = MemoryDecision.model_validate(parse_memory_decision_json(completion.content))
    except (TokenHubClientError, ValueError, ValidationError):
        memory_decision = MemoryDecision(
            decision="reject",
            proposals=[],
            reasoning_summary="memory evaluator failed; backend kept response non-mutating",
        )

    build_result = build_memory_patch_draft(
        workspace=workspace,
        source_message=source_message,
        agent_run=agent_run,
        context_pack=context_pack,
        memory_decision=memory_decision,
        base_workspace_version=base_workspace_version,
        instruction=instruction,
        settings=settings,
        response_usage=usage,
        evaluator_usage=evaluator_usage,
        llm_request_attempts=llm_request_attempts,
    )
    return SalesAgentTurnMemoryPipelineResult(
        patch_draft=build_result.patch_draft,
        memory_decision=memory_decision,
        memory_gate=build_result.gate,
    )


def _is_transient_llm_request_error(exc: TokenHubClientError) -> bool:
    message = str(exc).lower()
    return any(marker in message for marker in ("timeout", "timed out", "unavailable", "temporar", "transient"))


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
    if _should_force_product_profile_draft(normalized, source_message):
        normalized["message_type"] = "draft_summary"
        normalized["patch_operations"] = _normalize_operations(normalized.get("patch_operations"))
        return normalized
    if _should_force_lead_direction_draft(normalized, source_message):
        normalized["message_type"] = "draft_summary"
        normalized["patch_operations"] = _normalize_operations(normalized.get("patch_operations"))
        return normalized
    if (
        isinstance(operations, list)
        and operations
        and source_message.message_type
        in {"product_profile_update", "lead_direction_update", "mixed_product_and_direction_update"}
    ):
        normalized["message_type"] = "draft_summary"
    if normalized.get("message_type") == "draft_summary":
        normalized["patch_operations"] = _normalize_operations(normalized.get("patch_operations"))
    return normalized


def _normalize_operations(operations: Any) -> list[dict[str, Any]]:
    if not isinstance(operations, list):
        return []
    return [
        operation
        for operation in operations
        if isinstance(operation, dict) and isinstance(operation.get("type"), str)
    ]


def _should_force_product_profile_draft(normalized: dict[str, Any], source_message: ConversationMessage) -> bool:
    if source_message.message_type != "product_profile_update":
        return False
    if normalized.get("message_type") == "draft_summary":
        return False
    if normalized.get("patch_operations"):
        return False
    if normalized.get("message_type") == "clarifying_question" and len(normalized.get("clarifying_questions") or []) < 3:
        return False
    content = source_message.content.strip()
    if len(content) < 8:
        return False
    product_markers = (
        "我们做",
        "我做",
        "产品是",
        "服务是",
        "软件",
        "SaaS",
        "saas",
        "工具",
        "平台",
        "培训",
        "外包",
        "维保",
        "系统",
        "App",
        "应用",
    )
    vague_markers = ("帮我找客户", "我要找客户", "怎么找客户")
    return any(marker in content for marker in product_markers) and not content in vague_markers


def _should_force_lead_direction_draft(normalized: dict[str, Any], source_message: ConversationMessage) -> bool:
    if source_message.message_type != "lead_direction_update":
        return False
    if normalized.get("message_type") == "draft_summary":
        return False
    content = source_message.content.strip()
    if not content:
        return False
    intent_markers = ("客户", "找", "获客", "方向", "行业", "第一批", "怎么", "谁", "建议", "线索")
    return len(content) >= 12 or any(marker in content for marker in intent_markers)


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


def _build_sales_agent_turn_messages(
    *,
    source_message: ConversationMessage,
    context_pack: SalesAgentTurnContextPack,
    workspace: SalesWorkspace,
) -> list[dict[str, str]]:
    output_schema = {
        "message_type": "clarifying_question | workspace_question | draft_summary | out_of_scope_v2_2",
        "assistant_message": "完整中文回复，必须可独立阅读；先总结已理解的信息，再说明下一步",
        "clarifying_questions": ["信息不足时输出 3 到 5 个中文追问"],
        "patch_operations": [],
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
                "你只能基于输入的 workspace context 回答用户。"
                "不要联网搜索，不要生成公司名单、联系人、CRM 或自动触达内容。"
                "assistant_message 必须是完整自然语言回答。"
                "不要写“请补充以下内容/如下信息”后不列具体内容。"
                "不要在 assistant_message 中暴露字段名、schema、runtime、workspace_goal、blocked_capabilities、"
                "revision_id、patch_operations、ContextPack 或其他开发者术语。"
                "context_pack.current_product_profile_revision 和 current_lead_direction_version 是已经写入"
                "正式工作区的事实基线。你只能在此基础上补充、修正或解释。"
                "如果用户信息不足，输出 3 到 5 个中文追问，不要生成 patch_operations。"
                "但如果 user_message.message_type 是 product_profile_update，且用户已经描述了产品或服务，"
                "必须先用自然语言说明你理解到的产品事实；缺失信息写入 missing_fields，不要只追问。"
                "但如果 user_message.message_type 是 lead_direction_update，主任务是给找客户执行建议："
                "必须先回答应该找谁、为什么、怎么找；回复至少包含优先客户画像、优先行业或场景、"
                "筛选信号、可执行渠道或关键词、暂不建议方向。"
                "对“我的客户是什么/我该找谁/怎么找客户/第一批客户怎么找”这类输入，禁止只追问；"
                "即使仍有缺失信息，也要给一版可执行建议，把不确定项写入 missing_fields。"
                "不要承诺已经写入或已经沉淀到工作区；后端会用单独 MemoryEvaluator 判断是否保存。"
                "如果用户问当前方向原因，基于 context_pack 解释。"
                "patch_operations 必须输出空数组；正式记忆沉淀不由本轮回答模型决定。"
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
                "patch_operations 必须是空数组；正式记忆沉淀由后续 MemoryEvaluator 完成。\n\n"
                f"output_schema:\n{json.dumps(output_schema, ensure_ascii=False)}\n\n"
                f"runtime_input:\n{json.dumps(context, ensure_ascii=False)}"
            ),
        },
    ]


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
