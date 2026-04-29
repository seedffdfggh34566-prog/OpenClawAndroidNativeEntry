from __future__ import annotations

import re
from typing import Any, Literal

from fastapi import APIRouter, Body, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend.api.config import get_settings
from backend.sales_workspace.chat_first import (
    ChatTraceNotFound,
    ConversationMessage,
    ConversationThread,
    DefaultConversationThreadId,
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
from backend.runtime.sales_workspace_chat_turn_llm import (
    SalesAgentTurnLlmError,
    SalesAgentTurnLlmOutput,
    generate_sales_agent_turn_llm_result,
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


class CreateConversationThreadRequest(ApiModel):
    id: str | None = None
    title: str = "新对话"
    status: Literal["active", "archived"] = "active"


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


def _llm_runtime_error_response(exc: SalesAgentTurnLlmError, *, workspace_id: str) -> JSONResponse:
    status_code = 503 if exc.code == "llm_runtime_unavailable" else 422
    return _error_response(
        status_code=status_code,
        code=exc.code,
        message=exc.message,
        details={"workspace_id": workspace_id},
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


def _thread_ref(thread: ConversationThread) -> str:
    return f"ConversationThread:{thread.id}"


def _ensure_default_thread(request: Request, workspace_id: str) -> ConversationThread:
    trace_store = _chat_trace_store(request)
    try:
        return trace_store.get_thread(workspace_id, DefaultConversationThreadId)
    except ChatTraceNotFound:
        thread = ConversationThread(
            id=DefaultConversationThreadId,
            workspace_id=workspace_id,
            title="主对话",
        )
        trace_store.save_thread(thread)
        return thread


def _ensure_thread_exists(request: Request, workspace_id: str, thread_id: str) -> ConversationThread:
    if thread_id == DefaultConversationThreadId:
        return _ensure_default_thread(request, workspace_id)
    return _chat_trace_store(request).get_thread(workspace_id, thread_id)


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
        thread_id=agent_run.thread_id,
        role="assistant",
        message_type="clarifying_question",
        content=content,
        linked_object_refs=[],
        created_by_agent_run_id=agent_run.id,
    )


def _assistant_message_for_workspace_question(
    *,
    workspace: Any,
    context_pack: Any,
    workspace_id: str,
    agent_run: SalesAgentTurnRun,
) -> ConversationMessage:
    product = (
        workspace.product_profile_revisions.get(workspace.current_product_profile_revision_id)
        if workspace.current_product_profile_revision_id
        else None
    )
    direction = (
        workspace.lead_direction_versions.get(workspace.current_lead_direction_version_id)
        if workspace.current_lead_direction_version_id
        else None
    )
    refs: list[str] = []
    if product is not None:
        refs.append(f"ProductProfileRevision:{product.id}")
    if direction is not None:
        refs.append(f"LeadDirectionVersion:{direction.id}")

    if product is None and direction is None:
        content = (
            "当前 workspace 还没有正式产品理解或获客方向。"
            "我需要先通过产品理解和获客方向输入形成可审阅草稿，再解释推荐依据。"
        )
    else:
        product_summary = (
            f"产品理解是：{product.one_liner or product.product_name}。"
            if product is not None
            else "当前还没有正式产品理解。"
        )
        direction_summary = (
            "当前获客方向是："
            f"优先行业 {', '.join(direction.priority_industries) or '未明确'}；"
            f"目标客户 {', '.join(direction.target_customer_types) or '未明确'}；"
            f"地区 {', '.join(direction.regions) or '未明确'}；"
            f"规模 {', '.join(direction.company_sizes) or '未明确'}。"
            if direction is not None
            else "当前还没有正式获客方向。"
        )
        rationale = (
            "推荐依据来自当前结构化 workspace objects 和本轮 ContextPack source versions："
            f"workspace_version={context_pack.source_versions.get('workspace_version')}，"
            f"current_product_profile_revision_id={context_pack.source_versions.get('current_product_profile_revision_id')}，"
            f"current_lead_direction_version_id={context_pack.source_versions.get('current_lead_direction_version_id')}。"
        )
        content = f"{product_summary}\n{direction_summary}\n{rationale}"

    return ConversationMessage(
        id=f"msg_assistant_{agent_run.id}",
        workspace_id=workspace_id,
        thread_id=agent_run.thread_id,
        role="assistant",
        message_type="workspace_question",
        content=content,
        linked_object_refs=refs,
        created_by_agent_run_id=agent_run.id,
    )


def _product_profile_payload_for_message(
    *,
    message: ConversationMessage,
    revision_id: str,
    product_version: int,
) -> dict[str, Any]:
    content = message.content
    if _contains_any(content, ["维保", "停机", "设备台账", "预测性维护"]):
        payload = {
            "product_name": "工业设备维保软件",
            "one_liner": "帮助设备密集型工厂降低停机时间、提升维保计划性的工业设备维保软件。",
            "target_customers": ["制造业工厂设备部", "维保服务商", "设备厂商售后团队"],
            "target_industries": ["制造业", "设备密集型工厂"],
            "pain_points": ["停机损失", "维修响应慢", "设备台账分散"],
            "value_props": ["降低停机时间", "提高维保计划性", "集中设备维保信息"],
            "constraints": ["需要明确设备类型", "需要确认服务地区"],
        }
    elif _contains_any(content, ["培训", "线下课", "销售和管理"]):
        payload = {
            "product_name": "本地企业培训服务",
            "one_liner": "面向本地企业的线下销售和管理培训服务。",
            "target_customers": ["本地中小企业", "HR", "销售负责人", "企业老板"],
            "target_industries": ["本地服务业", "销售团队驱动行业"],
            "pain_points": ["销售转化低", "管理能力不足", "培训体系不稳定"],
            "value_props": ["提升销售能力", "提升基层管理能力", "提供线下交付支持"],
            "constraints": ["线下交付半径明显", "需要确认城市和课程类型"],
        }
    elif _contains_any(content, ["财税", "现金流", "发票", "税务"]):
        payload = {
            "product_name": "中小企业财税 SaaS",
            "one_liner": "帮助中小企业老板和财务负责人查看现金流、发票和税务风险的财税 SaaS。",
            "target_customers": ["中小企业老板", "财务负责人", "代账服务商"],
            "target_industries": ["中小企业服务", "财税数字化"],
            "pain_points": ["现金流不透明", "发票管理分散", "税务风险难以及时发现"],
            "value_props": ["提升现金流可见性", "集中发票管理", "提前识别税务风险"],
            "constraints": ["需要发票或流水数据可接入", "需要确认目标客户规模"],
        }
    elif _contains_any(content, ["园区", "招商", "扩租", "选址"]):
        payload = {
            "product_name": "产业园区招商运营服务",
            "one_liner": "帮助产业园区匹配有选址、扩租和政策需求企业的招商运营服务。",
            "target_customers": ["有选址需求的企业", "有扩租需求的成长型企业", "园区招商团队"],
            "target_industries": ["产业园区主导产业", "成长型企业服务"],
            "pain_points": ["选址成本高", "政策不清", "产业配套不匹配"],
            "value_props": ["匹配园区产业定位", "降低选址沟通成本", "提升招商线索质量"],
            "constraints": ["需要确认园区区域", "需要明确主导产业和空间条件"],
        }
    elif _contains_any(content, ["外包", "装配", "小批量", "多品种"]):
        payload = {
            "product_name": "制造业外包生产和装配服务",
            "one_liner": "面向小批量、多品种订单的制造业外包生产和装配服务。",
            "target_customers": ["品牌方", "贸易商", "制造企业供应链部门"],
            "target_industries": ["小批量多品种硬件制造", "设备制造", "消费品制造"],
            "pain_points": ["自建产能成本高", "订单波动", "交付弹性不足"],
            "value_props": ["提供弹性产能", "适配小批量多品种订单", "降低自建产线成本"],
            "constraints": ["需要明确外包能力", "需要确认订单量和交付周期"],
        }
    elif _contains_any(content, ["FactoryOps", "排产", "库存", "ERP"]):
        payload = {
            "product_name": "FactoryOps AI",
            "one_liner": "Manufacturing scheduling, inventory, and ERP coordination assistant.",
            "target_customers": ["100-500 employee manufacturing companies"],
            "target_industries": ["manufacturing"],
            "pain_points": ["production plan changes do not sync with inventory and ERP context"],
            "value_props": [
                "reduce operational data fragmentation",
                "help teams coordinate scheduling and inventory changes",
            ],
            "constraints": ["needs ERP-adjacent workflow data"],
        }
    else:
        payload = {
            "product_name": "待确认产品或服务",
            "one_liner": f"用户消息中描述的产品或服务：{content[:80]}",
            "target_customers": ["待确认目标客户"],
            "target_industries": ["待确认行业"],
            "pain_points": ["待确认痛点"],
            "value_props": ["待确认价值主张"],
            "constraints": ["需要继续追问产品、客户、痛点、区域和排除项"],
        }

    return {
        "id": revision_id,
        "version": product_version,
        **payload,
        "constraints": [
            *payload["constraints"],
            f"derived from message {message.id}",
        ],
    }


def _lead_direction_payload_for_message(
    *,
    message: ConversationMessage,
    direction_id: str,
    direction_version: int,
) -> dict[str, Any]:
    content = message.content
    priority_industries = _direction_priority_industries(content)
    target_customer_types = _direction_target_customer_types(content)
    regions = _direction_regions(content)
    company_sizes = _direction_company_sizes(content)
    excluded_industries = _direction_excluded_industries(content)
    excluded_customer_types = _direction_excluded_customer_types(content)
    priority_constraints = _direction_priority_constraints(content)

    return {
        "id": direction_id,
        "version": direction_version,
        "priority_industries": priority_industries,
        "target_customer_types": target_customer_types,
        "regions": regions,
        "company_sizes": company_sizes,
        "priority_constraints": priority_constraints,
        "excluded_industries": excluded_industries,
        "excluded_customer_types": excluded_customer_types,
        "change_reason": f"用户通过 chat message {message.id} 调整获客方向：{content[:120]}",
    }


def _direction_priority_industries(content: str) -> list[str]:
    if _contains_any(content, ["制造", "工厂", "设备", "外包", "装配"]):
        return ["制造业"]
    if _contains_any(content, ["培训", "销售团队", "管理"]):
        return ["本地服务业", "销售团队驱动行业"]
    if _contains_any(content, ["财税", "现金流", "发票"]):
        return ["中小企业服务", "财税数字化"]
    if _contains_any(content, ["园区", "招商", "选址", "扩租"]):
        return ["园区主导产业"]
    return ["待确认优先行业"]


def _direction_target_customer_types(content: str) -> list[str]:
    if _contains_any(content, ["设备部", "维保"]):
        return ["制造业工厂设备部", "维保服务商"]
    if _contains_any(content, ["HR", "老板", "销售负责人", "培训"]):
        return ["本地中小企业老板", "HR", "销售负责人"]
    if _contains_any(content, ["财务", "代账", "现金流"]):
        return ["中小企业老板", "财务负责人", "代账服务商"]
    if _contains_any(content, ["扩租", "选址", "园区"]):
        return ["有选址或扩租需求的成长型企业"]
    if _contains_any(content, ["品牌方", "贸易商", "供应链"]):
        return ["品牌方", "贸易商", "制造企业供应链部门"]
    if _contains_any(content, ["ERP", "排产", "库存"]):
        return ["有 ERP 但排产库存协同弱的制造企业"]
    return ["待确认目标客户类型"]


def _direction_regions(content: str) -> list[str]:
    regions: list[str] = []
    for keyword in ["华东", "华南", "华北", "上海", "杭州", "苏州", "深圳", "北京", "本地"]:
        if keyword in content:
            regions.append(keyword)
    return regions or ["待确认地区"]


def _direction_company_sizes(content: str) -> list[str]:
    if _contains_any(content, ["100 到 500", "100-500", "100 至 500"]):
        return ["100-500 人"]
    if _contains_any(content, ["20-300", "20 到 300", "20 至 300"]):
        return ["20-300 人"]
    if _contains_any(content, ["中小", "小微"]):
        return ["中小企业"]
    if _contains_any(content, ["成长型", "扩租"]):
        return ["成长型企业"]
    if _contains_any(content, ["小批量", "多品种"]):
        return ["小批量多品种订单客户"]
    return ["待确认规模"]


def _direction_excluded_industries(content: str) -> list[str]:
    excluded: list[str] = []
    if _contains_any(content, ["不要教育", "排除教育", "不做教育"]):
        excluded.append("教育")
    if _contains_any(content, ["不要金融", "排除金融", "不做金融"]):
        excluded.append("金融")
    if _contains_any(content, ["不承接食品", "不要食品"]):
        excluded.append("食品")
    return excluded


def _direction_excluded_customer_types(content: str) -> list[str]:
    excluded: list[str] = []
    if _contains_any(content, ["大型集团", "超大型", "集团客户"]):
        excluded.append("大型集团客户")
    if _contains_any(content, ["纯线上"]):
        excluded.append("纯线上需求客户")
    return excluded


def _direction_priority_constraints(content: str) -> list[str]:
    constraints: list[str] = []
    if _contains_any(content, ["ERP"]):
        constraints.append("已有 ERP")
    if _contains_any(content, ["MES"]):
        constraints.append("已有 MES")
    if _contains_any(content, ["发票", "流水"]):
        constraints.append("发票或流水数据可接入")
    if _contains_any(content, ["线下"]):
        constraints.append("线下交付半径可覆盖")
    if _contains_any(content, ["小批量", "多品种"]):
        constraints.append("订单小批量多品种")
    if _contains_any(content, ["排产", "库存"]):
        constraints.append("排产和库存协同弱")
    return constraints or ["需要继续确认优先约束"]


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
                "payload": _product_profile_payload_for_message(
                    message=message,
                    revision_id=f"ppr_chat_v{next_version}",
                    product_version=product_version,
                ),
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
                    "payload": _lead_direction_payload_for_message(
                        message=message,
                        direction_id=direction_id,
                        direction_version=direction_version,
                    ),
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
    workspace: Any,
    context_pack: Any,
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
    elif draft_review is None and source_message.message_type == "workspace_question":
        return _assistant_message_for_workspace_question(
            workspace=workspace,
            context_pack=context_pack,
            workspace_id=workspace_id,
            agent_run=agent_run,
        )
    elif draft_review is None:
        content = "我可以先解释当前 workspace 状态；这轮没有生成 WorkspacePatchDraft。"
        message_type = "workspace_question"
        refs = []
    else:
        content = "我已整理出一版可审阅更新，请先确认预览，再写入销售工作区。"
        message_type = "draft_summary"
        refs = [f"WorkspacePatchDraftReview:{draft_review.id}"]

    return ConversationMessage(
        id=f"msg_assistant_{agent_run.id}",
        workspace_id=workspace_id,
        thread_id=agent_run.thread_id,
        role="assistant",
        message_type=message_type,
        content=content,
        linked_object_refs=refs,
        created_by_agent_run_id=agent_run.id,
    )


def _assistant_message_for_llm_output(
    *,
    workspace: Any,
    workspace_id: str,
    agent_run: SalesAgentTurnRun,
    output: SalesAgentTurnLlmOutput,
    draft_review: WorkspacePatchDraftReview | None,
) -> ConversationMessage:
    refs: list[str] = []
    if draft_review is not None:
        refs.append(f"WorkspacePatchDraftReview:{draft_review.id}")
    if output.message_type == "workspace_question":
        if workspace.current_product_profile_revision_id:
            refs.append(f"ProductProfileRevision:{workspace.current_product_profile_revision_id}")
        if workspace.current_lead_direction_version_id:
            refs.append(f"LeadDirectionVersion:{workspace.current_lead_direction_version_id}")

    content = _format_llm_assistant_message(
        output=output,
        has_draft_review=draft_review is not None,
        draft_review_status=draft_review.status if draft_review is not None else None,
    )

    return ConversationMessage(
        id=f"msg_assistant_{agent_run.id}",
        workspace_id=workspace_id,
        thread_id=agent_run.thread_id,
        role="assistant",
        message_type=output.message_type,
        content=content,
        linked_object_refs=refs,
        created_by_agent_run_id=agent_run.id,
    )


def _format_llm_assistant_message(
    *,
    output: SalesAgentTurnLlmOutput,
    has_draft_review: bool,
    draft_review_status: str | None = None,
) -> str:
    content = output.assistant_message.strip()
    if output.message_type == "clarifying_question" and output.clarifying_questions:
        content = content.rstrip() + "\n" + "\n".join(
            f"{index}. {question}" for index, question in enumerate(output.clarifying_questions, start=1)
        )
    if output.message_type == "draft_summary":
        if has_draft_review:
            content = _replace_pending_draft_language(content)
        missing_labels = _missing_field_labels(output.missing_fields)
        if missing_labels:
            content = _trim_dangling_followup_intro(content)
            content = content.rstrip() + "\n\n还需要补充：\n" + "\n".join(
                f"{index}. {label}" for index, label in enumerate(missing_labels, start=1)
            )
        if has_draft_review and draft_review_status == "applied" and "沉淀到工作区" not in content:
            content = content.rstrip() + "\n\n我已将本轮有价值信息沉淀到工作区，当前卡片已更新。"
        elif has_draft_review and "写入前不会改变" not in content:
            content = (
                content.rstrip()
                + "\n\n我已把可保存到工作区的更新放在下方，写入前不会改变正式工作区。"
            )
    return _sanitize_user_visible_assistant_content(content)


def _replace_pending_draft_language(content: str) -> str:
    replacement = "我已经把这版判断整理成下方可保存到工作区的更新。"
    patterns = [
        r"如果你确认以上方向，我可以输出正式的\s*lead_direction_version\s*供你审阅[。.]?",
        r"如果你(确认|认可|同意)[^。\n]*(我)?可以(帮你)?(输出|生成|整理)[^。\n]*(lead_direction_version|草稿|可审阅更新|可保存)[^。\n]*[。.]?",
    ]
    normalized = content
    for pattern in patterns:
        normalized = re.sub(pattern, replacement, normalized)
    return re.sub(rf"({re.escape(replacement)})(\s*\1)+", replacement, normalized).strip()


def _trim_dangling_followup_intro(content: str) -> str:
    return re.sub(
        r"(请)?补充(以下内容|如下信息|以下信息|如下内容)?以完善(资料|信息|档案)?[。:：]?\s*$",
        "",
        content,
    ).rstrip()


def _sanitize_user_visible_assistant_content(content: str) -> str:
    sanitized = content
    replacements = {
        "target industries": "目标行业",
        "target_industries": "目标行业",
        "priority industries": "优先行业",
        "priority_industries": "优先行业",
        "company sizes": "公司规模",
        "company_sizes": "公司规模",
        "regions": "目标地区",
        "target customers": "目标客户",
        "target_customers": "目标客户",
        "target customer types": "目标客户类型",
        "target_customer_types": "目标客户类型",
        "pain points": "客户痛点",
        "pain_points": "客户痛点",
        "value props": "价值主张",
        "value_props": "价值主张",
        "workspace_goal": "当前目标",
        "blocked_capabilities": "当前版本限制",
        "V2.2 runtime": "当前版本",
        "runtime": "运行环境",
        "ContextPack": "当前上下文",
        "context_pack": "当前上下文",
        "runtime_metadata": "运行信息",
        "lead_direction_version": "获客方向",
        "current_lead_direction_version_id": "当前获客方向",
        "current_product_profile_revision_id": "当前产品档案",
        "revision_id": "版本标识",
    }
    for raw, replacement in replacements.items():
        sanitized = re.sub(re.escape(raw), replacement, sanitized, flags=re.IGNORECASE)

    sanitized = re.sub(
        r"patch[_\s-]*operations?",
        "可保存更新",
        sanitized,
        flags=re.IGNORECASE,
    )
    sanitized = re.sub(
        r"(当前产品档案|当前获客方向|版本标识)\s*(为|=|:|：)\s*[\w\-:.]+",
        r"\1已记录",
        sanitized,
    )
    sanitized = re.sub(
        r"(当前版本限制标注为|当前目标明确写着|当前版本也将)[^。；;\n]*(公司名单|联系人|CRM|自动触达)[^。；;\n]*[。；;]?",
        "当前版本不能直接生成真实公司名单、联系人或自动触达内容。",
        sanitized,
    )
    sanitized = re.sub(
        r"当前版本限制[^。；;\n]*(公司名单|联系人|CRM|自动触达)[^。；;\n]*[。；;]?",
        "当前版本不能直接生成真实公司名单、联系人或自动触达内容。",
        sanitized,
    )
    sanitized = re.sub(
        r"如果以上信息你觉得够用，我可以生成可保存更新正式保存方向和确认产品 profile[。.]?",
        "如果以上信息够用，我已将可保存到工作区的更新放在下方，写入前不会改变正式工作区。",
        sanitized,
    )
    sanitized = re.sub(
        r"如果[^。\n]*(生成|输出|整理)[^。\n]*可保存更新[^。\n]*[。.]?",
        "我会把这版判断整理成可保存到工作区的更新，写入前不会改变正式工作区。",
        sanitized,
    )
    return sanitized.strip()


def _missing_field_labels(missing_fields: list[str]) -> list[str]:
    labels = {
        "product": "产品正式名称和一句话定位",
        "product_profile": "产品定位、客户和核心价值",
        "product_form": "产品形态",
        "preferred_channels": "获客渠道偏好",
        "product_name": "产品正式名称",
        "one_liner": "一句话产品定位",
        "target_customer": "目标客户",
        "target_customers": "目标客户",
        "target_customer_types": "目标客户类型",
        "target_industry": "目标行业",
        "target_industries": "目标行业",
        "priority_industries": "优先行业",
        "company_size": "目标公司规模",
        "company_sizes": "目标公司规模",
        "region": "目标地区",
        "regions": "目标地区",
        "pain_point": "客户痛点",
        "pain_points": "客户痛点",
        "value_prop": "价值主张",
        "value_props": "价值主张",
        "lead_direction": "获客方向",
    }
    result: list[str] = []
    for field in missing_fields:
        label = labels.get(field, field.replace("_", " "))
        if label not in result:
            result.append(label)
    return result


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
    return _create_conversation_message_for_thread(
        workspace_id=workspace_id,
        thread_id=DefaultConversationThreadId,
        request=request,
        payload=payload,
    )


@router.post("/{workspace_id}/threads/{thread_id}/messages")
def create_thread_conversation_message(
    workspace_id: str,
    thread_id: str,
    request: Request,
    payload: Any = Body(...),
):
    return _create_conversation_message_for_thread(
        workspace_id=workspace_id,
        thread_id=thread_id,
        request=request,
        payload=payload,
    )


def _create_conversation_message_for_thread(
    *,
    workspace_id: str,
    thread_id: str,
    request: Request,
    payload: Any,
):
    try:
        parsed = CreateConversationMessageRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc, workspace_id=workspace_id)

    try:
        _store(request).get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    try:
        thread = _ensure_thread_exists(request, workspace_id, thread_id)
    except ChatTraceNotFound:
        return _chat_trace_not_found_response(workspace_id, "conversation_thread", thread_id)

    trace_store = _chat_trace_store(request)
    thread_prefix = "msg_user" if thread.id == DefaultConversationThreadId else f"msg_user_{thread.id}"
    message_id = parsed.id or next_trace_id(thread_prefix, len(trace_store.list_messages(workspace_id, thread.id)))
    message = ConversationMessage(
        id=message_id,
        workspace_id=workspace_id,
        thread_id=thread.id,
        role=parsed.role,
        message_type=parsed.message_type,
        content=parsed.content,
        linked_object_refs=parsed.linked_object_refs,
    )
    trace_store.save_message(message)
    return JSONResponse(status_code=201, content=jsonable_encoder({"message": message}))


@router.get("/{workspace_id}/messages")
def list_conversation_messages(workspace_id: str, request: Request):
    return _list_conversation_messages_for_thread(
        workspace_id=workspace_id,
        thread_id=DefaultConversationThreadId,
        request=request,
    )


@router.get("/{workspace_id}/threads/{thread_id}/messages")
def list_thread_conversation_messages(workspace_id: str, thread_id: str, request: Request):
    return _list_conversation_messages_for_thread(
        workspace_id=workspace_id,
        thread_id=thread_id,
        request=request,
    )


def _list_conversation_messages_for_thread(*, workspace_id: str, thread_id: str, request: Request):
    try:
        _store(request).get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    try:
        thread = _ensure_thread_exists(request, workspace_id, thread_id)
    except ChatTraceNotFound:
        return _chat_trace_not_found_response(workspace_id, "conversation_thread", thread_id)
    return {"messages": _chat_trace_store(request).list_messages(workspace_id, thread.id)}


@router.get("/{workspace_id}/threads")
def list_conversation_threads(workspace_id: str, request: Request):
    try:
        _store(request).get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)
    _ensure_default_thread(request, workspace_id)
    return {"threads": _chat_trace_store(request).list_threads(workspace_id)}


@router.post("/{workspace_id}/threads")
def create_conversation_thread(workspace_id: str, request: Request, payload: Any = Body(...)):
    try:
        parsed = CreateConversationThreadRequest.model_validate(payload)
    except ValidationError as exc:
        return _validation_error(exc, workspace_id=workspace_id)

    try:
        _store(request).get(workspace_id)
    except WorkspaceNotFound:
        return _not_found_response(workspace_id)

    trace_store = _chat_trace_store(request)
    existing_threads = trace_store.list_threads(workspace_id)
    thread_id = parsed.id or next_trace_id("thread", len(existing_threads))
    thread = ConversationThread(
        id=thread_id,
        workspace_id=workspace_id,
        title=parsed.title.strip() or "新对话",
        status=parsed.status,
    )
    trace_store.save_thread(thread)
    return JSONResponse(status_code=201, content=jsonable_encoder({"thread": thread}))


@router.post("/{workspace_id}/agent-runs/sales-agent-turns")
def create_sales_agent_turn(workspace_id: str, request: Request, payload: Any = Body(...)):
    return _create_sales_agent_turn_for_thread(
        workspace_id=workspace_id,
        thread_id=DefaultConversationThreadId,
        request=request,
        payload=payload,
    )


@router.post("/{workspace_id}/threads/{thread_id}/agent-runs/sales-agent-turns")
def create_thread_sales_agent_turn(workspace_id: str, thread_id: str, request: Request, payload: Any = Body(...)):
    return _create_sales_agent_turn_for_thread(
        workspace_id=workspace_id,
        thread_id=thread_id,
        request=request,
        payload=payload,
    )


def _create_sales_agent_turn_for_thread(
    *,
    workspace_id: str,
    thread_id: str,
    request: Request,
    payload: Any,
):
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
        thread = _ensure_thread_exists(request, workspace_id, thread_id)
    except ChatTraceNotFound:
        return _chat_trace_not_found_response(workspace_id, "conversation_thread", thread_id)
    try:
        source_message = trace_store.get_message(workspace_id, parsed.message_id)
    except ChatTraceNotFound:
        return _chat_trace_not_found_response(workspace_id, "conversation_message", parsed.message_id)
    if source_message.thread_id != thread.id:
        return _chat_trace_not_found_response(workspace_id, "conversation_message", parsed.message_id)

    existing_messages = trace_store.list_messages(workspace_id, thread.id)
    agent_run_suffix = source_message.id.removeprefix("msg_user_")
    agent_run_id = f"run_sales_turn_{agent_run_suffix}"
    context_pack_id = f"ctx_{agent_run_id}"
    started_at = utc_now()
    agent_run = SalesAgentTurnRun(
        id=agent_run_id,
        workspace_id=workspace_id,
        thread_id=thread.id,
        status="running",
        input_refs=[
            _message_ref(source_message),
            _thread_ref(thread),
            f"SalesWorkspace:{workspace_id}",
            f"ContextPack:{context_pack_id}",
        ],
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
        thread_id=thread.id,
        agent_run_id=agent_run.id,
        context_pack_id=context_pack_id,
        recent_messages=existing_messages,
        token_budget_chars=parsed.token_budget_chars,
    )
    trace_store.save_context_pack(context_pack)

    settings = get_settings()
    runtime_mode = settings.sales_agent_runtime_mode.strip().lower()
    if runtime_mode == "llm":
        llm_metadata = {
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "prompt_version": settings.sales_agent_llm_prompt_version,
            "mode": "real_llm_no_langgraph",
            "intent": source_message.message_type,
        }
        trace_store.save_agent_run(agent_run.model_copy(update={"runtime_metadata": llm_metadata}))
        try:
            llm_result = generate_sales_agent_turn_llm_result(
                settings=settings,
                workspace=workspace,
                source_message=source_message,
                agent_run=agent_run,
                context_pack=context_pack,
                base_workspace_version=parsed.base_workspace_version,
                instruction=parsed.instruction,
            )
        except SalesAgentTurnLlmError as exc:
            failed = agent_run.model_copy(
                update={
                    "status": "failed",
                    "runtime_metadata": llm_metadata,
                    "error": {"code": exc.code, "message": exc.message},
                    "finished_at": utc_now(),
                }
            )
            trace_store.save_agent_run(failed)
            return _llm_runtime_error_response(exc, workspace_id=workspace_id)

        patch_draft = llm_result.patch_draft
        draft_review: WorkspacePatchDraftReview | None = None
        if patch_draft is not None:
            try:
                patch = materialize_workspace_patch(patch_draft)
                preview_workspace = apply_workspace_patch(workspace, patch)
                updated_workspace = store.apply_patch(patch)
            except WorkspaceVersionConflict as exc:
                failed = agent_run.model_copy(
                    update={
                        "status": "failed",
                        "runtime_metadata": llm_result.runtime_metadata,
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
                        "runtime_metadata": llm_result.runtime_metadata,
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
                        "runtime_metadata": llm_result.runtime_metadata,
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
                status="applied",
                base_workspace_version=patch_draft.base_workspace_version,
                created_by=patch_draft.author,
                instruction=patch_draft.instruction,
                runtime_metadata=patch_draft.runtime_metadata,
                preview=WorkspacePatchDraftPreview(
                    materialized_patch=patch,
                    preview_workspace_version=preview_workspace.workspace_version,
                    preview_ranking_board=preview_workspace.ranking_board,
                    would_mutate=True,
                ),
                apply_result=WorkspacePatchDraftApplyResult(
                    status="applied",
                    materialized_patch_id=patch.id,
                    workspace_version=updated_workspace.workspace_version,
                    ranking_impact_summary=_ranking_impact_summary(updated_workspace.ranking_board),
                    applied_at=utc_now(),
                ),
            )
            review_store.save(draft_review)
            workspace = updated_workspace

        assistant_message = _assistant_message_for_llm_output(
            workspace=workspace,
            workspace_id=workspace_id,
            agent_run=agent_run,
            output=llm_result.output,
            draft_review=draft_review,
        )
        trace_store.save_message(assistant_message)
        output_refs = [_message_ref(assistant_message)]
        if draft_review is not None:
            output_refs.insert(0, f"WorkspacePatchDraftReview:{draft_review.id}")
        completed = agent_run.model_copy(
            update={
                "status": "succeeded",
                "runtime_metadata": llm_result.runtime_metadata,
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

    if runtime_mode != "deterministic":
        failed = agent_run.model_copy(
            update={
                "status": "failed",
                "error": {
                    "code": "validation_error",
                    "message": f"unsupported sales agent runtime mode: {runtime_mode}",
                },
                "finished_at": utc_now(),
            }
        )
        trace_store.save_agent_run(failed)
        return _error_response(
            status_code=422,
            code="validation_error",
            message="unsupported sales agent runtime mode",
            details={"workspace_id": workspace_id, "runtime_mode": runtime_mode},
        )

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
        workspace=workspace,
        context_pack=context_pack,
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
