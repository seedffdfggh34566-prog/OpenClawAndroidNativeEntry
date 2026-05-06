from __future__ import annotations

import json
import re
from time import perf_counter
from typing import Any, TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from backend.api.config import Settings
from backend.runtime.llm_client import TokenHubClient, TokenHubClientError, TokenHubCompletion, TokenHubToolCall
from backend.runtime.tokenhub_native_fc import tokenhub_native_fc_request_policy
from backend.runtime.v3_sandbox.schemas import (
    CoreMemoryBlock,
    CoreMemoryToolEvent,
    V3SandboxDebugTraceOptions,
    V3SandboxMessage,
    V3SandboxSession,
    V3SandboxTraceEvent,
    V3SandboxTurnResult,
    utc_now,
)


CORE_MEMORY_LABELS: tuple[str, ...] = ("persona", "human", "product", "sales_strategy", "customer_intelligence")
CORE_MEMORY_LINE_NUMBER_WARNING = (
    "# NOTE: Line numbers shown below (with arrows like '1→') are to help during editing. "
    "Do NOT include line number prefixes in your memory edit tool calls."
)

# Approximate context window sizes (in tokens) for models used via TokenHub.
# Values reflect the upstream allowlist's published windows; unknown models
# fall back to the conservative DEFAULT_CONTEXT_WINDOW.
_MODEL_CONTEXT_WINDOWS: dict[str, int] = {
    "minimax-m2.5": 200_000,
    "minimax-m2.7": 200_000,
    "deepseek-v4-flash": 1_000_000,
    "kimi-k2.6": 256_000,
    "glm-5.1": 200_000,
}
_DEFAULT_CONTEXT_WINDOW = 128_000
# Summarize older messages once total in-context tokens cross this fraction
# of the model context window. Letta uses ~0.9; we align with that now that
# all allowlisted models have >= 200k windows, leaving headroom for the
# assistant response and tiktoken/model tokenizer mismatch.
_CONTEXT_COMPRESSION_THRESHOLD_RATIO = 0.90


class V3SandboxRuntimeError(RuntimeError):
    def __init__(self, code: str, message: str, *, session: V3SandboxSession | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.session = session


class V3SandboxGraphState(TypedDict, total=False):
    settings: Settings
    max_steps: int
    session: V3SandboxSession
    user_message: V3SandboxMessage
    turn_id: str
    raw_content: str
    usage: dict[str, Any]
    usage_total: dict[str, int]
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
    summary_info: dict[str, Any] | None


def run_v3_sandbox_turn(
    *,
    settings: Settings,
    session: V3SandboxSession,
    user_message: V3SandboxMessage,
    client: TokenHubClient | None = None,
    debug_options: V3SandboxDebugTraceOptions | dict[str, Any] | None = None,
    max_steps: int = 16,
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
                "max_steps": max(4, min(50, max_steps)),
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

    return V3SandboxTurnResult(
        session=state["session"],
        assistant_message=state["assistant_message"],
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
    messages, summary_info = _build_tool_loop_messages(
        state["session"], state["user_message"], settings=state.get("settings"), runtime_metadata=state["runtime_metadata"]
    )
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
    return {"tool_messages": messages, "summary_info": summary_info, "session": state["session"]}


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
    # Persist the assistant's tool_calls into session.messages so the next turn
    # can see what tools were requested.
    session = state["session"]
    session.messages.append(
        V3SandboxMessage(
            id=f"msg_assistant_{state['turn_id']}_{len(session.messages)}",
            role="assistant",
            content=completion.content or "",
            tool_calls=assistant_message.get("tool_calls"),
        )
    )
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
        "session": session,
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
        # Persist tool results into session.messages so the next turn can see outcomes.
        for tr_msg in tool_result_messages:
            session.messages.append(
                V3SandboxMessage(
                    id=f"msg_tool_{state['turn_id']}_{len(session.messages)}",
                    role="tool",
                    content=tr_msg["content"],
                    tool_call_id=tr_msg["tool_call_id"],
                )
            )
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
    # Record guard metrics on every invocation so observability always sees the
    # current accumulated tool_messages token count, even when final_message is
    # already set and we are about to exit normally.
    settings = state.get("settings")
    if settings:
        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            tool_text = json.dumps(state.get("tool_messages", []), ensure_ascii=False)
            token_count = len(encoding.encode(tool_text))
            threshold = int(_context_window_for_model(settings.llm_model) * 0.95)
            # Scope: current accumulated tool_messages token count inside this turn's
            # tool loop (includes tool calls and tool results generated so far).
            state["runtime_metadata"]["guard_tool_tokens"] = token_count
            state["runtime_metadata"]["guard_tool_threshold"] = threshold
            if token_count > threshold:
                state["runtime_metadata"]["early_return_reason"] = "context_budget_exhausted"
                return "return"
        except Exception:
            pass

    if state.get("final_message"):
        return "return"
    tool_events = state.get("tool_events", [])
    max_steps = state.get("max_steps", 16)
    if len(tool_events) >= max_steps * 4:
        raise ValueError("v3_tool_loop_exhausted")
    call_count = sum(1 for message in state.get("tool_messages", []) if message.get("role") == "assistant")
    if call_count >= max_steps:
        raise ValueError("v3_tool_loop_exhausted")
    return "continue"


def _build_tool_loop_messages(
    session: V3SandboxSession,
    user_message: V3SandboxMessage,
    settings: Settings | None = None,
    runtime_metadata: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    system_lines = [
        "You are OpenClaw V3 Product Sales Agent running in a sandbox.",
        "Use native tools to maintain session-scoped core memory blocks before replying.",
        "Core memory is editable and should stay concise. Use exact memory tools for corrections.",
        "If the user corrects you, update the relevant core memory block rather than treating old text as current fact.",
        "customer_intelligence remains draft sandbox state; never claim CRM writes, outreach, export, or external actions.",
        "You must produce the final visible reply by calling send_message. Do not answer as plain assistant content.",
        "",
        "Core memory blocks (session-scoped, editable, visible across the conversation):",
    ]
    for label in CORE_MEMORY_LABELS:
        block = session.core_memory_blocks.get(label)
        if block is None:
            continue
        used = len(block.value)
        system_lines.append("")
        system_lines.append(
            f"[{block.label}] description: {block.description} | limit: {block.limit} chars | used: {used} chars"
        )
        system_lines.append(block.value if block.value else "(empty)")

    max_context_messages = 32
    system_prompt = "\n".join(system_lines)

    # Endpoint-A-lite: persistent recursive summary with cursor.
    # `historical` excludes the current user message (which is the last entry
    # in session.messages, appended by _load_state).
    historical = session.messages[:-1]
    cursor_index = _find_cursor_index(historical, session.summary_cursor_message_id)
    after_cursor = historical[cursor_index + 1:] if cursor_index is not None else historical

    summary_info: dict[str, Any] | None = None
    if settings:
        summary_info = _maybe_run_summarization(
            session=session,
            settings=settings,
            system_prompt=system_prompt,
            current_user_content=user_message.content,
            historical=historical,
            after_cursor=after_cursor,
            max_context_messages=max_context_messages,
            runtime_metadata=runtime_metadata,
        )
        # Re-derive after_cursor in case summarization advanced the cursor
        cursor_index = _find_cursor_index(historical, session.summary_cursor_message_id)
        after_cursor = historical[cursor_index + 1:] if cursor_index is not None else historical

    # Pressure warning: if total payload exceeds 75 % of context window,
    # inject a hint recommending incremental memory ops (not memory_rethink).
    if settings:
        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            _pressure_parts: list[str] = [system_prompt]
            _existing_summary = _summary_message_for_payload(session)
            if _existing_summary:
                _pressure_parts.append(_existing_summary["content"])
            _pressure_parts.extend(f"[{m.role}] {m.content}" for m in after_cursor)
            if user_message.content:
                _pressure_parts.append(user_message.content)
            _pressure_text = "\n".join(_pressure_parts)
            _pressure_tokens = len(encoding.encode(_pressure_text))
            _pressure_threshold = int(_context_window_for_model(settings.llm_model) * 0.75)
            # Scope: initial payload token count at turn start (system prompt + memory blocks
            # + existing summary + after_cursor history + current user message). Does NOT
            # include tool loop messages generated during this turn.
            if runtime_metadata is not None:
                runtime_metadata["context_pressure_tokens"] = _pressure_tokens
                runtime_metadata["context_pressure_threshold"] = _pressure_threshold
                runtime_metadata["context_pressure_triggered"] = _pressure_tokens > _pressure_threshold
            if _pressure_tokens > _pressure_threshold:
                system_lines.append("")
                system_lines.append(
                    "⚠️ Memory pressure warning: conversation context is approaching the model limit. "
                    "To avoid losing information, proactively consolidate key facts into core memory using "
                    "memory_insert, memory_replace, or core_memory_append. Avoid large reorganizations "
                    "(memory_rethink) under pressure; prefer small, precise edits."
                )
                system_prompt = "\n".join(system_lines)
        except Exception:
            pass

    summary_message = _summary_message_for_payload(session)

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
    ]
    if summary_message:
        messages.append(summary_message)

    # Convert after_cursor history to native LLM message format so tool
    # metadata (tool_calls / tool_call_id) is preserved across turns.
    for msg in after_cursor:
        if msg.role == "assistant" and msg.tool_calls:
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": msg.tool_calls,
            })
        elif msg.role == "tool":
            messages.append({
                "role": "tool",
                "tool_call_id": msg.tool_call_id,
                "content": msg.content,
            })
        else:
            messages.append({"role": msg.role, "content": msg.content})

    user_lines: list[str] = [
        "Process the current sales-agent turn.",
        (
            "First update core memory when useful, then call send_message. "
            "Use memory_insert or memory_replace for precise corrections when an exact substring anchor is available; "
            "use core_memory_append for new facts or hypotheses. "
            "Use memory_rethink only for large sweeping reorganizations of a memory block; for small precise edits, prefer memory_insert or memory_replace."
        ),
        "",
        f"Current user message:\n{user_message.content}",
    ]
    messages.append({"role": "user", "content": "\n".join(user_lines)})
    return messages, summary_info


def _context_window_for_model(model: str) -> int:
    return _MODEL_CONTEXT_WINDOWS.get(model, _DEFAULT_CONTEXT_WINDOW)


def _find_cursor_index(historical: list[V3SandboxMessage], cursor_id: str | None) -> int | None:
    """Return the index of cursor_id in historical, or None if not set or not
    found. Defensive against deleted/renumbered messages."""
    if cursor_id is None:
        return None
    for index, message in enumerate(historical):
        if message.id == cursor_id:
            return index
    return None


def _summary_message_for_payload(session: V3SandboxSession) -> dict[str, Any] | None:
    """If a persistent summary exists, package it as a role=user message for
    the LLM payload. Returns None if no summary has been generated yet."""
    if not session.context_summary:
        return None
    cursor_id = session.summary_cursor_message_id
    suffix = f" (cursor={cursor_id})" if cursor_id else ""
    content = (
        f"Note: earlier messages have been hidden from view due to conversation "
        f"memory constraints.{suffix}\nSummary of older conversation:\n"
        f"{session.context_summary}"
    )
    return {"role": "user", "content": content}


def _maybe_run_summarization(
    *,
    session: V3SandboxSession,
    settings: Settings,
    system_prompt: str,
    current_user_content: str,
    historical: list[V3SandboxMessage],
    after_cursor: list[V3SandboxMessage],
    max_context_messages: int,
    runtime_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Endpoint-A-lite: if total token count of the in-context payload
    crosses the threshold, recursively summarize (existing summary + new
    after-cursor messages beyond the recent window) and persist the result
    onto session.context_summary, advancing summary_cursor_message_id so
    that the recent window is exactly max_context_messages original
    messages after the cursor.

    Mutates session in place. Always returns a dict with ``action``:
    - ``"created"`` / ``"refreshed"``: summarization ran and persisted.
    - ``"noop_insufficient_messages"``: not enough after-cursor messages yet.
    - ``"noop_below_threshold"``: token count below compression threshold.
    - ``"noop_cursor_at_boundary"``: cursor already at the window boundary.
    - ``"failed_tiktoken"``: tiktoken import or encoding failed.
    - ``"failed_llm_empty_response"``: LLM returned empty content.
    - ``"failed_llm_exception"``: LLM call raised an exception.
    Successful actions also include ``"llm_usage"``.
    """
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
    except Exception:
        if runtime_metadata is not None:
            runtime_metadata["summarization_action"] = "failed_tiktoken"
        return {"action": "failed_tiktoken"}

    # We need at least max_context_messages + 1 after-cursor messages before
    # we can advance the cursor while keeping the recent window intact.
    if len(after_cursor) <= max_context_messages:
        if runtime_metadata is not None:
            runtime_metadata["summarization_action"] = "noop_insufficient_messages"
        return {"action": "noop_insufficient_messages"}

    # Compute approximate token count of what the LLM would see this turn
    # if we DID NOT summarize: system prompt + existing summary banner +
    # full after-cursor history + current user message.
    existing_summary_msg = _summary_message_for_payload(session)
    payload_parts: list[str] = [system_prompt]
    if existing_summary_msg:
        payload_parts.append(existing_summary_msg["content"])
    payload_parts.extend(f"[{m.role}] {m.content}" for m in after_cursor)
    if current_user_content:
        payload_parts.append(current_user_content)
    total_text = "\n".join(part for part in payload_parts if part)
    token_count = len(encoding.encode(total_text))
    # Scope: same as context_pressure_tokens (turn-start payload without tool loop).
    if runtime_metadata is not None:
        runtime_metadata["summarization_token_count"] = token_count
    threshold = int(_context_window_for_model(settings.llm_model) * _CONTEXT_COMPRESSION_THRESHOLD_RATIO)
    if token_count < threshold:
        if runtime_metadata is not None:
            runtime_metadata["summarization_action"] = "noop_below_threshold"
        return {"action": "noop_below_threshold"}

    # Messages to absorb into the summary this turn = everything in
    # after_cursor EXCEPT the most recent max_context_messages entries.
    to_absorb = after_cursor[:-max_context_messages]

    # Pairing safety: if the last absorbed message is an assistant with
    # tool_calls, we must also absorb the corresponding tool results so the
    # remaining history never contains an orphaned tool_calls block.
    if to_absorb and to_absorb[-1].role == "assistant" and to_absorb[-1].tool_calls:
        call_ids = {tc["id"] for tc in to_absorb[-1].tool_calls}
        extra: list[V3SandboxMessage] = []
        reserve_start = len(to_absorb)
        for msg in after_cursor[reserve_start:]:
            if msg.role == "tool" and msg.tool_call_id in call_ids:
                extra.append(msg)
                call_ids.discard(msg.tool_call_id)
            elif msg.role == "tool":
                break
            else:
                break
        if extra:
            to_absorb = to_absorb + extra

    if not to_absorb:
        if runtime_metadata is not None:
            runtime_metadata["summarization_action"] = "noop_cursor_at_boundary"
        return {"action": "noop_cursor_at_boundary"}

    summary_input_lines: list[str] = []
    if session.context_summary:
        summary_input_lines.append("Previous summary (authoritative for content older than the new messages below):")
        summary_input_lines.append(session.context_summary)
        summary_input_lines.append("")
    summary_input_lines.append("New messages to merge into the summary (oldest first):")
    for m in to_absorb:
        if m.role == "assistant" and m.tool_calls:
            calls_str = "; ".join(
                f"{tc['function']['name']}({tc['function']['arguments']})"
                for tc in m.tool_calls
            )
            summary_input_lines.append(f"[{m.role}] {m.content or ''} | tool_calls: {calls_str}")
        else:
            summary_input_lines.append(f"[{m.role}] {m.content}")
    summary_input = "\n".join(summary_input_lines)

    summary_prompt = (
        "You are summarizing the older portion of a conversation between a "
        "salesperson (the user — they sell a product/service via OpenClaw) "
        "and the V3 sales-agent assistant. The seller is using the agent to "
        "clarify their own product and identify candidate customer leads.\n\n"
        "Compress conversational flow but PRESERVE VERBATIM:\n"
        "- The seller's exact wording about what they sell (positioning, "
        "capabilities, constraints, pricing tiers, units of measurement)\n"
        "- Numbers the seller mentioned (prices, headcount, dates, market size, "
        "deal sizes)\n"
        "- Names the seller mentioned (competitors, partners, channels, "
        "candidate leads)\n"
        "- The seller's stated constraints, hesitations, and explicit corrections "
        "to the agent's prior interpretations\n"
        "- The seller's description of the ideal customer profile (industry, "
        "role, geography, signals)\n\n"
        "If a previous summary is provided, treat it as authoritative for content "
        "older than the new messages, and merge the new messages into it.\n\n"
        "Output: 1-3 sentences for narrative continuity, followed by a "
        "\"Key facts:\" bullet list of preserved verbatim items.\n\n"
        f"{summary_input}\n\nMerged summary:"
    )
    try:
        client = TokenHubClient(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            timeout_seconds=settings.llm_summary_timeout_seconds,
        )
        completion = client.complete_with_tools(
            messages=[{"role": "user", "content": summary_prompt}],
            tools=[],
            tool_choice="none",
            model_policy=tokenhub_native_fc_request_policy(settings.llm_model, "auto"),
        )
        summary = completion.content.strip() if completion.content else ""
        if not summary:
            if runtime_metadata is not None:
                runtime_metadata["summarization_action"] = "failed_llm_empty_response"
            return {"action": "failed_llm_empty_response"}
        usage = _normalize_usage(completion.usage)
    except Exception:
        if runtime_metadata is not None:
            runtime_metadata["summarization_action"] = "failed_llm_exception"
        return {"action": "failed_llm_exception"}

    action = "created" if session.summary_recursion_count == 0 else "refreshed"
    session.context_summary = summary
    session.summary_cursor_message_id = to_absorb[-1].id
    # NOTE: summary_recursion_count is observability-only. It is exposed in
    # trace metadata so /lab can show how many compactions a session has
    # undergone, but it does NOT trigger any hard-refresh or gamma-style
    # periodic reset. That mechanism was evaluated and rejected (not industry
    # standard, does not fundamentally solve recursive degradation, conflicts
    # with the recursive architecture).
    session.summary_recursion_count += 1

    if runtime_metadata is not None:
        runtime_metadata["summarization_action"] = action

    return {
        "action": action,
        "llm_usage": usage,
    }


def _core_memory_tools() -> list[dict[str, Any]]:
    labels = list(CORE_MEMORY_LABELS)
    return [
        {
            "type": "function",
            "function": {
                "name": "core_memory_append",
                "description": (
                    "Append concise content to the end of a core memory block.\n\n"
                    "Use this for new observations, hypotheses, or facts that don't have a precise anchor "
                    "to attach to. The new text is added on a new line at the bottom of the block.\n\n"
                    "WARNING: When the block contents are shown to you, the block text is rendered raw. "
                    "Do NOT include any line-number prefixes (e.g. 'Line 3:') or line-number warning banners "
                    "in the `content` argument. Pass only the raw text you want to append.\n\n"
                    "Args:\n"
                    "  label: Which core memory block to append to.\n"
                    "  content: Text to append.\n\n"
                    "Examples:\n"
                    "  label='human', content='User is the head of growth at Acme.'\n"
                    "  label='product', content='(inferred) Pricing tiers above 50 seats require sales contact.'"
                ),
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
                "description": (
                    "Insert content immediately after an exact substring anchor inside a core memory block.\n\n"
                    "`insert_after` is matched as a literal substring (whitespace and newlines included) "
                    "against the block's raw text. Insertion happens immediately after the LAST character "
                    "of the first match. If the anchor is not found, the call fails.\n\n"
                    "WARNING: When the block contents are shown to you, the block text is rendered raw. "
                    "Do NOT include any line-number prefixes (e.g. 'Line 3:') or line-number warning banners "
                    "in either `insert_after` or `content`. Pass only the raw text from the block.\n\n"
                    "Args:\n"
                    "  label: Which core memory block to edit.\n"
                    "  insert_after: An exact substring that already appears in the block.\n"
                    "  content: The text to insert.\n\n"
                    "Examples:\n"
                    "  label='human', insert_after='works at Acme', content=' (head of growth)'"
                ),
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
                "description": (
                    "Replace exact text inside a core memory block.\n\n"
                    "`old_content` MUST appear EXACTLY ONCE in the block (whitespace and newlines included). "
                    "If it does not appear at all, or appears more than once, the call will fail. "
                    "To replace text that appears multiple times, expand `old_content` with more surrounding "
                    "context until it becomes unique.\n\n"
                    "WARNING: When the block contents are shown to you, the block text is rendered raw. "
                    "Do NOT include any line-number prefixes (e.g. 'Line 3:') or line-number warning banners "
                    "in either `old_content` or `new_content`. Pass only the raw text from the block.\n\n"
                    "Args:\n"
                    "  label: Which core memory block to edit.\n"
                    "  old_content: The exact substring to replace. Must be unique within the block.\n"
                    "  new_content: The replacement text. May be empty (use to delete `old_content`).\n\n"
                    "Examples:\n"
                    "  label='human', old_content='role: head of growth', new_content='role: VP of growth'\n\n"
                    "Failure modes:\n"
                    "  - not found: error 'v3_memory_replace_old_content_not_found'.\n"
                    "  - multiple matches: error 'v3_memory_replace_old_content_not_unique' lists the "
                    "1-indexed line numbers where each match starts; expand `old_content` with surrounding "
                    "context until it becomes unique."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string", "enum": labels},
                        "old_content": {"type": "string", "minLength": 1},
                        "new_content": {"type": "string"},
                    },
                    "required": ["label", "old_content", "new_content"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "memory_rethink",
                "description": (
                    "Completely rewrite the contents of a core memory block. "
                    "Use this tool to make large sweeping changes (e.g. when you want to condense, reorganize, "
                    "or merge information into the memory block). Do NOT use this tool for small precise edits "
                    "(e.g. add or remove a line, replace a specific string, etc). For small edits, use memory_replace.\n\n"
                    "WARNING: When the block contents are shown to you, the block text is rendered raw. "
                    "Do NOT include any line-number prefixes (e.g. 'Line 3:') or line-number warning banners "
                    "in the `new_memory` argument. Pass only the raw text you want to store.\n\n"
                    "Args:\n"
                    "  label: Which core memory block to rewrite.\n"
                    "  new_memory: The new complete contents of the block.\n\n"
                    "Examples:\n"
                    "  label='product', new_memory='Product: OpenClaw sales management training. Target: SMB owners in Suzhou. Pricing: offline courses, contact for quote.'"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string", "enum": labels},
                        "new_memory": {"type": "string", "minLength": 1},
                    },
                    "required": ["label", "new_memory"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "send_message",
                "description": (
                    "Send the final visible assistant reply to the user. "
                    "This MUST be the final tool call in a turn — no other tool calls are allowed after it. "
                    "Use this to deliver the assistant message you want the user to see."
                ),
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
        elif tool_name == "memory_rethink":
            result, block_label, before, after = _tool_memory_rethink(session, arguments)
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
    if bool(re.search(r"\nLine \d+: ", content)):
        raise ValueError(
            "content contains a line number prefix, which is not allowed. "
            "Do not include line numbers when calling memory tools (line numbers are for display purposes only)."
        )
    if CORE_MEMORY_LINE_NUMBER_WARNING in content:
        raise ValueError(
            "content contains a line number warning, which is not allowed. "
            "Do not include line number information when calling memory tools (line numbers are for display purposes only)."
        )
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
    if bool(re.search(r"\nLine \d+: ", content)):
        raise ValueError(
            "content contains a line number prefix, which is not allowed. "
            "Do not include line numbers when calling memory tools (line numbers are for display purposes only)."
        )
    if CORE_MEMORY_LINE_NUMBER_WARNING in content:
        raise ValueError(
            "content contains a line number warning, which is not allowed. "
            "Do not include line number information when calling memory tools (line numbers are for display purposes only)."
        )
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
    if bool(re.search(r"\nLine \d+: ", new_content)):
        raise ValueError(
            "new_content contains a line number prefix, which is not allowed. "
            "Do not include line numbers when calling memory tools (line numbers are for display purposes only)."
        )
    if CORE_MEMORY_LINE_NUMBER_WARNING in new_content:
        raise ValueError(
            "new_content contains a line number warning, which is not allowed. "
            "Do not include line number information when calling memory tools (line numbers are for display purposes only)."
        )
    block = _editable_block(session, label)
    before = block.value
    positions = _find_all_occurrences(before, old_content)
    if not positions:
        raise ValueError("v3_memory_replace_old_content_not_found")
    if len(positions) > 1:
        line_numbers = sorted(_line_number_at(before, position) for position in positions)
        raise ValueError(
            "v3_memory_replace_old_content_not_unique: "
            f"matches at line(s) {line_numbers}; "
            "expand 'old_content' with more surrounding context so it appears exactly once."
        )
    position = positions[0]
    after = before[:position] + new_content + before[position + len(old_content):]
    _set_core_memory_block(session, block, after)
    return {"ok": True, "label": label, "operation": "replace", "chars": len(after)}, label, before, after


def _tool_memory_rethink(
    session: V3SandboxSession,
    arguments: dict[str, Any],
) -> tuple[dict[str, Any], str, str, str]:
    label = _require_block_label(arguments)
    new_memory = _require_arg_str(arguments, "new_memory")
    if bool(re.search(r"\nLine \d+: ", new_memory)):
        raise ValueError(
            "new_memory contains a line number prefix, which is not allowed. "
            "Do not include line numbers when calling memory tools (line numbers are for display purposes only)."
        )
    if CORE_MEMORY_LINE_NUMBER_WARNING in new_memory:
        raise ValueError(
            "new_memory contains a line number warning, which is not allowed. "
            "Do not include line number information when calling memory tools (line numbers are for display purposes only)."
        )
    block = _editable_block(session, label)
    before = block.value
    after = new_memory
    _set_core_memory_block(session, block, after)
    return {"ok": True, "label": label, "operation": "rethink", "chars": len(after)}, label, before, after


def _find_all_occurrences(haystack: str, needle: str) -> list[int]:
    if not needle:
        return []
    positions: list[int] = []
    start = 0
    while True:
        index = haystack.find(needle, start)
        if index < 0:
            break
        positions.append(index)
        start = index + len(needle)
    return positions


def _line_number_at(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def _require_block_label(arguments: dict[str, Any]) -> str:
    label = _require_arg_str(arguments, "label")
    if label not in CORE_MEMORY_LABELS:
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


def _return_turn(state: V3SandboxGraphState) -> V3SandboxGraphState:
    started = perf_counter()
    session = state["session"]
    final_message = state.get("final_message", "")
    if not final_message:
        final_message = "（Agent 在本轮执行了多个内部操作，但未发送最终回复。）"
    # Find the last assistant message (added by _call_agent_with_tools) and
    # update its content with the final send_message text. Tool results were
    # appended after it by _execute_tool_calls, so messages[-1] may be a tool.
    last_assistant_index: int | None = None
    for i in range(len(session.messages) - 1, -1, -1):
        if session.messages[i].role == "assistant":
            last_assistant_index = i
            break

    if last_assistant_index is not None:
        last = session.messages[last_assistant_index]
        if not last.content.strip():
            session.messages[last_assistant_index] = V3SandboxMessage(
                id=last.id,
                role="assistant",
                content=final_message,
                tool_calls=last.tool_calls,
                created_at=last.created_at,
            )
            assistant_message = session.messages[last_assistant_index]
        else:
            assistant_message = V3SandboxMessage(
                id=f"msg_assistant_{state['turn_id']}_final",
                role="assistant",
                content=final_message,
            )
            session.messages.append(assistant_message)
    else:
        assistant_message = V3SandboxMessage(
            id=f"msg_assistant_{state['turn_id']}_final",
            role="assistant",
            content=final_message,
        )
        session.messages.append(assistant_message)
    parsed_output = {
        "assistant_message": final_message,
        "tool_event_count": len(state.get("tool_events", [])),
    }
    summary_info = state.get("summary_info")
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
            "context_summary_present": bool(session.context_summary),
            "context_summary_chars": len(session.context_summary) if session.context_summary else 0,
            "summary_cursor_message_id": session.summary_cursor_message_id,
            "summary_recursion_count": session.summary_recursion_count,
            "summary_action": summary_info["action"] if summary_info else "noop_no_settings",
            "summary_llm_usage": summary_info.get("llm_usage") if summary_info else None,
        },
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
        "trace_event": trace_event,
    }


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
