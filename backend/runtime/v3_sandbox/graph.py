from __future__ import annotations

import json
import re
from time import perf_counter
from typing import Any, TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from pydantic import ValidationError

from backend.api.config import Settings
from backend.runtime.llm_client import TokenHubClient, TokenHubClientError, TokenHubCompletion, TokenHubToolCall
from backend.runtime.tokenhub_native_fc import tokenhub_native_fc_request_policy
from backend.runtime.v3_sandbox.schemas import (
    AgentAction,
    CoreMemoryBlock,
    CoreMemoryToolEvent,
    CoreMemoryToolName,
    CustomerCandidateDraft,
    MemoryItem,
    V3SandboxDebugTraceOptions,
    V3SandboxMessage,
    V3SandboxSession,
    V3SandboxTraceEvent,
    V3SandboxTurnOutput,
    V3SandboxTurnResult,
    utc_now,
)


class V3SandboxRuntimeError(RuntimeError):
    def __init__(self, code: str, message: str, *, session: V3SandboxSession | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.session = session


class V3SandboxGraphState(TypedDict, total=False):
    settings: Settings
    session: V3SandboxSession
    user_message: V3SandboxMessage
    turn_id: str
    raw_content: str
    usage: dict[str, Any]
    usage_total: dict[str, int]
    parsed_output: V3SandboxTurnOutput
    actions: list[AgentAction]
    tool_messages: list[dict[str, Any]]
    tool_events: list[CoreMemoryToolEvent]
    _current_tool_calls: list[TokenHubToolCall]
    final_message: str
    runtime_metadata: dict[str, Any]
    assistant_message: V3SandboxMessage
    trace_event: V3SandboxTraceEvent
    started_perf: float
    debug_options: V3SandboxDebugTraceOptions
    debug_trace: dict[str, Any] | None


def run_v3_sandbox_turn(
    *,
    settings: Settings,
    session: V3SandboxSession,
    user_message: V3SandboxMessage,
    client: TokenHubClient | None = None,
    debug_options: V3SandboxDebugTraceOptions | dict[str, Any] | None = None,
) -> V3SandboxTurnResult:
    graph = _build_graph(client=client)
    turn_id = f"turn_{uuid4().hex[:12]}"
    runtime_session = session.model_copy(deep=True)
    started_perf = perf_counter()
    normalized_debug_options = V3SandboxDebugTraceOptions.model_validate(debug_options or {})
    debug_trace = _new_debug_trace(normalized_debug_options) if _debug_enabled(normalized_debug_options) else None
    try:
        state = graph.invoke(
            {
                "settings": settings,
                "session": runtime_session,
                "user_message": user_message,
                "turn_id": turn_id,
                "started_perf": started_perf,
                "debug_options": normalized_debug_options,
                "debug_trace": debug_trace,
            }
        )
    except TokenHubClientError as exc:
        failed_session = _failed_session(
            settings=settings,
            session=runtime_session,
            user_message=user_message,
            turn_id=turn_id,
            started_perf=started_perf,
            debug_trace=debug_trace,
            code="llm_runtime_unavailable",
            message=str(exc),
        )
        raise V3SandboxRuntimeError("llm_runtime_unavailable", str(exc), session=failed_session) from exc
    except (ValueError, ValidationError) as exc:
        failed_session = _failed_session(
            settings=settings,
            session=runtime_session,
            user_message=user_message,
            turn_id=turn_id,
            started_perf=started_perf,
            debug_trace=debug_trace,
            code="llm_structured_output_invalid",
            message=str(exc),
        )
        raise V3SandboxRuntimeError("llm_structured_output_invalid", str(exc), session=failed_session) from exc

    return V3SandboxTurnResult(
        session=state["session"],
        assistant_message=state["assistant_message"],
        actions=state["actions"],
        trace_event=state["trace_event"],
    )


def _build_graph(*, client: TokenHubClient | None = None):
    graph = StateGraph(V3SandboxGraphState)
    graph.add_node("load_state", _load_state)
    graph.add_node("compose_context", _compose_context)
    graph.add_node("call_agent_with_tools", lambda state: _call_agent_with_tools(state, client=client))
    graph.add_node("execute_tool_calls", _execute_tool_calls)
    graph.add_node("return_turn", _return_turn)
    graph.add_edge(START, "load_state")
    graph.add_edge("load_state", "compose_context")
    graph.add_edge("compose_context", "call_agent_with_tools")
    graph.add_edge("call_agent_with_tools", "execute_tool_calls")
    graph.add_conditional_edges(
        "execute_tool_calls",
        _continue_or_return,
        {
            "continue": "call_agent_with_tools",
            "return": "return_turn",
        },
    )
    graph.add_edge("return_turn", END)
    return graph.compile()


def _load_state(state: V3SandboxGraphState) -> V3SandboxGraphState:
    started = perf_counter()
    session = state["session"]
    user_message = state["user_message"]
    before_messages = len(session.messages)
    session.messages.append(user_message)
    session.updated_at = utc_now()
    _append_debug_event(
        state.get("debug_trace"),
        state["debug_options"],
        {
            "node": "load_state",
            "status": "completed",
            "duration_ms": _duration_ms(started),
            "input": _maybe_node_io(
                state,
                {
                    "session_id": session.id,
                    "message_count_before": before_messages,
                    "user_message": user_message.model_dump(mode="json"),
                },
            ),
            "output": _maybe_node_io(
                state,
                {
                    "message_count_after": len(session.messages),
                    "updated_at": session.updated_at.isoformat(),
                },
            ),
        },
    )
    return {
        "session": session,
        "tool_events": [],
        "usage_total": {},
        "runtime_metadata": {
            "provider": "langgraph",
            "mode": "v3_sandbox_native_tool_loop_poc",
            "graph_name": "v3_sandbox_core_memory_tool_loop_poc",
            "memory_runtime": "native_tool_loop",
            "native_function_calling": True,
            "llm_provider": state["settings"].llm_provider,
            "llm_model": state["settings"].llm_model,
            "turn_id": state["turn_id"],
        },
    }


def _compose_context(state: V3SandboxGraphState) -> V3SandboxGraphState:
    started = perf_counter()
    messages = _build_tool_loop_messages(state["session"], state["user_message"])
    _append_debug_event(
        state.get("debug_trace"),
        state["debug_options"],
        {
            "node": "compose_context",
            "status": "completed",
            "duration_ms": _duration_ms(started),
            "input": _maybe_node_io(
                state,
                {
                    "session_id": state["session"].id,
                    "core_memory_blocks": list(state["session"].core_memory_blocks.keys()),
                    "message_count": len(state["session"].messages),
                },
            ),
            "output": _maybe_node_io(state, {"tool_message_count": len(messages)}),
        },
    )
    return {"tool_messages": messages}


def _call_agent_with_tools(state: V3SandboxGraphState, *, client: TokenHubClient | None) -> V3SandboxGraphState:
    started = perf_counter()
    settings = state["settings"]
    llm_client = client or TokenHubClient(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        timeout_seconds=max(settings.llm_timeout_seconds, 90.0),
    )
    messages = state["tool_messages"]
    event: dict[str, Any] = {
        "node": "call_agent_with_tools",
        "status": "completed",
        "input": _maybe_node_io(
            state,
            {
                "message_count": len(messages),
                "current_user_message_id": state["user_message"].id,
                "tool_names": [tool["function"]["name"] for tool in _core_memory_tools()],
            },
        ),
    }
    if state["debug_options"].include_prompt:
        event["messages"] = messages
    try:
        completion = llm_client.complete_with_tools(
            messages,
            tools=_core_memory_tools(),
            tool_choice="auto",
            model_policy=tokenhub_native_fc_request_policy(settings.llm_model, "auto"),
        )
    except Exception as exc:
        event["status"] = "error"
        event["duration_ms"] = _duration_ms(started)
        event["error"] = _debug_error(exc)
        _append_debug_event(state.get("debug_trace"), state["debug_options"], event)
        raise

    usage_total = _merge_usage(state.get("usage_total", {}), _normalize_usage(completion.usage))
    tool_calls = completion.tool_calls or []
    if not tool_calls:
        event["status"] = "error"
        event["duration_ms"] = _duration_ms(started)
        event["output"] = _maybe_node_io(
            state,
            {
                "finish_reason": completion.finish_reason,
                "content_length": len(completion.content),
                "tool_call_count": 0,
                "usage": _normalize_usage(completion.usage),
            },
        )
        if state["debug_options"].include_raw_llm_output:
            event["raw_output"] = completion.raw_message or completion.content
        _append_debug_event(state.get("debug_trace"), state["debug_options"], event)
        raise ValueError("v3_tool_loop_no_tool_call")

    assistant_message = _assistant_tool_message(completion)
    event["duration_ms"] = _duration_ms(started)
    event["output"] = _maybe_node_io(
        state,
        {
            "finish_reason": completion.finish_reason,
            "content_length": len(completion.content),
            "tool_call_count": len(tool_calls),
            "tool_calls": [_tool_call_summary(tool_call) for tool_call in tool_calls],
            "usage": _normalize_usage(completion.usage),
        },
    )
    if state["debug_options"].include_raw_llm_output:
        event["raw_output"] = completion.raw_message or completion.content
    _append_debug_event(state.get("debug_trace"), state["debug_options"], event)
    return {
        "raw_content": completion.content,
        "usage": completion.usage,
        "usage_total": usage_total,
        "tool_messages": [*messages, assistant_message],
        "_current_tool_calls": tool_calls,
    }


def _execute_tool_calls(state: V3SandboxGraphState) -> V3SandboxGraphState:
    started = perf_counter()
    session = state["session"]
    before_session = session.model_copy(deep=True)
    tool_calls: list[TokenHubToolCall] = state.get("_current_tool_calls", [])
    existing_tool_events = list(state.get("tool_events", []))
    tool_result_messages: list[dict[str, Any]] = []
    tool_results: list[dict[str, Any]] = []
    final_message: str | None = None
    event: dict[str, Any] = {
        "node": "execute_tool_calls",
        "status": "completed",
        "input": _maybe_node_io(state, {"tool_call_count": len(tool_calls)}),
    }
    try:
        send_indices = [index for index, tool_call in enumerate(tool_calls) if tool_call.function.name == "send_message"]
        if send_indices and send_indices[-1] != len(tool_calls) - 1:
            raise ValueError("v3_tool_loop_send_message_must_be_last")
        for index, tool_call in enumerate(tool_calls):
            result, tool_event = _execute_core_memory_tool(
                session=session,
                trace_turn_id=state["turn_id"],
                tool_call=tool_call,
                index=len(existing_tool_events) + index,
            )
            existing_tool_events.append(tool_event)
            tool_results.append(tool_event.model_dump(mode="json"))
            tool_result_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )
            if tool_call.function.name == "send_message" and tool_event.status == "applied":
                message = result.get("message")
                if isinstance(message, str) and message.strip():
                    final_message = message.strip()
    except Exception as exc:
        event["status"] = "error"
        event["duration_ms"] = _duration_ms(started)
        event["error"] = _debug_error(exc)
        event["tool_results"] = tool_results
        if state["debug_options"].include_state_diff:
            event["state_diff"] = _state_diff(before_session, session)
        _append_debug_event(state.get("debug_trace"), state["debug_options"], event)
        raise

    session.updated_at = utc_now()
    event["duration_ms"] = _duration_ms(started)
    event["output"] = _maybe_node_io(
        state,
        {
            "tool_event_count": len(tool_results),
            "final_message_present": bool(final_message),
            "core_memory_blocks": _core_memory_summary(session),
        },
    )
    event["tool_results"] = tool_results
    if state["debug_options"].include_state_diff:
        event["state_diff"] = _state_diff(before_session, session)
    _append_debug_event(state.get("debug_trace"), state["debug_options"], event)
    return {
        "session": session,
        "tool_events": existing_tool_events,
        "tool_messages": [*state["tool_messages"], *tool_result_messages],
        "final_message": final_message or "",
    }


def _continue_or_return(state: V3SandboxGraphState) -> str:
    if state.get("final_message"):
        return "return"
    tool_events = state.get("tool_events", [])
    if len(tool_events) >= 16:
        raise ValueError("v3_tool_loop_exhausted")
    call_count = sum(1 for message in state.get("tool_messages", []) if message.get("role") == "assistant")
    if call_count >= 4:
        raise ValueError("v3_tool_loop_exhausted")
    return "continue"


def _build_tool_loop_messages(session: V3SandboxSession, user_message: V3SandboxMessage) -> list[dict[str, Any]]:
    runtime_input = {
        "session_id": session.id,
        "core_memory_blocks": {
            label: block.model_dump(mode="json")
            for label, block in session.core_memory_blocks.items()
        },
        "legacy_active_memory_for_context": [
            item.model_dump(mode="json")
            for item in session.memory_items.values()
            if item.status not in {"rejected", "superseded"}
        ],
        "legacy_inactive_memory_for_correction_context_only": [
            item.model_dump(mode="json")
            for item in session.memory_items.values()
            if item.status in {"rejected", "superseded"}
        ],
        "working_state": session.working_state.model_dump(mode="json"),
        "customer_intelligence": session.customer_intelligence.model_dump(mode="json"),
        "recent_messages": [message.model_dump(mode="json") for message in session.messages[-8:]],
        "current_user_message": user_message.model_dump(mode="json"),
    }
    return [
        {
            "role": "system",
            "content": (
                "You are OpenClaw V3 Product Sales Agent running in a sandbox. "
                "Use native tools to maintain session-scoped core memory blocks before replying. "
                "Core memory is editable and should stay concise. Use exact memory tools for corrections. "
                "If the user corrects you, update the relevant core memory block rather than treating old text as current fact. "
                "Customer intelligence remains draft sandbox state; never claim CRM writes, outreach, export, or external actions. "
                "You must produce the final visible reply by calling send_message. Do not answer as plain assistant content."
            ),
        },
        {
            "role": "user",
            "content": (
                "Process the current sales-agent turn. First update core memory when useful, then call send_message. "
                "Use memory_insert or memory_replace for precise corrections when an exact anchor/substr is available; "
                "use core_memory_append for new facts or hypotheses.\n\n"
                f"runtime_input:\n{json.dumps(runtime_input, ensure_ascii=False)}"
            ),
        },
    ]


def _core_memory_tools() -> list[dict[str, Any]]:
    labels = ["persona", "human", "product", "sales_strategy", "customer_intelligence"]
    return [
        {
            "type": "function",
            "function": {
                "name": "core_memory_append",
                "description": "Append concise content to an existing core memory block.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string", "enum": labels},
                        "content": {"type": "string", "minLength": 1},
                    },
                    "required": ["label", "content"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "memory_insert",
                "description": "Insert content immediately after an exact anchor string inside a core memory block.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string", "enum": labels},
                        "insert_after": {"type": "string", "minLength": 1},
                        "content": {"type": "string", "minLength": 1},
                    },
                    "required": ["label", "insert_after", "content"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "memory_replace",
                "description": "Replace exact text inside a core memory block.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string", "enum": labels},
                        "old_content": {"type": "string", "minLength": 1},
                        "new_content": {"type": "string"},
                        "replace_all": {"type": "boolean", "default": False},
                    },
                    "required": ["label", "old_content", "new_content"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "send_message",
                "description": "Send the final visible assistant reply to the user. Must be the final tool call in a turn.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "minLength": 1},
                    },
                    "required": ["message"],
                    "additionalProperties": False,
                },
            },
        },
    ]


def _assistant_tool_message(completion: TokenHubCompletion) -> dict[str, Any]:
    raw = completion.raw_message if isinstance(completion.raw_message, dict) else {}
    tool_calls = raw.get("tool_calls")
    if not isinstance(tool_calls, list):
        tool_calls = [
            {
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in completion.tool_calls or []
        ]
    return {
        "role": "assistant",
        "content": completion.content,
        "tool_calls": tool_calls,
    }


def _tool_call_summary(tool_call: TokenHubToolCall) -> dict[str, Any]:
    return {
        "id": tool_call.id,
        "type": tool_call.type,
        "name": tool_call.function.name,
        "arguments_length": len(tool_call.function.arguments),
    }


def _execute_core_memory_tool(
    *,
    session: V3SandboxSession,
    trace_turn_id: str,
    tool_call: TokenHubToolCall,
    index: int,
) -> tuple[dict[str, Any], CoreMemoryToolEvent]:
    tool_name = tool_call.function.name
    arguments = _parse_tool_arguments(tool_call.function.arguments)
    created_at = utc_now()
    event_id = f"tool_{trace_turn_id}_{index}"
    try:
        if tool_name == "core_memory_append":
            result, block_label, before, after = _tool_core_memory_append(session, arguments)
        elif tool_name == "memory_insert":
            result, block_label, before, after = _tool_memory_insert(session, arguments)
        elif tool_name == "memory_replace":
            result, block_label, before, after = _tool_memory_replace(session, arguments)
        elif tool_name == "send_message":
            message = _require_arg_str(arguments, "message")
            result, block_label, before, after = {"ok": True, "message": message}, None, None, None
        else:
            raise ValueError(f"v3_unknown_core_memory_tool:{tool_name}")
        event = CoreMemoryToolEvent(
            id=event_id,
            tool_call_id=tool_call.id,
            tool_name=tool_name,
            arguments=arguments,
            status="applied",
            result=result,
            block_label=block_label,
            before_value=before,
            after_value=after,
            created_at=created_at,
        )
        return result, event
    except Exception as exc:
        block_label = arguments.get("label") if isinstance(arguments.get("label"), str) else None
        result = {"ok": False, "error": {"code": "core_memory_tool_error", "message": str(exc)}}
        event = CoreMemoryToolEvent(
            id=event_id,
            tool_call_id=tool_call.id,
            tool_name=tool_name,
            arguments=arguments,
            status="error",
            result=result,
            error={"code": "core_memory_tool_error", "message": str(exc)},
            block_label=block_label,
            created_at=created_at,
        )
        return result, event


def _parse_tool_arguments(raw_arguments: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_arguments or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError("v3_tool_arguments_not_json") from exc
    if not isinstance(parsed, dict):
        raise ValueError("v3_tool_arguments_object_required")
    return parsed


def _tool_core_memory_append(
    session: V3SandboxSession,
    arguments: dict[str, Any],
) -> tuple[dict[str, Any], str, str, str]:
    label = _require_block_label(arguments)
    content = _require_arg_str(arguments, "content")
    block = _editable_block(session, label)
    before = block.value
    separator = "\n" if before.strip() else ""
    after = f"{before.rstrip()}{separator}{content.strip()}".strip()
    _set_core_memory_block(session, block, after)
    return {"ok": True, "label": label, "operation": "append", "chars": len(after)}, label, before, after


def _tool_memory_insert(
    session: V3SandboxSession,
    arguments: dict[str, Any],
) -> tuple[dict[str, Any], str, str, str]:
    label = _require_block_label(arguments)
    insert_after = _require_arg_str(arguments, "insert_after")
    content = _require_arg_str(arguments, "content")
    block = _editable_block(session, label)
    before = block.value
    position = before.find(insert_after)
    if position < 0:
        raise ValueError("v3_memory_insert_anchor_not_found")
    insert_at = position + len(insert_after)
    after = f"{before[:insert_at]}{content}{before[insert_at:]}"
    _set_core_memory_block(session, block, after)
    return {"ok": True, "label": label, "operation": "insert", "chars": len(after)}, label, before, after


def _tool_memory_replace(
    session: V3SandboxSession,
    arguments: dict[str, Any],
) -> tuple[dict[str, Any], str, str, str]:
    label = _require_block_label(arguments)
    old_content = _require_arg_str(arguments, "old_content")
    new_content = _require_arg_str(arguments, "new_content", allow_empty=True)
    replace_all = bool(arguments.get("replace_all", False))
    block = _editable_block(session, label)
    before = block.value
    if old_content not in before:
        raise ValueError("v3_memory_replace_old_content_not_found")
    after = before.replace(old_content, new_content) if replace_all else before.replace(old_content, new_content, 1)
    _set_core_memory_block(session, block, after)
    return {"ok": True, "label": label, "operation": "replace", "chars": len(after)}, label, before, after


def _require_block_label(arguments: dict[str, Any]) -> str:
    label = _require_arg_str(arguments, "label")
    if label not in {"persona", "human", "product", "sales_strategy", "customer_intelligence"}:
        raise ValueError(f"v3_core_memory_block_not_allowed:{label}")
    return label


def _editable_block(session: V3SandboxSession, label: str) -> CoreMemoryBlock:
    block = session.core_memory_blocks.get(label)
    if block is None:
        raise ValueError(f"v3_core_memory_block_not_found:{label}")
    if block.read_only:
        raise ValueError(f"v3_core_memory_block_read_only:{label}")
    return block


def _set_core_memory_block(session: V3SandboxSession, block: CoreMemoryBlock, value: str) -> None:
    if len(value) > block.limit:
        raise ValueError(f"v3_core_memory_block_limit_exceeded:{block.label}")
    session.core_memory_blocks[block.label] = block.model_copy(update={"value": value, "updated_at": utc_now()})


def _require_arg_str(arguments: dict[str, Any], key: str, *, allow_empty: bool = False) -> str:
    value = arguments.get(key)
    if not isinstance(value, str):
        raise ValueError(f"v3_tool_argument_requires_{key}")
    if not allow_empty and not value.strip():
        raise ValueError(f"v3_tool_argument_requires_{key}")
    return value if allow_empty else value.strip()


def _core_memory_summary(session: V3SandboxSession) -> dict[str, dict[str, Any]]:
    return {
        label: {
            "chars": len(block.value),
            "limit": block.limit,
            "updated_at": block.updated_at.isoformat(),
        }
        for label, block in session.core_memory_blocks.items()
    }


def _call_llm(state: V3SandboxGraphState, *, client: TokenHubClient | None) -> V3SandboxGraphState:
    started = perf_counter()
    settings = state["settings"]
    llm_client = client or TokenHubClient(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        timeout_seconds=max(settings.llm_timeout_seconds, 90.0),
    )
    messages = _build_messages(state["session"], state["user_message"])
    event: dict[str, Any] = {
        "node": "call_llm",
        "status": "completed",
        "input": _maybe_node_io(
            state,
            {
                "message_count": len(messages),
                "current_user_message_id": state["user_message"].id,
            },
        ),
    }
    if state["debug_options"].include_prompt:
        event["messages"] = messages
    try:
        completion = llm_client.complete(messages)
        valid_initial = _is_valid_turn_output(completion.content)
        event["output"] = _maybe_node_io(
            state,
            {
                "usage": _normalize_usage(completion.usage),
                "initial_output_valid": valid_initial,
            },
        )
        if state["debug_options"].include_raw_llm_output:
            event["raw_output"] = completion.content
        if not valid_initial:
            repair_messages = [
                *messages,
                {
                    "role": "user",
                    "content": (
                        "上一次输出没有通过 backend JSON/Pydantic 校验。"
                        "请只重新输出一个 JSON object，必须包含 assistant_message、actions、"
                        "reasoning_summary、confidence。actions 必须是数组；每个 action 必须包含 "
                        "type 和 payload。不要输出 markdown、注释、空对象或额外文本。"
                    ),
                },
            ]
            repair_completion = llm_client.complete(repair_messages)
            repair_attempt: dict[str, Any] = {
                "usage": _normalize_usage(repair_completion.usage),
                "output_valid": _is_valid_turn_output(repair_completion.content),
            }
            if state["debug_options"].include_prompt:
                repair_attempt["messages"] = repair_messages
            if state["debug_options"].include_raw_llm_output:
                repair_attempt["raw_output"] = repair_completion.content
            if state["debug_options"].include_repair_attempts:
                event["repair_attempts"] = [repair_attempt]
            completion = repair_completion
    except Exception as exc:
        event["status"] = "error"
        event["duration_ms"] = _duration_ms(started)
        event["error"] = _debug_error(exc)
        _append_debug_event(state.get("debug_trace"), state["debug_options"], event)
        raise
    event["duration_ms"] = _duration_ms(started)
    _append_debug_event(state.get("debug_trace"), state["debug_options"], event)
    return {"raw_content": completion.content, "usage": completion.usage}


def _parse_actions(state: V3SandboxGraphState) -> V3SandboxGraphState:
    started = perf_counter()
    event: dict[str, Any] = {
        "node": "parse_actions",
        "status": "completed",
        "input": _maybe_node_io(
            state,
            {
                "raw_content_length": len(state["raw_content"]),
            },
        ),
    }
    try:
        parsed = _parse_json_object(state["raw_content"])
        output = V3SandboxTurnOutput.model_validate(parsed)
    except Exception as exc:
        event["status"] = "error"
        event["duration_ms"] = _duration_ms(started)
        event["error"] = _debug_error(exc)
        _append_debug_event(state.get("debug_trace"), state["debug_options"], event)
        raise
    event["duration_ms"] = _duration_ms(started)
    event["output"] = _maybe_node_io(
        state,
        {
            "action_count": len(output.actions),
            "confidence": output.confidence,
        },
    )
    if state["debug_options"].verbose:
        event["parsed_output"] = output.model_dump(mode="json")
    _append_debug_event(state.get("debug_trace"), state["debug_options"], event)
    return {
        "parsed_output": output,
        "actions": output.actions,
    }


def _apply_actions(state: V3SandboxGraphState) -> V3SandboxGraphState:
    started = perf_counter()
    session = state["session"]
    before_session = session.model_copy(deep=True)
    action_results: list[dict[str, Any]] = []
    event: dict[str, Any] = {
        "node": "apply_actions",
        "status": "completed",
        "input": _maybe_node_io(state, {"action_count": len(state["actions"])}),
    }
    try:
        for index, action in enumerate(state["actions"]):
            result = {"index": index, "type": action.type, "status": "applied", "payload": _action_payload(action)}
            try:
                _apply_action(session, action)
            except Exception as exc:
                result["status"] = "error"
                result["error"] = _debug_error(exc)
                action_results.append(result)
                raise
            action_results.append(result)
    except Exception as exc:
        event["status"] = "error"
        event["duration_ms"] = _duration_ms(started)
        event["error"] = _debug_error(exc)
        event["action_results"] = action_results
        if state["debug_options"].include_state_diff:
            event["state_diff"] = _state_diff(before_session, session)
        _append_debug_event(state.get("debug_trace"), state["debug_options"], event)
        raise
    session.updated_at = utc_now()
    event["duration_ms"] = _duration_ms(started)
    event["output"] = _maybe_node_io(
        state,
        {
            "memory_count": len(session.memory_items),
            "action_count": len(action_results),
        },
    )
    event["action_results"] = action_results
    if state["debug_options"].include_state_diff:
        event["state_diff"] = _state_diff(before_session, session)
    _append_debug_event(state.get("debug_trace"), state["debug_options"], event)
    return {"session": session}


def _return_turn(state: V3SandboxGraphState) -> V3SandboxGraphState:
    started = perf_counter()
    session = state["session"]
    assistant_message = V3SandboxMessage(
        id=f"msg_assistant_{state['turn_id']}",
        role="assistant",
        content=state["final_message"],
    )
    session.messages.append(assistant_message)
    parsed_output = {
        "assistant_message": state["final_message"],
        "tool_event_count": len(state.get("tool_events", [])),
    }
    trace_event = V3SandboxTraceEvent(
        id=f"trace_{state['turn_id']}",
        session_id=session.id,
        turn_id=state["turn_id"],
        event_type="v3_sandbox_agent_turn",
        runtime_metadata={
            **state["runtime_metadata"],
            "duration_ms": round((perf_counter() - state["started_perf"]) * 1000, 3),
            "llm_usage": state.get("usage_total", _normalize_usage(state.get("usage", {}))),
            "tool_event_count": len(state.get("tool_events", [])),
        },
        actions=[],
        tool_events=state.get("tool_events", []),
        parsed_output=parsed_output,
        debug_trace=state.get("debug_trace"),
    )
    session.trace.append(trace_event)
    session.updated_at = utc_now()
    _append_debug_event(
        state.get("debug_trace"),
        state["debug_options"],
        {
            "node": "return_turn",
            "status": "completed",
            "duration_ms": _duration_ms(started),
            "input": _maybe_node_io(state, {"assistant_message_id": assistant_message.id}),
            "output": _maybe_node_io(state, {"trace_event_id": trace_event.id, "message_count": len(session.messages)}),
        },
    )
    return {
        "session": session,
        "assistant_message": assistant_message,
        "actions": [],
        "trace_event": trace_event,
    }


def _apply_action(session: V3SandboxSession, action: AgentAction) -> None:
    payload = _action_payload(action)
    if action.type == "no_op":
        return
    if action.type == "write_memory":
        memory = MemoryItem.model_validate(payload)
        session.memory_items[memory.id] = memory
        for old_id in memory.supersedes:
            old = session.memory_items.get(old_id)
            if old is not None:
                session.memory_items[old_id] = old.model_copy(
                    update={"status": "superseded", "superseded_by": memory.id, "updated_at": utc_now()}
                )
        return
    if action.type == "update_memory_status":
        memory_id = _require_str(payload, "memory_id")
        status = _require_str(payload, "status")
        if memory_id not in session.memory_items:
            raise ValueError(f"memory_item_not_found:{memory_id}")
        updates: dict[str, Any] = {"status": status, "updated_at": utc_now()}
        superseded_by = payload.get("superseded_by")
        if isinstance(superseded_by, str) and superseded_by:
            updates["superseded_by"] = superseded_by
        session.memory_items[memory_id] = session.memory_items[memory_id].model_copy(update=updates)
        return
    if action.type == "update_working_state":
        updates = _list_updates(payload)
        session.working_state = session.working_state.model_copy(
            update={
                "product_understanding": _merge_list(
                    session.working_state.product_understanding,
                    updates.get("product_understanding", []),
                ),
                "sales_strategy": _merge_list(session.working_state.sales_strategy, updates.get("sales_strategy", [])),
                "open_questions": _merge_list(session.working_state.open_questions, updates.get("open_questions", [])),
                "current_hypotheses": _merge_list(
                    session.working_state.current_hypotheses,
                    updates.get("current_hypotheses", []),
                ),
                "correction_summary": _merge_list(
                    session.working_state.correction_summary,
                    updates.get("correction_summary", []),
                ),
                "updated_at": utc_now(),
            }
        )
        return
    if action.type == "update_customer_intelligence":
        updates = payload
        draft = session.customer_intelligence
        candidates = list(draft.candidates)
        for item in updates.get("candidates", []):
            candidate = CustomerCandidateDraft.model_validate(item)
            candidates = [existing for existing in candidates if existing.id != candidate.id]
            candidates.append(candidate)
        scoring_draft = dict(draft.scoring_draft)
        for key, value in updates.get("scoring_draft", {}).items():
            if isinstance(value, int):
                scoring_draft[key] = value
        session.customer_intelligence = draft.model_copy(
            update={
                "target_industries": _merge_list(draft.target_industries, _strings(updates.get("target_industries", []))),
                "target_roles": _merge_list(draft.target_roles, _strings(updates.get("target_roles", []))),
                "candidates": candidates,
                "ranking_reasons": _merge_list(draft.ranking_reasons, _strings(updates.get("ranking_reasons", []))),
                "scoring_draft": scoring_draft,
                "validation_signals": _merge_list(draft.validation_signals, _strings(updates.get("validation_signals", []))),
                "updated_at": utc_now(),
            }
        )
        return
    raise ValueError(f"unsupported_v3_sandbox_action:{action.type}")


def _action_payload(action: AgentAction) -> dict[str, Any]:
    nested = action.payload.get(action.type)
    if isinstance(nested, dict):
        return nested
    return action.payload


def _build_messages(session: V3SandboxSession, user_message: V3SandboxMessage) -> list[dict[str, str]]:
    active_memory = [
        item.model_dump(mode="json")
        for item in session.memory_items.values()
        if item.status not in {"rejected", "superseded"}
    ]
    inactive_memory = [
        item.model_dump(mode="json")
        for item in session.memory_items.values()
        if item.status in {"rejected", "superseded"}
    ]
    schema = {
        "assistant_message": "string",
        "actions": [
            {
                "type": "write_memory | update_memory_status | update_working_state | update_customer_intelligence | no_op",
                "payload": {
                    "write_memory": {
                        "id": "mem_x",
                        "status": "observed | inferred | hypothesis | confirmed | rejected | superseded",
                        "content": "memory text",
                        "source": "user | agent",
                        "evidence": ["short source quote"],
                        "confidence": 0.0,
                        "supersedes": ["old_memory_id"],
                        "tags": ["product | customer_intelligence | correction"],
                    },
                    "update_memory_status": {
                        "memory_id": "old_memory_id",
                        "status": "rejected | superseded | confirmed",
                        "superseded_by": "new_memory_id",
                    },
                    "update_working_state": {
                        "product_understanding": ["string"],
                        "sales_strategy": ["string"],
                        "open_questions": ["string"],
                        "current_hypotheses": ["string"],
                        "correction_summary": ["string"],
                    },
                    "update_customer_intelligence": {
                        "target_industries": ["string"],
                        "target_roles": ["string"],
                        "candidates": [
                            {
                                "id": "cand_x",
                                "name": "candidate segment",
                                "segment": "string",
                                "target_roles": ["string"],
                                "ranking_reason": "string",
                                "score": 0,
                                "validation_signals": ["string"],
                            }
                        ],
                        "ranking_reasons": ["string"],
                        "scoring_draft": {"cand_x": 0},
                        "validation_signals": ["string"],
                    },
                    "no_op": {},
                },
            }
        ],
        "reasoning_summary": "short summary, no chain-of-thought",
        "confidence": "0 to 1",
    }
    runtime_input = {
        "session_id": session.id,
        "active_memory": active_memory,
        "inactive_memory_for_correction_context_only": inactive_memory,
        "working_state": session.working_state.model_dump(mode="json"),
        "customer_intelligence": session.customer_intelligence.model_dump(mode="json"),
        "recent_messages": [message.model_dump(mode="json") for message in session.messages[-8:]],
        "current_user_message": user_message.model_dump(mode="json"),
    }
    return [
        {
            "role": "system",
            "content": (
                "你是 OpenClaw V3 Product Sales Agent sandbox runtime。"
                "你可以维护开放认知 memory、sandbox working state 和 customer intelligence draft。"
                "memory 可以是 observed、inferred、hypothesis、confirmed、rejected 或 superseded。"
                "用户纠错时，必须用 update_memory_status 将旧记忆标为 superseded 或 rejected，"
                "并用 write_memory 写入新的 observed/confirmed 记忆。"
                "不要把 rejected 或 superseded memory 当作当前事实。"
                "customer intelligence 只能是 draft/working state，不要声称已经写入 CRM 或执行外部触达。"
                "只输出单个 JSON object，不要输出 markdown、注释或额外文本。"
            ),
        },
        {
            "role": "user",
            "content": (
                "请处理本轮销售助手对话，并输出可由 backend 应用的 actions。\n"
                f"output_schema:\n{json.dumps(schema, ensure_ascii=False)}\n\n"
                f"runtime_input:\n{json.dumps(runtime_input, ensure_ascii=False)}"
            ),
        },
    ]


def _parse_json_object(content: str) -> dict[str, Any]:
    text = _strip_thinking_and_fences(content)
    decoder = json.JSONDecoder()
    last_error: json.JSONDecodeError | None = None
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError as exc:
            last_error = exc
            continue
        if not isinstance(parsed, dict):
            raise ValueError("v3_sandbox_llm_json_object_required")
        return parsed
    raise ValueError("v3_sandbox_llm_json_object_not_found") from last_error


def _is_valid_turn_output(content: str) -> bool:
    try:
        V3SandboxTurnOutput.model_validate(_parse_json_object(content))
    except (ValueError, ValidationError):
        return False
    return True


def _debug_enabled(options: V3SandboxDebugTraceOptions) -> bool:
    return any(
        (
            options.verbose,
            options.include_prompt,
            options.include_raw_llm_output,
            options.include_repair_attempts,
            options.include_node_io,
            options.include_state_diff,
        )
    )


def _new_debug_trace(options: V3SandboxDebugTraceOptions) -> dict[str, Any]:
    return {
        "version": "v3_sandbox_debug_trace_v1",
        "truncated": False,
        "options": options.model_dump(mode="json"),
        "graph": {
            "nodes": [
                "load_state",
                "compose_context",
                "call_agent_with_tools",
                "execute_tool_calls",
                "return_turn",
            ],
            "edges": [
                ["START", "load_state"],
                ["load_state", "compose_context"],
                ["compose_context", "call_agent_with_tools"],
                ["call_agent_with_tools", "execute_tool_calls"],
                ["execute_tool_calls", "call_agent_with_tools"],
                ["execute_tool_calls", "return_turn"],
                ["return_turn", "END"],
            ],
        },
        "events": [],
    }


def _append_debug_event(
    debug_trace: dict[str, Any] | None,
    options: V3SandboxDebugTraceOptions,
    event: dict[str, Any],
) -> None:
    if debug_trace is None:
        return
    event = {key: value for key, value in event.items() if value is not None}
    debug_trace.setdefault("events", []).append(event)
    _enforce_debug_trace_limit(debug_trace, options.max_bytes)


def _enforce_debug_trace_limit(debug_trace: dict[str, Any], max_bytes: int) -> None:
    if _json_size(debug_trace) <= max_bytes:
        return
    debug_trace["truncated"] = True
    for event in debug_trace.get("events", []):
        if not isinstance(event, dict):
            continue
        for key in (
            "messages",
            "raw_output",
            "repair_attempts",
            "parsed_output",
            "action_results",
            "tool_results",
            "state_diff",
            "input",
            "output",
        ):
            if key in event:
                event[key] = _summarize_debug_value(event[key])
        if _json_size(debug_trace) <= max_bytes:
            return
    if _json_size(debug_trace) > max_bytes:
        debug_trace["events"] = [
            {
                "node": "debug_trace",
                "status": "truncated",
                "message": "Debug trace exceeded max_bytes; detailed node payloads were truncated.",
            }
        ]


def _json_size(value: Any) -> int:
    return len(json.dumps(value, ensure_ascii=False, default=str).encode("utf-8"))


def _summarize_debug_value(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        return {"truncated": True, "type": "string", "length": len(value), "preview": value[:500]}
    if isinstance(value, list):
        return {"truncated": True, "type": "list", "length": len(value)}
    if isinstance(value, dict):
        return {"truncated": True, "type": "object", "keys": sorted(str(key) for key in value.keys())[:40]}
    return {"truncated": True, "type": type(value).__name__}


def _maybe_node_io(state: V3SandboxGraphState, payload: dict[str, Any]) -> dict[str, Any] | None:
    if state["debug_options"].include_node_io or state["debug_options"].verbose:
        return payload
    return None


def _duration_ms(started: float) -> float:
    return round((perf_counter() - started) * 1000, 3)


def _debug_error(exc: Exception) -> dict[str, str]:
    return {"type": type(exc).__name__, "message": str(exc)}


def _state_diff(before: V3SandboxSession, after: V3SandboxSession) -> dict[str, Any]:
    return {
        "core_memory_blocks": _core_memory_diff(before, after),
        "memory_items": _memory_diff(before, after),
        "working_state": _model_field_diff(before.working_state.model_dump(mode="json"), after.working_state.model_dump(mode="json")),
        "customer_intelligence": _model_field_diff(
            before.customer_intelligence.model_dump(mode="json"),
            after.customer_intelligence.model_dump(mode="json"),
        ),
    }


def _core_memory_diff(before: V3SandboxSession, after: V3SandboxSession) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for label in sorted(set(before.core_memory_blocks) | set(after.core_memory_blocks)):
        before_block = before.core_memory_blocks.get(label)
        after_block = after.core_memory_blocks.get(label)
        if before_block is None and after_block is not None:
            changes.append({"label": label, "change": "added", "after_value": after_block.value})
            continue
        if before_block is not None and after_block is None:
            changes.append({"label": label, "change": "removed", "before_value": before_block.value})
            continue
        if before_block is None or after_block is None:
            continue
        if before_block.value != after_block.value:
            changes.append(
                {
                    "label": label,
                    "change": "updated",
                    "before_value": before_block.value,
                    "after_value": after_block.value,
                    "before_chars": len(before_block.value),
                    "after_chars": len(after_block.value),
                }
            )
    return changes


def _memory_diff(before: V3SandboxSession, after: V3SandboxSession) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    before_items = before.memory_items
    after_items = after.memory_items
    for memory_id in sorted(set(before_items) | set(after_items)):
        before_item = before_items.get(memory_id)
        after_item = after_items.get(memory_id)
        if before_item is None and after_item is not None:
            changes.append(
                {
                    "id": memory_id,
                    "change": "added",
                    "after_status": after_item.status,
                    "after_content": after_item.content,
                    "superseded_by": after_item.superseded_by,
                }
            )
            continue
        if before_item is not None and after_item is None:
            changes.append(
                {
                    "id": memory_id,
                    "change": "removed",
                    "before_status": before_item.status,
                    "before_content": before_item.content,
                }
            )
            continue
        if before_item is None or after_item is None:
            continue
        before_dump = before_item.model_dump(mode="json")
        after_dump = after_item.model_dump(mode="json")
        changed_fields = sorted(field for field in before_dump if before_dump.get(field) != after_dump.get(field))
        if changed_fields:
            changes.append(
                {
                    "id": memory_id,
                    "change": "updated",
                    "changed_fields": changed_fields,
                    "before_status": before_item.status,
                    "after_status": after_item.status,
                    "before_content": before_item.content,
                    "after_content": after_item.content,
                    "superseded_by": after_item.superseded_by,
                }
            )
    return changes


def _model_field_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    changes: dict[str, Any] = {}
    for key in sorted(set(before) | set(after)):
        if before.get(key) != after.get(key):
            changes[key] = {"before": before.get(key), "after": after.get(key)}
    return changes


def _failed_session(
    *,
    settings: Settings,
    session: V3SandboxSession,
    user_message: V3SandboxMessage,
    turn_id: str,
    started_perf: float,
    debug_trace: dict[str, Any] | None,
    code: str,
    message: str,
) -> V3SandboxSession:
    if user_message.id not in {item.id for item in session.messages}:
        session.messages.append(user_message)
    session.trace.append(
        V3SandboxTraceEvent(
            id=f"trace_{turn_id}",
            session_id=session.id,
            turn_id=turn_id,
            event_type="v3_sandbox_agent_turn_failed",
            runtime_metadata={
                "provider": "langgraph",
                "mode": "v3_sandbox_native_tool_loop_poc",
                "graph_name": "v3_sandbox_core_memory_tool_loop_poc",
                "memory_runtime": "native_tool_loop",
                "native_function_calling": True,
                "llm_provider": settings.llm_provider,
                "llm_model": settings.llm_model,
                "duration_ms": round((perf_counter() - started_perf) * 1000, 3),
            },
            debug_trace=debug_trace,
            error={"code": code, "message": message},
        )
    )
    session.updated_at = utc_now()
    return session


def _strip_thinking_and_fences(content: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE)
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _require_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"v3_sandbox_action_requires_{key}")
    return value


def _list_updates(payload: dict[str, Any]) -> dict[str, list[str]]:
    return {
        key: _strings(payload.get(key, []))
        for key in (
            "product_understanding",
            "sales_strategy",
            "open_questions",
            "current_hypotheses",
            "correction_summary",
        )
    }


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _merge_list(existing: list[str], additions: list[str]) -> list[str]:
    result = list(existing)
    seen = set(result)
    for item in additions:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _normalize_usage(usage: dict[str, Any]) -> dict[str, int]:
    normalized: dict[str, int] = {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        value = usage.get(key)
        if isinstance(value, int) and value >= 0:
            normalized[key] = value
    return normalized


def _merge_usage(existing: dict[str, int], addition: dict[str, int]) -> dict[str, int]:
    merged = dict(existing)
    for key, value in addition.items():
        merged[key] = merged.get(key, 0) + value
    return merged
