from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Body, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend.api.config import get_settings
from backend.runtime.v3_sandbox import (
    InMemoryV3SandboxStore,
    JsonFileV3SandboxStore,
    V3SandboxRuntimeError,
    V3SandboxSessionNotFound,
    run_v3_sandbox_turn,
)
from backend.runtime.v3_sandbox.schemas import V3SandboxMessage, V3SandboxSession


router = APIRouter(prefix="/v3/sandbox", tags=["v3-sandbox"])


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateV3SandboxSessionRequest(ApiModel):
    session_id: str | None = None
    title: str = "V3 Sandbox Session"


class CreateV3SandboxTurnRequest(ApiModel):
    content: str = Field(min_length=1)


def create_v3_sandbox_store() -> InMemoryV3SandboxStore | JsonFileV3SandboxStore:
    store_path = get_settings().v3_sandbox_store_path
    if store_path is not None:
        return JsonFileV3SandboxStore(store_path)
    return InMemoryV3SandboxStore()


def _store(request: Request) -> InMemoryV3SandboxStore | JsonFileV3SandboxStore:
    store = getattr(request.app.state, "v3_sandbox_store", None)
    if store is None:
        store = create_v3_sandbox_store()
        request.app.state.v3_sandbox_store = store
    return store


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
            settings=get_settings(),
            session=session,
            user_message=user_message,
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
