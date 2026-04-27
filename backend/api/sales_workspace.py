from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Body, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend.api.config import get_settings
from backend.sales_workspace.context_pack import compile_context_pack
from backend.sales_workspace.draft_reviews import (
    DraftReviewNotFound,
    InMemoryDraftReviewStore,
    JsonFileDraftReviewStore,
    WorkspacePatchDraftApplyResult,
    WorkspacePatchDraftPreview,
    WorkspacePatchDraftReview,
    WorkspacePatchDraftReviewDecision,
    draft_review_id_for_draft,
)
from backend.sales_workspace.patches import WorkspacePatchError, WorkspaceVersionConflict, apply_workspace_patch
from backend.sales_workspace.projection import render_markdown_projection
from backend.sales_workspace.repository import PostgresDraftReviewStore, PostgresWorkspaceStore
from backend.sales_workspace.schemas import WorkspacePatch, utc_now
from backend.sales_workspace.store import InMemoryWorkspaceStore, JsonFileWorkspaceStore, WorkspaceNotFound
from backend.runtime.sales_workspace_patchdraft import (
    WorkspacePatchDraft,
    generate_deterministic_workspace_patch_draft,
    materialize_workspace_patch,
)


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


class RuntimePatchDraftPrototypeRequest(ApiModel):
    base_workspace_version: int = Field(ge=0)
    instruction: str = ""


class ApplyRuntimePatchDraftRequest(ApiModel):
    patch_draft: WorkspacePatchDraft


class CreateDraftReviewRequest(ApiModel):
    patch_draft: WorkspacePatchDraft


class ReviewDraftReviewRequest(ApiModel):
    decision: Literal["accept", "reject"]
    reviewed_by: str = "android_demo_user"
    comment: str = ""
    client: str = "api"


class ApplyDraftReviewRequest(ApiModel):
    requested_by: str = "android_demo_user"


class RejectDraftReviewRequest(ApiModel):
    rejected_by: str = "android_demo_user"
    reason: str = ""


def _sales_workspace_store_backend() -> str:
    settings = get_settings()
    if settings.sales_workspace_store_backend:
        return settings.sales_workspace_store_backend.strip().lower()
    if settings.sales_workspace_store_path is not None:
        return "json"
    return "memory"


def create_sales_workspace_store() -> InMemoryWorkspaceStore | JsonFileWorkspaceStore | PostgresWorkspaceStore:
    settings = get_settings()
    backend = _sales_workspace_store_backend()
    if backend == "postgres":
        return PostgresWorkspaceStore()
    if backend == "json":
        store_path = settings.sales_workspace_store_path
        if store_path is None:
            raise ValueError("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR is required for json store backend")
        return JsonFileWorkspaceStore(store_path)
    if backend == "memory":
        return InMemoryWorkspaceStore()
    raise ValueError(f"unsupported sales workspace store backend: {backend}")


def create_draft_review_store() -> InMemoryDraftReviewStore | JsonFileDraftReviewStore | PostgresDraftReviewStore:
    backend = _sales_workspace_store_backend()
    if backend == "postgres":
        return PostgresDraftReviewStore()
    store_path = get_settings().sales_workspace_store_path
    if backend == "json" and store_path is not None:
        return JsonFileDraftReviewStore(store_path)
    if backend == "json":
        raise ValueError("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR is required for json store backend")
    return InMemoryDraftReviewStore()


def _store(request: Request) -> InMemoryWorkspaceStore | JsonFileWorkspaceStore | PostgresWorkspaceStore:
    store = getattr(request.app.state, "sales_workspace_store", None)
    if store is None:
        store = create_sales_workspace_store()
        request.app.state.sales_workspace_store = store
    return store


def _draft_review_store(request: Request) -> InMemoryDraftReviewStore | JsonFileDraftReviewStore | PostgresDraftReviewStore:
    store = getattr(request.app.state, "sales_workspace_draft_review_store", None)
    if store is None:
        store = create_draft_review_store()
        request.app.state.sales_workspace_draft_review_store = store
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


def _draft_review_not_found_response(workspace_id: str, draft_review_id: str) -> JSONResponse:
    return _error_response(
        status_code=404,
        code="not_found",
        message="draft review not found",
        details={
            "workspace_id": workspace_id,
            "draft_review_id": draft_review_id,
            "object_type": "draft_review",
        },
    )


def _draft_review_state_conflict_response(
    *,
    workspace_id: str,
    draft_review: WorkspacePatchDraftReview,
    action: str,
) -> JSONResponse:
    code = "draft_review_expired" if draft_review.status == "expired" else "draft_review_state_conflict"
    return _error_response(
        status_code=409,
        code=code,
        message=f"draft review in status {draft_review.status} cannot be {action}",
        details={
            "workspace_id": workspace_id,
            "draft_review_id": draft_review.id,
            "status": draft_review.status,
            "action": action,
        },
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


def _patchdraft_validation_error(exc: ValidationError, *, workspace_id: str) -> JSONResponse:
    return _error_response(
        status_code=422,
        code="patchdraft_validation_error",
        message="runtime WorkspacePatchDraft failed validation",
        details={"workspace_id": workspace_id, "errors": jsonable_encoder(exc.errors())},
    )


def _workspace_version_conflict_response(
    exc: WorkspaceVersionConflict,
    *,
    workspace_id: str,
    current_workspace_version: int | None,
    base_workspace_version: int,
) -> JSONResponse:
    return _error_response(
        status_code=409,
        code="workspace_version_conflict",
        message="base_workspace_version does not match current workspace_version",
        details={
            "workspace_id": workspace_id,
            "current_workspace_version": current_workspace_version,
            "base_workspace_version": base_workspace_version,
            "reason": str(exc),
        },
    )


def _draft_review_version_conflict_response(
    *,
    workspace_id: str,
    draft_review: WorkspacePatchDraftReview,
    current_workspace_version: int | None,
) -> JSONResponse:
    return _error_response(
        status_code=409,
        code="workspace_version_conflict",
        message="draft review base_workspace_version does not match current workspace_version",
        details={
            "workspace_id": workspace_id,
            "draft_review_id": draft_review.id,
            "current_workspace_version": current_workspace_version,
            "base_workspace_version": draft_review.base_workspace_version,
        },
    )


def _ranking_impact_summary(ranking_board: Any) -> dict[str, str | int | None]:
    ranked_items = getattr(ranking_board, "ranked_items", None) or []
    if not ranked_items:
        return {"top_candidate_id": None, "top_candidate_name": None, "top_candidate_rank": None}
    top_item = ranked_items[0]
    return {
        "top_candidate_id": top_item.candidate_id,
        "top_candidate_name": top_item.candidate_name,
        "top_candidate_rank": top_item.rank,
    }


def _expired_review(draft_review: WorkspacePatchDraftReview) -> WorkspacePatchDraftReview:
    return draft_review.model_copy(
        update={
            "status": "expired",
            "updated_at": utc_now(),
            "apply_result": WorkspacePatchDraftApplyResult(
                status="failed",
                error_code="workspace_version_conflict",
                error_message="base_workspace_version does not match current workspace_version",
                failed_at=utc_now(),
            ),
        }
    )


def _failed_apply_review(
    draft_review: WorkspacePatchDraftReview,
    *,
    error_code: str,
    error_message: str,
) -> WorkspacePatchDraftReview:
    return draft_review.model_copy(
        update={
            "updated_at": utc_now(),
            "apply_result": WorkspacePatchDraftApplyResult(
                status="failed",
                error_code=error_code,
                error_message=error_message,
                failed_at=utc_now(),
            ),
        }
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
        return _workspace_version_conflict_response(
            exc,
            workspace_id=workspace_id,
            current_workspace_version=current_version,
            base_workspace_version=patch.base_workspace_version,
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


@router.post("/{workspace_id}/runtime/patch-drafts/prototype")
def apply_runtime_patchdraft_prototype(workspace_id: str, request: Request, payload: Any = Body(...)):
    try:
        parsed = RuntimePatchDraftPrototypeRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc, workspace_id=workspace_id)

    store = _store(request)
    try:
        workspace = store.get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)

    try:
        patch_draft = generate_deterministic_workspace_patch_draft(
            workspace,
            base_workspace_version=parsed.base_workspace_version,
            instruction=parsed.instruction,
        )
        patch = materialize_workspace_patch(patch_draft)
    except ValidationError as exc:
        return _patchdraft_validation_error(exc, workspace_id=workspace_id)

    try:
        updated = store.apply_patch(patch)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    except WorkspaceVersionConflict as exc:
        return _workspace_version_conflict_response(
            exc,
            workspace_id=workspace_id,
            current_workspace_version=workspace.workspace_version,
            base_workspace_version=patch.base_workspace_version,
        )
    except WorkspacePatchError as exc:
        return _patch_error_response(exc, workspace_id=workspace_id)
    except ValidationError as exc:
        return _patchdraft_validation_error(exc, workspace_id=workspace_id)

    return {
        "patch_draft": patch_draft,
        "patch": patch,
        "workspace": updated,
        "commit": updated.commits[-1] if updated.commits else None,
        "ranking_board": updated.ranking_board,
    }


@router.post("/{workspace_id}/runtime/patch-drafts/prototype/preview")
def preview_runtime_patchdraft_prototype(workspace_id: str, request: Request, payload: Any = Body(...)):
    try:
        parsed = RuntimePatchDraftPrototypeRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc, workspace_id=workspace_id)

    try:
        workspace = _store(request).get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)

    try:
        patch_draft = generate_deterministic_workspace_patch_draft(
            workspace,
            base_workspace_version=parsed.base_workspace_version,
            instruction=parsed.instruction,
        )
        patch = materialize_workspace_patch(patch_draft)
        preview_workspace = apply_workspace_patch(workspace, patch)
    except WorkspaceVersionConflict as exc:
        return _workspace_version_conflict_response(
            exc,
            workspace_id=workspace_id,
            current_workspace_version=workspace.workspace_version,
            base_workspace_version=parsed.base_workspace_version,
        )
    except WorkspacePatchError as exc:
        return _patch_error_response(exc, workspace_id=workspace_id)
    except ValidationError as exc:
        return _patchdraft_validation_error(exc, workspace_id=workspace_id)

    return {
        "patch_draft": patch_draft,
        "patch": patch,
        "preview_workspace_version": preview_workspace.workspace_version,
        "preview_ranking_board": preview_workspace.ranking_board,
        "would_mutate": False,
    }


@router.post("/{workspace_id}/runtime/patch-drafts/prototype/apply")
def apply_reviewed_runtime_patchdraft_prototype(workspace_id: str, request: Request, payload: Any = Body(...)):
    try:
        parsed = ApplyRuntimePatchDraftRequest.model_validate(payload)
    except ValidationError as exc:
        return _patchdraft_validation_error(exc, workspace_id=workspace_id)

    patch_draft = parsed.patch_draft
    if patch_draft.workspace_id != workspace_id:
        return _error_response(
            status_code=422,
            code="validation_error",
            message="path workspace_id does not match patch_draft.workspace_id",
            details={"workspace_id": workspace_id, "patch_draft_workspace_id": patch_draft.workspace_id},
        )

    store = _store(request)
    try:
        workspace = store.get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)

    try:
        patch = materialize_workspace_patch(patch_draft)
        updated = store.apply_patch(patch)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    except WorkspaceVersionConflict as exc:
        return _workspace_version_conflict_response(
            exc,
            workspace_id=workspace_id,
            current_workspace_version=workspace.workspace_version,
            base_workspace_version=patch_draft.base_workspace_version,
        )
    except WorkspacePatchError as exc:
        return _patch_error_response(exc, workspace_id=workspace_id)
    except ValidationError as exc:
        return _patchdraft_validation_error(exc, workspace_id=workspace_id)

    return {
        "patch_draft": patch_draft,
        "patch": patch,
        "workspace": updated,
        "commit": updated.commits[-1] if updated.commits else None,
        "ranking_board": updated.ranking_board,
    }


@router.post("/{workspace_id}/draft-reviews")
def create_draft_review(workspace_id: str, request: Request, payload: Any = Body(...)):
    try:
        parsed = CreateDraftReviewRequest.model_validate(payload)
    except ValidationError as exc:
        return _patchdraft_validation_error(exc, workspace_id=workspace_id)

    patch_draft = parsed.patch_draft
    if patch_draft.workspace_id != workspace_id:
        return _error_response(
            status_code=422,
            code="validation_error",
            message="path workspace_id does not match patch_draft.workspace_id",
            details={"workspace_id": workspace_id, "patch_draft_workspace_id": patch_draft.workspace_id},
        )

    try:
        workspace = _store(request).get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)

    try:
        patch = materialize_workspace_patch(patch_draft)
        preview_workspace = apply_workspace_patch(workspace, patch)
    except WorkspaceVersionConflict as exc:
        return _workspace_version_conflict_response(
            exc,
            workspace_id=workspace_id,
            current_workspace_version=workspace.workspace_version,
            base_workspace_version=patch_draft.base_workspace_version,
        )
    except WorkspacePatchError as exc:
        return _patch_error_response(exc, workspace_id=workspace_id)
    except ValidationError as exc:
        return _patchdraft_validation_error(exc, workspace_id=workspace_id)

    draft_review = WorkspacePatchDraftReview(
        id=draft_review_id_for_draft(patch_draft.id),
        workspace_id=workspace_id,
        draft=patch_draft,
        base_workspace_version=patch_draft.base_workspace_version,
        created_by=patch_draft.author,
        instruction=patch_draft.instruction,
        runtime_metadata=patch_draft.runtime_metadata,
        preview=WorkspacePatchDraftPreview(
            materialized_patch=patch,
            preview_workspace_version=preview_workspace.workspace_version,
            preview_ranking_board=preview_workspace.ranking_board,
            would_mutate=False,
        ),
    )
    _draft_review_store(request).save(draft_review)
    return JSONResponse(status_code=201, content=jsonable_encoder({"draft_review": draft_review}))


@router.get("/{workspace_id}/draft-reviews/{draft_review_id}")
def get_draft_review(workspace_id: str, draft_review_id: str, request: Request):
    try:
        draft_review = _draft_review_store(request).get(workspace_id, draft_review_id)
    except DraftReviewNotFound:
        return _draft_review_not_found_response(workspace_id, draft_review_id)
    return {"draft_review": draft_review}


@router.post("/{workspace_id}/draft-reviews/{draft_review_id}/review")
def review_draft_review(workspace_id: str, draft_review_id: str, request: Request, payload: Any = Body(...)):
    try:
        parsed = ReviewDraftReviewRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc, workspace_id=workspace_id)

    review_store = _draft_review_store(request)
    try:
        draft_review = review_store.get(workspace_id, draft_review_id)
    except DraftReviewNotFound:
        return _draft_review_not_found_response(workspace_id, draft_review_id)

    if draft_review.status != "previewed":
        return _draft_review_state_conflict_response(
            workspace_id=workspace_id,
            draft_review=draft_review,
            action="reviewed",
        )

    if parsed.decision == "accept":
        try:
            workspace = _store(request).get(workspace_id)
        except WorkspaceNotFound:
            return _not_found_response(workspace_id)
        if workspace.workspace_version != draft_review.base_workspace_version:
            expired = _expired_review(draft_review)
            review_store.save(expired)
            return _draft_review_version_conflict_response(
                workspace_id=workspace_id,
                draft_review=expired,
                current_workspace_version=workspace.workspace_version,
            )

    next_status = "reviewed" if parsed.decision == "accept" else "rejected"
    updated = draft_review.model_copy(
        update={
            "status": next_status,
            "review": WorkspacePatchDraftReviewDecision(
                decision=parsed.decision,
                reviewed_by=parsed.reviewed_by,
                comment=parsed.comment,
                client=parsed.client,
            ),
            "updated_at": utc_now(),
        }
    )
    review_store.save(updated)
    return {"draft_review": updated}


@router.post("/{workspace_id}/draft-reviews/{draft_review_id}/apply")
def apply_draft_review(workspace_id: str, draft_review_id: str, request: Request, payload: Any = Body(...)):
    try:
        ApplyDraftReviewRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc, workspace_id=workspace_id)

    review_store = _draft_review_store(request)
    try:
        draft_review = review_store.get(workspace_id, draft_review_id)
    except DraftReviewNotFound:
        return _draft_review_not_found_response(workspace_id, draft_review_id)

    if draft_review.status != "reviewed":
        return _draft_review_state_conflict_response(
            workspace_id=workspace_id,
            draft_review=draft_review,
            action="applied",
        )

    store = _store(request)
    try:
        workspace = store.get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)

    if workspace.workspace_version != draft_review.base_workspace_version:
        expired = _expired_review(draft_review)
        review_store.save(expired)
        return _draft_review_version_conflict_response(
            workspace_id=workspace_id,
            draft_review=expired,
            current_workspace_version=workspace.workspace_version,
        )

    try:
        patch = materialize_workspace_patch(draft_review.draft)
        updated_workspace = store.apply_patch(patch)
    except WorkspaceVersionConflict:
        current_version = None
        try:
            current_version = store.get(workspace_id).workspace_version
        except WorkspaceNotFound:
            pass
        expired = _expired_review(draft_review)
        review_store.save(expired)
        return _draft_review_version_conflict_response(
            workspace_id=workspace_id,
            draft_review=expired,
            current_workspace_version=current_version,
        )
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    except WorkspacePatchError as exc:
        failed = _failed_apply_review(
            draft_review,
            error_code="unsupported_workspace_operation"
            if str(exc).startswith("unsupported workspace operation:")
            else "validation_error",
            error_message=str(exc),
        )
        review_store.save(failed)
        return _patch_error_response(exc, workspace_id=workspace_id)
    except ValidationError as exc:
        failed = _failed_apply_review(
            draft_review,
            error_code="patchdraft_validation_error",
            error_message="runtime WorkspacePatchDraft failed validation",
        )
        review_store.save(failed)
        return _patchdraft_validation_error(exc, workspace_id=workspace_id)

    applied = draft_review.model_copy(
        update={
            "status": "applied",
            "updated_at": utc_now(),
            "apply_result": WorkspacePatchDraftApplyResult(
                status="applied",
                materialized_patch_id=patch.id,
                workspace_version=updated_workspace.workspace_version,
                ranking_impact_summary=_ranking_impact_summary(updated_workspace.ranking_board),
                applied_at=utc_now(),
            ),
        }
    )
    review_store.save(applied)
    return {
        "draft_review": applied,
        "patch": patch,
        "workspace": updated_workspace,
        "commit": updated_workspace.commits[-1] if updated_workspace.commits else None,
        "ranking_board": updated_workspace.ranking_board,
    }


@router.post("/{workspace_id}/draft-reviews/{draft_review_id}/reject")
def reject_draft_review(workspace_id: str, draft_review_id: str, request: Request, payload: Any = Body(...)):
    try:
        parsed = RejectDraftReviewRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc, workspace_id=workspace_id)

    review_store = _draft_review_store(request)
    try:
        draft_review = review_store.get(workspace_id, draft_review_id)
    except DraftReviewNotFound:
        return _draft_review_not_found_response(workspace_id, draft_review_id)

    if draft_review.status != "previewed":
        return _draft_review_state_conflict_response(
            workspace_id=workspace_id,
            draft_review=draft_review,
            action="rejected",
        )

    updated = draft_review.model_copy(
        update={
            "status": "rejected",
            "review": WorkspacePatchDraftReviewDecision(
                decision="reject",
                reviewed_by=parsed.rejected_by,
                comment=parsed.reason,
                client="api",
            ),
            "updated_at": utc_now(),
        }
    )
    review_store.save(updated)
    return {"draft_review": updated}


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
