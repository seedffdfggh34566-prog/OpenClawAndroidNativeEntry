from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend.sales_workspace.context_pack import compile_context_pack
from backend.sales_workspace.patches import WorkspacePatchError, WorkspaceVersionConflict
from backend.sales_workspace.projection import render_markdown_projection
from backend.sales_workspace.schemas import WorkspacePatch
from backend.sales_workspace.store import InMemoryWorkspaceStore, WorkspaceNotFound


router = APIRouter(prefix="/sales-workspaces", tags=["sales-workspaces"])


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateWorkspaceRequest(ApiModel):
    workspace_id: str
    name: str
    goal: str = ""
    owner_id: str = "local_user"
    workspace_key: str = "local_default"


class ApplyWorkspacePatchRequest(ApiModel):
    patch: WorkspacePatch


class CreateContextPackRequest(ApiModel):
    task_type: str = "research_round"
    token_budget_chars: int = Field(default=6000, ge=1)
    top_n_candidates: int = Field(default=5, ge=0)


def create_sales_workspace_store() -> InMemoryWorkspaceStore:
    return InMemoryWorkspaceStore()


def _store(request: Request) -> InMemoryWorkspaceStore:
    store = getattr(request.app.state, "sales_workspace_store", None)
    if store is None:
        store = create_sales_workspace_store()
        request.app.state.sales_workspace_store = store
    return store


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


def _validation_error(exc: ValidationError, *, workspace_id: str | None = None) -> JSONResponse:
    details: dict[str, Any] = {"errors": exc.errors()}
    if workspace_id is not None:
        details["workspace_id"] = workspace_id
    return _error_response(
        status_code=422,
        code="validation_error",
        message="request body failed validation",
        details=details,
    )


def _not_found_response(workspace_id: str, *, object_type: str = "workspace") -> JSONResponse:
    return _error_response(
        status_code=404,
        code="not_found",
        message=f"{object_type} not found",
        details={"workspace_id": workspace_id, "object_type": object_type},
    )


def _patch_error_response(exc: WorkspacePatchError, *, workspace_id: str) -> JSONResponse:
    message = str(exc)
    if message.startswith("unsupported workspace operation:"):
        return _error_response(
            status_code=400,
            code="unsupported_workspace_operation",
            message=message,
            details={"workspace_id": workspace_id},
        )
    if message.startswith("unknown "):
        return _error_response(
            status_code=404,
            code="not_found",
            message=message,
            details={"workspace_id": workspace_id},
        )
    return _error_response(
        status_code=422,
        code="validation_error",
        message=message,
        details={"workspace_id": workspace_id},
    )


@router.post("")
def create_workspace(request: Request, payload: Any = Body(...)):
    try:
        parsed = CreateWorkspaceRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc)

    store = _store(request)
    try:
        store.get(parsed.workspace_id)
    except WorkspaceNotFound:
        workspace = store.create_workspace(
            workspace_id=parsed.workspace_id,
            name=parsed.name,
            goal=parsed.goal,
            owner_id=parsed.owner_id,
            workspace_key=parsed.workspace_key,
        )
        return JSONResponse(status_code=201, content=jsonable_encoder({"workspace": workspace}))

    return _error_response(
        status_code=409,
        code="workspace_already_exists",
        message="workspace already exists",
        details={"workspace_id": parsed.workspace_id},
    )


@router.get("/{workspace_id}")
def get_workspace(workspace_id: str, request: Request):
    try:
        workspace = _store(request).get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    return {"workspace": workspace}


@router.post("/{workspace_id}/patches")
def apply_patch(workspace_id: str, request: Request, payload: Any = Body(...)):
    try:
        parsed = ApplyWorkspacePatchRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc, workspace_id=workspace_id)

    patch = parsed.patch
    if patch.workspace_id != workspace_id:
        return _error_response(
            status_code=422,
            code="validation_error",
            message="path workspace_id does not match patch.workspace_id",
            details={"workspace_id": workspace_id, "patch_workspace_id": patch.workspace_id},
        )

    store = _store(request)
    try:
        updated = store.apply_patch(patch)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    except WorkspaceVersionConflict as exc:
        current_version = None
        try:
            current_version = store.get(workspace_id).workspace_version
        except WorkspaceNotFound:
            pass
        return _error_response(
            status_code=409,
            code="workspace_version_conflict",
            message="base_workspace_version does not match current workspace_version",
            details={
                "workspace_id": workspace_id,
                "current_workspace_version": current_version,
                "base_workspace_version": patch.base_workspace_version,
                "reason": str(exc),
            },
        )
    except WorkspacePatchError as exc:
        return _patch_error_response(exc, workspace_id=workspace_id)
    except ValidationError as exc:
        return _validation_error(exc, workspace_id=workspace_id)

    return {
        "workspace": updated,
        "commit": updated.commits[-1] if updated.commits else None,
        "ranking_board": updated.ranking_board,
    }


@router.get("/{workspace_id}/ranking-board/current")
def get_current_ranking_board(workspace_id: str, request: Request):
    try:
        workspace = _store(request).get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    if workspace.ranking_board is None:
        return _not_found_response(workspace_id, object_type="candidate_ranking_board")
    return {"ranking_board": workspace.ranking_board}


@router.get("/{workspace_id}/projection")
def get_projection(workspace_id: str, request: Request):
    try:
        workspace = _store(request).get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    return {
        "workspace_id": workspace.id,
        "workspace_version": workspace.workspace_version,
        "files": render_markdown_projection(workspace),
    }


@router.post("/{workspace_id}/context-packs")
def create_context_pack(workspace_id: str, request: Request, payload: Any = Body(...)):
    try:
        parsed = CreateContextPackRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc, workspace_id=workspace_id)

    try:
        workspace = _store(request).get(workspace_id)
        context_pack = compile_context_pack(
            workspace,
            task_type=parsed.task_type,
            token_budget_chars=parsed.token_budget_chars,
            top_n_candidates=parsed.top_n_candidates,
        )
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    except ValueError as exc:
        return _error_response(
            status_code=422,
            code="validation_error",
            message=str(exc),
            details={"workspace_id": workspace_id},
        )

    return {"context_pack": context_pack}
