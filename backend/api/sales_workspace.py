from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Body, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend.api.config import get_settings
from backend.sales_workspace.chat_first import (
    ChatTraceNotFound,
    ConversationMessage,
    InMemoryChatTraceStore,
    MessageType,
    PostgresChatTraceStore,
    SalesAgentTurnRun,
    compile_sales_agent_turn_context_pack,
    next_trace_id,
)
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


class CreateConversationMessageRequest(ApiModel):
    id: str | None = None
    role: Literal["user"] = "user"
    message_type: MessageType
    content: str = Field(min_length=1)
    linked_object_refs: list[str] = Field(default_factory=list)


class CreateSalesAgentTurnRequest(ApiModel):
    message_id: str
    base_workspace_version: int = Field(ge=0)
    instruction: str = ""
    token_budget_chars: int = Field(default=6000, ge=1)


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


def create_chat_trace_store() -> InMemoryChatTraceStore | PostgresChatTraceStore:
    if _sales_workspace_store_backend() == "postgres":
        return PostgresChatTraceStore()
    return InMemoryChatTraceStore()


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


def _chat_trace_store(request: Request) -> InMemoryChatTraceStore | PostgresChatTraceStore:
    store = getattr(request.app.state, "sales_workspace_chat_trace_store", None)
    if store is None:
        store = create_chat_trace_store()
        request.app.state.sales_workspace_chat_trace_store = store
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


def _chat_trace_not_found_response(workspace_id: str, object_type: str, object_id: str) -> JSONResponse:
    return _error_response(
        status_code=404,
        code="not_found",
        message=f"{object_type} not found",
        details={"workspace_id": workspace_id, "object_type": object_type, "object_id": object_id},
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


def _message_ref(message: ConversationMessage) -> str:
    return f"ConversationMessage:{message.id}"


def _agent_run_ref(agent_run: SalesAgentTurnRun) -> str:
    return f"AgentRun:{agent_run.id}"


def _needs_clarifying_questions(message: ConversationMessage) -> bool:
    content = message.content.strip()
    if message.message_type not in {
        "product_profile_update",
        "lead_direction_update",
        "mixed_product_and_direction_update",
    }:
        return False
    if len(content) < 12:
        return True
    if message.message_type == "product_profile_update":
        return not _contains_any(
            content,
            [
                "软件",
                "SaaS",
                "服务",
                "培训",
                "园区",
                "招商",
                "维保",
                "外包",
                "排产",
                "库存",
                "财税",
                "现金流",
                "FactoryOps",
            ],
        )
    if message.message_type == "lead_direction_update":
        return not _contains_any(
            content,
            [
                "行业",
                "地区",
                "华东",
                "本地",
                "制造",
                "企业",
                "客户",
                "人",
                "优先",
                "排除",
                "不要",
                "规模",
            ],
        )
    return not _contains_any(content, ["客户", "行业", "地区", "产品", "软件", "服务", "优先"])


def _contains_any(content: str, keywords: list[str]) -> bool:
    normalized = content.lower()
    return any(keyword.lower() in normalized for keyword in keywords)


def _clarifying_questions_for_message(message: ConversationMessage) -> list[str]:
    if message.message_type == "lead_direction_update":
        return [
            "你希望优先覆盖哪些行业或客户类型？",
            "当前优先服务哪个地区或城市？",
            "目标客户大概是什么规模，例如员工人数、营收或门店数量？",
            "客户必须具备哪些前提条件，例如已有系统、预算或明确痛点？",
            "哪些行业、客户类型或订单暂时不想优先做？",
        ]
    return [
        "你的产品或服务主要解决什么具体问题？",
        "最适合的目标客户是谁，例如老板、业务负责人、HR、设备部或财务负责人？",
        "客户现在最痛的 1 到 2 个场景是什么？",
        "你希望优先覆盖哪个地区、行业或企业规模？",
        "哪些行业、客户类型或需求暂时不想优先做？",
    ]


def _assistant_message_for_clarifying_questions(
    *,
    workspace_id: str,
    agent_run: SalesAgentTurnRun,
    source_message: ConversationMessage,
) -> ConversationMessage:
    questions = _clarifying_questions_for_message(source_message)
    content = "我还需要先确认几个关键信息，避免过早生成不可靠的工作区草稿：\n" + "\n".join(
        f"{index}. {question}" for index, question in enumerate(questions, start=1)
    )
    return ConversationMessage(
        id=f"msg_assistant_{agent_run.id}",
        workspace_id=workspace_id,
        role="assistant",
        message_type="clarifying_question",
        content=content,
        linked_object_refs=[],
        created_by_agent_run_id=agent_run.id,
    )


def _generate_chat_first_patch_draft(
    workspace: Any,
    *,
    message: ConversationMessage,
    agent_run: SalesAgentTurnRun,
    context_pack_id: str,
    base_workspace_version: int,
    instruction: str,
) -> WorkspacePatchDraft | None:
    next_version = workspace.workspace_version + 1
    operations: list[dict[str, Any]] = []

    if message.message_type in {"product_profile_update", "mixed_product_and_direction_update"}:
        current_product = (
            workspace.product_profile_revisions.get(workspace.current_product_profile_revision_id)
            if workspace.current_product_profile_revision_id
            else None
        )
        product_version = (current_product.version + 1) if current_product else 1
        operations.append(
            {
                "type": "upsert_product_profile_revision",
                "payload": {
                    "id": f"ppr_chat_v{next_version}",
                    "version": product_version,
                    "product_name": "FactoryOps AI",
                    "one_liner": "Manufacturing scheduling, inventory, and ERP coordination assistant.",
                    "target_customers": ["100-500 employee manufacturing companies"],
                    "target_industries": ["manufacturing"],
                    "pain_points": [
                        "production plan changes do not sync with inventory and ERP context",
                    ],
                    "value_props": [
                        "reduce operational data fragmentation",
                        "help teams coordinate scheduling and inventory changes",
                    ],
                    "constraints": [
                        "needs ERP-adjacent workflow data",
                        f"derived from message {message.id}",
                    ],
                },
            }
        )

    if message.message_type in {"lead_direction_update", "mixed_product_and_direction_update"}:
        current_direction = (
            workspace.lead_direction_versions.get(workspace.current_lead_direction_version_id)
            if workspace.current_lead_direction_version_id
            else None
        )
        direction_version = (current_direction.version + 1) if current_direction else 1
        direction_id = f"dir_chat_v{next_version}"
        operations.extend(
            [
                {
                    "type": "upsert_lead_direction_version",
                    "payload": {
                        "id": direction_id,
                        "version": direction_version,
                        "priority_industries": ["manufacturing"],
                        "target_customer_types": [
                            "manufacturers with ERP but weak scheduling and inventory coordination",
                        ],
                        "regions": ["East China"],
                        "company_sizes": ["100-500 employees"],
                        "priority_constraints": [
                            "has ERP",
                            "scheduling and inventory coordination is weak",
                        ],
                        "excluded_industries": ["education"],
                        "excluded_customer_types": ["large conglomerates"],
                        "change_reason": f"User clarified target segment in chat message {message.id}.",
                    },
                },
                {
                    "type": "set_active_lead_direction",
                    "payload": {"lead_direction_version_id": direction_id},
                },
            ]
        )

    if not operations:
        return None

    intent = message.message_type
    return WorkspacePatchDraft(
        id=f"draft_sales_turn_{intent}_v{next_version}",
        workspace_id=workspace.id,
        base_workspace_version=base_workspace_version,
        author="sales_agent_turn_runtime",
        instruction=instruction or f"chat-first {intent}",
        runtime_metadata={
            "provider": "deterministic_chat_first_runtime",
            "mode": "no_llm_no_langgraph",
            "intent": intent,
            "agent_run_id": agent_run.id,
            "context_pack_id": context_pack_id,
            "source_message_ids": [message.id],
            "kernel_boundary": (
                "Runtime returns WorkspacePatchDraft; Sales Workspace Kernel validates and writes formal objects."
            ),
        },
        operations=operations,
    )


def _assistant_message_for_turn(
    *,
    workspace_id: str,
    agent_run: SalesAgentTurnRun,
    source_message: ConversationMessage,
    draft_review: WorkspacePatchDraftReview | None,
) -> ConversationMessage:
    if source_message.message_type == "out_of_scope_v2_2":
        content = (
            "V2.1 先完成产品理解和获客方向的 chat-first 工作区闭环。"
            "联网搜索、联系人和 CRM 属于 V2.2，当前不会生成 formal lead research result。"
        )
        message_type: MessageType = "out_of_scope_v2_2"
        refs: list[str] = []
    elif draft_review is None:
        content = "我可以先解释当前 workspace 状态；这轮没有生成 WorkspacePatchDraft。"
        message_type = "workspace_question"
        refs = []
    else:
        content = "我已整理出一版工作区更新草稿，请审阅 Draft Review 后再应用。"
        message_type = "draft_summary"
        refs = [f"WorkspacePatchDraftReview:{draft_review.id}"]

    return ConversationMessage(
        id=f"msg_assistant_{agent_run.id}",
        workspace_id=workspace_id,
        role="assistant",
        message_type=message_type,
        content=content,
        linked_object_refs=refs,
        created_by_agent_run_id=agent_run.id,
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


@router.post("/{workspace_id}/messages")
def create_conversation_message(workspace_id: str, request: Request, payload: Any = Body(...)):
    try:
        parsed = CreateConversationMessageRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc, workspace_id=workspace_id)

    try:
        _store(request).get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)

    trace_store = _chat_trace_store(request)
    message_id = parsed.id or next_trace_id("msg_user", len(trace_store.list_messages(workspace_id)))
    message = ConversationMessage(
        id=message_id,
        workspace_id=workspace_id,
        role=parsed.role,
        message_type=parsed.message_type,
        content=parsed.content,
        linked_object_refs=parsed.linked_object_refs,
    )
    trace_store.save_message(message)
    return JSONResponse(status_code=201, content=jsonable_encoder({"message": message}))


@router.get("/{workspace_id}/messages")
def list_conversation_messages(workspace_id: str, request: Request):
    try:
        _store(request).get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    return {"messages": _chat_trace_store(request).list_messages(workspace_id)}


@router.post("/{workspace_id}/agent-runs/sales-agent-turns")
def create_sales_agent_turn(workspace_id: str, request: Request, payload: Any = Body(...)):
    try:
        parsed = CreateSalesAgentTurnRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc, workspace_id=workspace_id)

    store = _store(request)
    trace_store = _chat_trace_store(request)
    review_store = _draft_review_store(request)
    try:
        workspace = store.get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    try:
        source_message = trace_store.get_message(workspace_id, parsed.message_id)
    except ChatTraceNotFound:
        return _chat_trace_not_found_response(workspace_id, "conversation_message", parsed.message_id)

    existing_messages = trace_store.list_messages(workspace_id)
    agent_run_suffix = source_message.id.removeprefix("msg_user_")
    agent_run_id = f"run_sales_turn_{agent_run_suffix}"
    context_pack_id = f"ctx_{agent_run_id}"
    started_at = utc_now()
    agent_run = SalesAgentTurnRun(
        id=agent_run_id,
        workspace_id=workspace_id,
        status="running",
        input_refs=[_message_ref(source_message), f"SalesWorkspace:{workspace_id}", f"ContextPack:{context_pack_id}"],
        runtime_metadata={
            "provider": "deterministic_chat_first_runtime",
            "mode": "no_llm_no_langgraph",
            "intent": source_message.message_type,
        },
        started_at=started_at,
    )
    trace_store.save_agent_run(agent_run)

    context_pack = compile_sales_agent_turn_context_pack(
        workspace,
        agent_run_id=agent_run.id,
        context_pack_id=context_pack_id,
        recent_messages=existing_messages,
        token_budget_chars=parsed.token_budget_chars,
    )
    trace_store.save_context_pack(context_pack)

    if _needs_clarifying_questions(source_message):
        assistant_message = _assistant_message_for_clarifying_questions(
            workspace_id=workspace_id,
            agent_run=agent_run,
            source_message=source_message,
        )
        trace_store.save_message(assistant_message)
        completed = agent_run.model_copy(
            update={
                "status": "succeeded",
                "output_refs": [_message_ref(assistant_message)],
                "finished_at": utc_now(),
            }
        )
        trace_store.save_agent_run(completed)
        return {
            "conversation_message": source_message,
            "agent_run": completed,
            "context_pack": context_pack,
            "assistant_message": assistant_message,
            "patch_draft": None,
            "draft_review": None,
        }

    patch_draft = _generate_chat_first_patch_draft(
        workspace,
        message=source_message,
        agent_run=agent_run,
        context_pack_id=context_pack.id,
        base_workspace_version=parsed.base_workspace_version,
        instruction=parsed.instruction,
    )

    draft_review: WorkspacePatchDraftReview | None = None
    if patch_draft is not None:
        try:
            patch = materialize_workspace_patch(patch_draft)
            preview_workspace = apply_workspace_patch(workspace, patch)
        except WorkspaceVersionConflict as exc:
            failed = agent_run.model_copy(
                update={
                    "status": "failed",
                    "error": {"code": "workspace_version_conflict", "message": str(exc)},
                    "finished_at": utc_now(),
                }
            )
            trace_store.save_agent_run(failed)
            return _workspace_version_conflict_response(
                exc,
                workspace_id=workspace_id,
                current_workspace_version=workspace.workspace_version,
                base_workspace_version=parsed.base_workspace_version,
            )
        except WorkspacePatchError as exc:
            failed = agent_run.model_copy(
                update={
                    "status": "failed",
                    "error": {"code": "validation_error", "message": str(exc)},
                    "finished_at": utc_now(),
                }
            )
            trace_store.save_agent_run(failed)
            return _patch_error_response(exc, workspace_id=workspace_id)
        except ValidationError as exc:
            failed = agent_run.model_copy(
                update={
                    "status": "failed",
                    "error": {"code": "patchdraft_validation_error", "message": "invalid patch draft"},
                    "finished_at": utc_now(),
                }
            )
            trace_store.save_agent_run(failed)
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
        review_store.save(draft_review)

    assistant_message = _assistant_message_for_turn(
        workspace_id=workspace_id,
        agent_run=agent_run,
        source_message=source_message,
        draft_review=draft_review,
    )
    trace_store.save_message(assistant_message)

    output_refs = [_message_ref(assistant_message)]
    if draft_review is not None:
        output_refs.insert(0, f"WorkspacePatchDraftReview:{draft_review.id}")
    completed = agent_run.model_copy(
        update={
            "status": "succeeded",
            "output_refs": output_refs,
            "finished_at": utc_now(),
        }
    )
    trace_store.save_agent_run(completed)

    return {
        "conversation_message": source_message,
        "agent_run": completed,
        "context_pack": context_pack,
        "assistant_message": assistant_message,
        "patch_draft": patch_draft,
        "draft_review": draft_review,
    }


@router.get("/{workspace_id}/agent-runs/{agent_run_id}")
def get_sales_agent_turn(workspace_id: str, agent_run_id: str, request: Request):
    try:
        _store(request).get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    try:
        agent_run = _chat_trace_store(request).get_agent_run(workspace_id, agent_run_id)
    except ChatTraceNotFound:
        return _chat_trace_not_found_response(workspace_id, "agent_run", agent_run_id)
    return {"agent_run": agent_run}


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
