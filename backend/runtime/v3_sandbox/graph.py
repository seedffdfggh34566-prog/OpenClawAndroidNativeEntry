from __future__ import annotations

import json
import re
from time import perf_counter
from typing import Any, TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from pydantic import ValidationError

from backend.api.config import Settings
from backend.runtime.llm_client import TokenHubClient, TokenHubClientError
from backend.runtime.v3_sandbox.schemas import (
    AgentAction,
    CustomerCandidateDraft,
    MemoryItem,
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
    parsed_output: V3SandboxTurnOutput
    actions: list[AgentAction]
    runtime_metadata: dict[str, Any]
    assistant_message: V3SandboxMessage
    trace_event: V3SandboxTraceEvent
    started_perf: float


def run_v3_sandbox_turn(
    *,
    settings: Settings,
    session: V3SandboxSession,
    user_message: V3SandboxMessage,
    client: TokenHubClient | None = None,
) -> V3SandboxTurnResult:
    graph = _build_graph(client=client)
    turn_id = f"turn_{uuid4().hex[:12]}"
    runtime_session = session.model_copy(deep=True)
    started_perf = perf_counter()
    try:
        state = graph.invoke(
            {
                "settings": settings,
                "session": runtime_session,
                "user_message": user_message,
                "turn_id": turn_id,
                "started_perf": started_perf,
            }
        )
    except TokenHubClientError as exc:
        failed_session = _failed_session(
            settings=settings,
            session=runtime_session,
            user_message=user_message,
            turn_id=turn_id,
            started_perf=started_perf,
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
    graph.add_node("call_llm", lambda state: _call_llm(state, client=client))
    graph.add_node("parse_actions", _parse_actions)
    graph.add_node("apply_actions", _apply_actions)
    graph.add_node("return_turn", _return_turn)
    graph.add_edge(START, "load_state")
    graph.add_edge("load_state", "call_llm")
    graph.add_edge("call_llm", "parse_actions")
    graph.add_edge("parse_actions", "apply_actions")
    graph.add_edge("apply_actions", "return_turn")
    graph.add_edge("return_turn", END)
    return graph.compile()


def _load_state(state: V3SandboxGraphState) -> V3SandboxGraphState:
    session = state["session"]
    user_message = state["user_message"]
    session.messages.append(user_message)
    session.updated_at = utc_now()
    return {
        "session": session,
        "runtime_metadata": {
            "provider": "langgraph",
            "mode": "v3_sandbox_memory_native_poc",
            "graph_name": "v3_sandbox_runtime_poc",
            "llm_provider": state["settings"].llm_provider,
            "llm_model": state["settings"].llm_model,
            "turn_id": state["turn_id"],
        },
    }


def _call_llm(state: V3SandboxGraphState, *, client: TokenHubClient | None) -> V3SandboxGraphState:
    settings = state["settings"]
    llm_client = client or TokenHubClient(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        timeout_seconds=max(settings.llm_timeout_seconds, 90.0),
    )
    messages = _build_messages(state["session"], state["user_message"])
    completion = llm_client.complete(messages)
    if not _is_valid_turn_output(completion.content):
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
        completion = llm_client.complete(repair_messages)
    return {"raw_content": completion.content, "usage": completion.usage}


def _parse_actions(state: V3SandboxGraphState) -> V3SandboxGraphState:
    parsed = _parse_json_object(state["raw_content"])
    output = V3SandboxTurnOutput.model_validate(parsed)
    return {
        "parsed_output": output,
        "actions": output.actions,
    }


def _apply_actions(state: V3SandboxGraphState) -> V3SandboxGraphState:
    session = state["session"]
    for action in state["actions"]:
        _apply_action(session, action)
    session.updated_at = utc_now()
    return {"session": session}


def _return_turn(state: V3SandboxGraphState) -> V3SandboxGraphState:
    output = state["parsed_output"]
    session = state["session"]
    assistant_message = V3SandboxMessage(
        id=f"msg_assistant_{state['turn_id']}",
        role="assistant",
        content=output.assistant_message,
    )
    session.messages.append(assistant_message)
    trace_event = V3SandboxTraceEvent(
        id=f"trace_{state['turn_id']}",
        session_id=session.id,
        turn_id=state["turn_id"],
        event_type="v3_sandbox_agent_turn",
        runtime_metadata={
            **state["runtime_metadata"],
            "duration_ms": round((perf_counter() - state["started_perf"]) * 1000, 3),
            "llm_usage": _normalize_usage(state.get("usage", {})),
            "confidence": output.confidence,
            "reasoning_summary": output.reasoning_summary,
        },
        actions=state["actions"],
        parsed_output=output.model_dump(mode="json"),
    )
    session.trace.append(trace_event)
    session.updated_at = utc_now()
    return {
        "session": session,
        "assistant_message": assistant_message,
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


def _failed_session(
    *,
    settings: Settings,
    session: V3SandboxSession,
    user_message: V3SandboxMessage,
    turn_id: str,
    started_perf: float,
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
                "mode": "v3_sandbox_memory_native_poc",
                "graph_name": "v3_sandbox_runtime_poc",
                "llm_provider": settings.llm_provider,
                "llm_model": settings.llm_model,
                "duration_ms": round((perf_counter() - started_perf) * 1000, 3),
            },
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
