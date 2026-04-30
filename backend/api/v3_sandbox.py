from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Body, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend.api.config import get_settings
from backend.runtime.v3_sandbox import (
    DatabaseV3SandboxStore,
    InMemoryV3SandboxStore,
    JsonFileV3SandboxStore,
    V3SandboxDebugTraceOptions,
    V3SandboxRuntimeError,
    V3SandboxReplayReport,
    V3SandboxSessionNotFound,
    V3SandboxStoreConfigError,
    run_v3_sandbox_turn,
)
from backend.runtime.v3_sandbox.schemas import (
    AgentAction,
    CustomerCandidateDraft,
    CustomerIntelligenceDraft,
    MemoryItem,
    SandboxWorkingState,
    V3SandboxMessage,
    V3SandboxSession,
    V3SandboxTraceEvent,
    utc_now,
)


router = APIRouter(prefix="/v3/sandbox", tags=["v3-sandbox"])


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateV3SandboxSessionRequest(ApiModel):
    session_id: str | None = None
    title: str = "V3 Sandbox Session"


class CreateV3SandboxTurnRequest(ApiModel):
    content: str = Field(min_length=1)
    debug_trace: V3SandboxDebugTraceOptions | None = None


class CreateV3SandboxDemoSeedRequest(ApiModel):
    scenario: str = "sales_training_correction"


AllowedV3SandboxModel = Literal["minimax-m2.5", "deepseek-v3.1", "deepseek-r1"]
AllowedV3SandboxTimeout = Literal[90, 120, 180, 300]
AllowedV3SandboxTraceMaxBytes = Literal[80_000, 200_000, 500_000]


class V3SandboxRuntimeConfigPatch(ApiModel):
    llm_model: AllowedV3SandboxModel | None = None
    llm_timeout_seconds: AllowedV3SandboxTimeout | None = None
    default_debug_trace: bool | None = None
    default_include_prompt: bool | None = None
    default_include_raw_llm_output: bool | None = None
    default_include_state_diff: bool | None = None
    replay_debug_trace: bool | None = None
    trace_max_bytes: AllowedV3SandboxTraceMaxBytes | None = None


V3SandboxStore = InMemoryV3SandboxStore | JsonFileV3SandboxStore | DatabaseV3SandboxStore

_MODEL_ALLOWLIST = ["minimax-m2.5", "deepseek-v3.1", "deepseek-r1"]
_TIMEOUT_ALLOWLIST = [90, 120, 180, 300]
_TRACE_MAX_BYTES_ALLOWLIST = [80_000, 200_000, 500_000]
_RUNTIME_OVERRIDE_KEYS = {
    "llm_model",
    "llm_timeout_seconds",
    "default_debug_trace",
    "default_include_prompt",
    "default_include_raw_llm_output",
    "default_include_state_diff",
    "replay_debug_trace",
    "trace_max_bytes",
}


def create_v3_sandbox_store() -> V3SandboxStore:
    backend = (get_settings().v3_sandbox_store_backend or "").strip().lower()
    store_path = get_settings().v3_sandbox_store_path
    if backend == "database":
        return DatabaseV3SandboxStore()
    if backend == "memory":
        return InMemoryV3SandboxStore()
    if backend == "json":
        if store_path is None:
            raise V3SandboxStoreConfigError("v3_sandbox_json_store_dir_required")
        return JsonFileV3SandboxStore(store_path)
    if backend:
        raise V3SandboxStoreConfigError(f"unsupported_v3_sandbox_store_backend:{backend}")
    if store_path is not None:
        return JsonFileV3SandboxStore(store_path)
    return InMemoryV3SandboxStore()


def _store(request: Request) -> V3SandboxStore:
    store = getattr(request.app.state, "v3_sandbox_store", None)
    if store is None:
        store = create_v3_sandbox_store()
        request.app.state.v3_sandbox_store = store
    return store


def _runtime_overrides(request: Request) -> dict[str, Any]:
    overrides = getattr(request.app.state, "v3_sandbox_runtime_overrides", None)
    if overrides is None:
        overrides = {}
        request.app.state.v3_sandbox_runtime_overrides = overrides
    return overrides


def _effective_settings(request: Request):
    settings = get_settings()
    overrides = _runtime_overrides(request)
    update: dict[str, Any] = {}
    for key in ("llm_model", "llm_timeout_seconds"):
        if key in overrides:
            update[key] = overrides[key]
    if not update:
        return settings
    return settings.model_copy(update=update)


def _runtime_debug_options(request: Request, explicit: V3SandboxDebugTraceOptions | None) -> V3SandboxDebugTraceOptions | None:
    if explicit is not None:
        return explicit
    overrides = _runtime_overrides(request)
    if not overrides.get("default_debug_trace", False):
        return None
    return V3SandboxDebugTraceOptions(
        verbose=True,
        include_prompt=bool(overrides.get("default_include_prompt", False)),
        include_raw_llm_output=bool(overrides.get("default_include_raw_llm_output", False)),
        include_repair_attempts=True,
        include_node_io=True,
        include_state_diff=bool(overrides.get("default_include_state_diff", False)),
        max_bytes=int(overrides.get("trace_max_bytes", 80_000)),
    )


def _replay_debug_options(request: Request) -> V3SandboxDebugTraceOptions | None:
    overrides = _runtime_overrides(request)
    if not overrides.get("replay_debug_trace", False):
        return None
    return V3SandboxDebugTraceOptions(
        verbose=True,
        include_prompt=bool(overrides.get("default_include_prompt", False)),
        include_raw_llm_output=bool(overrides.get("default_include_raw_llm_output", False)),
        include_repair_attempts=True,
        include_node_io=True,
        include_state_diff=bool(overrides.get("default_include_state_diff", False)),
        max_bytes=int(overrides.get("trace_max_bytes", 80_000)),
    )


def _runtime_config_response(request: Request) -> dict[str, Any]:
    settings = get_settings()
    effective = _effective_settings(request)
    overrides = dict(_runtime_overrides(request))
    return {
        "backend_status": {
            "store": _store_status(_store(request)),
            "llm_provider": effective.llm_provider,
            "llm_model": effective.llm_model,
            "llm_api_key_status": "configured" if bool(settings.llm_api_key) else "missing",
            "llm_timeout_seconds": effective.llm_timeout_seconds,
            "langfuse_enabled": settings.langfuse_enabled,
            "dev_llm_trace_enabled": settings.dev_llm_trace_enabled,
        },
        "runtime_config": {
            "llm_model": effective.llm_model,
            "llm_timeout_seconds": int(effective.llm_timeout_seconds),
            "default_debug_trace": bool(overrides.get("default_debug_trace", False)),
            "default_include_prompt": bool(overrides.get("default_include_prompt", False)),
            "default_include_raw_llm_output": bool(overrides.get("default_include_raw_llm_output", False)),
            "default_include_state_diff": bool(overrides.get("default_include_state_diff", False)),
            "replay_debug_trace": bool(overrides.get("replay_debug_trace", False)),
            "trace_max_bytes": int(overrides.get("trace_max_bytes", 80_000)),
        },
        "danger_readonly": {
            "database_url_status": "configured" if bool(settings.database_url) else "default_sqlite",
            "v3_sandbox_store_dir_status": "configured" if bool(settings.v3_sandbox_store_dir) else "not_configured",
            "llm_api_key_status": "configured" if bool(settings.llm_api_key) else "missing",
        },
        "overrides": overrides,
        "allowlists": {
            "llm_models": _MODEL_ALLOWLIST,
            "llm_timeout_seconds": _TIMEOUT_ALLOWLIST,
            "trace_max_bytes": _TRACE_MAX_BYTES_ALLOWLIST,
        },
    }


def _error_response(*, status_code: int, code: str, message: str, details: dict[str, Any] | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details or {}}},
    )


def _validation_error(exc: ValidationError) -> JSONResponse:
    return _error_response(
        status_code=422,
        code="validation_error",
        message="request body failed validation",
        details={"errors": jsonable_encoder(exc.errors())},
    )


def _store_backend_name(store: V3SandboxStore) -> str:
    if isinstance(store, DatabaseV3SandboxStore):
        return "database"
    if isinstance(store, JsonFileV3SandboxStore):
        return "json"
    return "memory"


def _store_status(store: V3SandboxStore) -> dict[str, Any]:
    backend = _store_backend_name(store)
    return {
        "backend": backend,
        "database_enabled": backend == "database",
        "json_enabled": backend == "json",
        "transition_events_supported": backend == "database",
    }


@router.get("/store")
def get_store_status(request: Request):
    return _store_status(_store(request))


@router.get("/runtime-config")
def get_runtime_config(request: Request):
    return _runtime_config_response(request)


@router.patch("/runtime-config")
def update_runtime_config(request: Request, payload: Any = Body(...)):
    try:
        parsed = V3SandboxRuntimeConfigPatch.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc)
    updates = parsed.model_dump(exclude_none=True)
    overrides = _runtime_overrides(request)
    for key, value in updates.items():
        if key in _RUNTIME_OVERRIDE_KEYS:
            overrides[key] = value
    return _runtime_config_response(request)


@router.post("/runtime-config/reset")
def reset_runtime_config(request: Request):
    _runtime_overrides(request).clear()
    return _runtime_config_response(request)


@router.post("/sessions")
def create_session(request: Request, payload: Any = Body(...)):
    try:
        parsed = CreateV3SandboxSessionRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc)
    session_id = parsed.session_id or f"v3s_{uuid4().hex[:12]}"
    session = V3SandboxSession(id=session_id, title=parsed.title)
    _store(request).create_session(session)
    return JSONResponse(status_code=201, content=jsonable_encoder({"session": session}))


@router.post("/demo-seeds")
def create_demo_seed(request: Request, payload: Any = Body(...)):
    try:
        parsed = CreateV3SandboxDemoSeedRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc)
    if parsed.scenario != "sales_training_correction":
        return _error_response(
            status_code=422,
            code="unsupported_demo_seed_scenario",
            message="unsupported demo seed scenario",
            details={"scenario": parsed.scenario},
        )
    session = _sales_training_correction_seed()
    _store(request).create_session(session)
    return JSONResponse(status_code=201, content=jsonable_encoder({"session": session, "scenario": parsed.scenario}))


@router.get("/sessions/{session_id}")
def get_session(session_id: str, request: Request):
    try:
        session = _store(request).get_session(session_id)
    except V3SandboxSessionNotFound:
        return _error_response(
            status_code=404,
            code="not_found",
            message="v3 sandbox session not found",
            details={"session_id": session_id},
        )
    return {"session": session}


@router.get("/sessions/{session_id}/trace")
def get_session_trace(session_id: str, request: Request):
    try:
        session = _store(request).get_session(session_id)
    except V3SandboxSessionNotFound:
        return _error_response(
            status_code=404,
            code="not_found",
            message="v3 sandbox session not found",
            details={"session_id": session_id},
        )
    return {"session_id": session.id, "trace": session.trace}


@router.get("/sessions/{session_id}/memory-transitions")
def get_session_memory_transitions(session_id: str, request: Request):
    store = _store(request)
    try:
        store.get_session(session_id)
    except V3SandboxSessionNotFound:
        return _error_response(
            status_code=404,
            code="not_found",
            message="v3 sandbox session not found",
            details={"session_id": session_id},
        )
    if not isinstance(store, DatabaseV3SandboxStore):
        return {
            "session_id": session_id,
            "available": False,
            "reason": "database_store_required",
            "store": _store_status(store),
            "counts": {},
            "transitions": [],
        }
    return {
        "session_id": session_id,
        "available": True,
        "reason": None,
        "store": _store_status(store),
        "counts": store.inspection_counts(session_id),
        "transitions": store.memory_transitions(session_id),
    }


@router.post("/sessions/{session_id}/turns")
def create_turn(session_id: str, request: Request, payload: Any = Body(...)):
    try:
        parsed = CreateV3SandboxTurnRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc)
    try:
        session = _store(request).get_session(session_id)
    except V3SandboxSessionNotFound:
        return _error_response(
            status_code=404,
            code="not_found",
            message="v3 sandbox session not found",
            details={"session_id": session_id},
        )
    user_message = V3SandboxMessage(
        id=f"msg_user_{uuid4().hex[:12]}",
        role="user",
        content=parsed.content,
    )
    try:
        result = run_v3_sandbox_turn(
            settings=_effective_settings(request),
            session=session,
            user_message=user_message,
            debug_options=_runtime_debug_options(request, parsed.debug_trace),
        )
    except V3SandboxRuntimeError as exc:
        if exc.session is not None:
            _store(request).save_session(exc.session)
        status_code = 503 if exc.code == "llm_runtime_unavailable" else 422
        return _error_response(
            status_code=status_code,
            code=exc.code,
            message=exc.message,
            details={"session_id": session_id},
        )
    _store(request).save_session(result.session)
    return {
        "session": result.session,
        "assistant_message": result.assistant_message,
        "actions": result.actions,
        "trace_event": result.trace_event,
    }


@router.post("/sessions/{session_id}/replay")
def replay_session(session_id: str, request: Request):
    store = _store(request)
    try:
        source_session = store.get_session(session_id)
    except V3SandboxSessionNotFound:
        return _error_response(
            status_code=404,
            code="not_found",
            message="v3 sandbox session not found",
            details={"session_id": session_id},
        )

    replay = V3SandboxSession(
        id=f"v3s_replay_{uuid4().hex[:12]}",
        title=f"Replay of {source_session.id}",
    )
    store.create_session(replay)
    report = V3SandboxReplayReport(
        status="completed",
        source_session_id=source_session.id,
        replay_session_id=replay.id,
    )
    user_messages = [message for message in source_session.messages if message.role == "user"]
    for index, source_message in enumerate(user_messages, start=1):
        replay_user_message = V3SandboxMessage(
            id=f"msg_user_replay_{index}_{uuid4().hex[:8]}",
            role="user",
            content=source_message.content,
        )
        try:
            result = run_v3_sandbox_turn(
                settings=_effective_settings(request),
                session=replay,
                user_message=replay_user_message,
                debug_options=_replay_debug_options(request),
            )
        except V3SandboxRuntimeError as exc:
            replay = exc.session or replay
            store.save_session(replay)
            report = V3SandboxReplayReport(
                status="failed",
                source_session_id=source_session.id,
                replay_session_id=replay.id,
                replayed_turns=index - 1,
                failed_turn_index=index,
                error={"code": exc.code, "message": exc.message},
            )
            return JSONResponse(
                status_code=200,
                content=jsonable_encoder({"session": replay, "replay": report}),
            )
        replay = result.session
        report = report.model_copy(update={"replayed_turns": index})
        store.save_session(replay)

    return {"session": replay, "replay": report}


def _sales_training_correction_seed() -> V3SandboxSession:
    session_id = f"v3s_seed_{uuid4().hex[:12]}"
    mem_product = MemoryItem(
        id="mem_seed_product",
        status="observed",
        content="产品是面向苏州小企业老板的线下销售管理培训",
        source="user",
        evidence=["我们做面向苏州小企业老板的销售管理培训，主要是线下课。"],
        confidence=0.96,
        tags=["product", "observed"],
    )
    mem_target_old = MemoryItem(
        id="mem_seed_target_hypothesis",
        status="superseded",
        content="可能优先找 HR 或培训负责人验证培训需求",
        source="agent",
        confidence=0.58,
        superseded_by="mem_seed_target_confirmed",
        tags=["customer_intelligence", "hypothesis"],
    )
    mem_target_new = MemoryItem(
        id="mem_seed_target_confirmed",
        status="confirmed",
        content="第一批客户应优先找小企业老板本人，而不是 HR 或培训负责人",
        source="user",
        evidence=["纠正一下，不是找 HR 或培训负责人，是找老板本人。"],
        confidence=0.98,
        supersedes=["mem_seed_target_hypothesis"],
        tags=["customer_intelligence", "correction"],
    )
    user_one = V3SandboxMessage(
        id="msg_user_seed_1",
        role="user",
        content="我们做面向苏州小企业老板的销售管理培训，主要是线下课。",
    )
    assistant_one = V3SandboxMessage(
        id="msg_assistant_seed_1",
        role="assistant",
        content="已记录产品理解，并形成第一批客户假设。",
    )
    user_two = V3SandboxMessage(
        id="msg_user_seed_2",
        role="user",
        content="纠正一下，不是找 HR 或培训负责人，是找老板本人。",
    )
    assistant_two = V3SandboxMessage(
        id="msg_assistant_seed_2",
        role="assistant",
        content="已将旧目标联系人假设标为 superseded，并确认老板本人是优先联系人。",
    )
    return V3SandboxSession(
        id=session_id,
        title="Seed: sales training correction",
        memory_items={
            mem_product.id: mem_product,
            mem_target_old.id: mem_target_old,
            mem_target_new.id: mem_target_new,
        },
        working_state=SandboxWorkingState(
            product_understanding=["面向苏州小企业老板的线下销售管理培训"],
            sales_strategy=["先围绕老板本人设计首轮访谈"],
            open_questions=["老板最关心业绩增长、团队管理还是获客转化？"],
            current_hypotheses=["老板本人更接近采购和销售管理决策"],
            correction_summary=["目标联系人已从 HR/培训负责人纠正为老板本人"],
        ),
        customer_intelligence=CustomerIntelligenceDraft(
            target_industries=["苏州本地小企业", "线下培训可触达行业"],
            target_roles=["老板本人"],
            candidates=[
                CustomerCandidateDraft(
                    id="cand_seed_owner",
                    name="苏州小企业老板",
                    segment="本地小企业",
                    target_roles=["老板本人"],
                    ranking_reason="用户明确纠正第一批客户应找老板本人，老板直接负责采购和销售管理决策。",
                    score=82,
                    validation_signals=["是否亲自管理销售团队", "是否愿意为线下培训付费"],
                )
            ],
            ranking_reasons=["老板本人拥有采购权，也直接感知销售管理痛点。"],
            scoring_draft={"cand_seed_owner": 82},
            validation_signals=["销售团队规模", "近期业绩压力", "老板是否亲自管销售"],
        ),
        messages=[user_one, assistant_one, user_two, assistant_two],
        trace=[
            V3SandboxTraceEvent(
                id="trace_seed_1",
                session_id=session_id,
                turn_id="turn_seed_1",
                event_type="v3_sandbox_demo_seed",
                runtime_metadata={"mode": "deterministic_seed", "scenario": "sales_training_correction"},
                actions=[
                    AgentAction(type="write_memory", payload=mem_product.model_dump(mode="json")),
                    AgentAction(
                        type="write_memory",
                        payload=mem_target_old.model_dump(mode="json"),
                    ),
                ],
                parsed_output={"assistant_message": assistant_one.content},
            ),
            V3SandboxTraceEvent(
                id="trace_seed_2",
                session_id=session_id,
                turn_id="turn_seed_2",
                event_type="v3_sandbox_demo_seed",
                runtime_metadata={"mode": "deterministic_seed", "scenario": "sales_training_correction"},
                actions=[
                    AgentAction(
                        type="write_memory",
                        payload=mem_target_new.model_dump(mode="json"),
                    ),
                    AgentAction(
                        type="update_memory_status",
                        payload={
                            "memory_id": mem_target_old.id,
                            "status": "superseded",
                            "superseded_by": mem_target_new.id,
                        },
                    ),
                    AgentAction(
                        type="update_customer_intelligence",
                        payload={"target_roles": ["老板本人"], "scoring_draft": {"cand_seed_owner": 82}},
                    ),
                ],
                parsed_output={"assistant_message": assistant_two.content},
            ),
        ],
        updated_at=utc_now(),
    )
