from __future__ import annotations

from backend.runtime.sales_workspace_memory_decision import MemoryDecision, build_memory_patch_draft
from backend.runtime.sales_workspace_patchdraft import materialize_workspace_patch
from backend.sales_workspace.chat_first import ConversationMessage, SalesAgentTurnContextPack, SalesAgentTurnRun
from backend.sales_workspace.patches import apply_workspace_patch
from backend.sales_workspace.schemas import LeadDirectionVersion, ProductProfileRevision, SalesWorkspace


class _Settings:
    llm_provider = "test_provider"
    llm_model = "test_model"
    sales_agent_llm_prompt_version = "sales_agent_turn_llm_v1"


def test_product_constraint_auto_apply_preserves_existing_one_liner() -> None:
    workspace = _workspace_with_product()
    message = _message(
        message_type="product_profile_update",
        content="补充：老客户转介绍有限，主要想拓新客户。",
    )
    decision = MemoryDecision.model_validate(
        {
            "decision": "auto_apply",
            "proposals": [
                {
                    "object_type": "product_profile",
                    "intent": "constraint_only",
                    "field_updates": {"constraints": {"add": ["老客户转介绍有限，主要想拓新客户"]}},
                    "source_evidence": [{"message_id": message.id, "quote": message.content}],
                    "confidence": 0.9,
                    "risk_flags": [],
                }
            ],
            "reasoning_summary": "用户补充销售约束。",
        }
    )

    result = build_memory_patch_draft(
        workspace=workspace,
        source_message=message,
        agent_run=_run(),
        context_pack=_context_pack(workspace),
        memory_decision=decision,
        base_workspace_version=workspace.workspace_version,
        instruction="",
        settings=_Settings(),
        response_usage={},
        evaluator_usage={},
        llm_request_attempts=2,
    )

    assert result.gate.decision == "auto_apply"
    updated = apply_workspace_patch(workspace, materialize_workspace_patch(result.patch_draft))
    product = updated.product_profile_revisions[updated.current_product_profile_revision_id]
    assert product.one_liner == "面向本地企业的销售管理能力提升培训，以线下课形式交付"
    assert "老客户转介绍有限，主要想拓新客户" in product.constraints


def test_corrective_direction_removes_superseded_positive_targets() -> None:
    workspace = _workspace_with_direction()
    message = _message(message_type="lead_direction_update", content="纠正一下：不是 HR，是老板本人，也不要找大企业。")
    decision = MemoryDecision.model_validate(
        {
            "decision": "auto_apply",
            "proposals": [
                {
                    "object_type": "lead_direction",
                    "intent": "correct",
                    "field_updates": {
                        "target_customer_types": {"add": ["老板本人"]},
                        "excluded_customer_types": {"add": ["HR负责人", "培训负责人", "大型企业"]},
                    },
                    "remove_or_supersede": [
                        {"field": "target_customer_types", "values": ["HR负责人", "培训负责人"], "reason": "用户纠正"},
                    ],
                    "source_evidence": [{"message_id": message.id, "quote": message.content}],
                    "confidence": 0.92,
                    "risk_flags": [],
                }
            ],
            "reasoning_summary": "用户纠正目标联系人和排除对象。",
        }
    )

    result = build_memory_patch_draft(
        workspace=workspace,
        source_message=message,
        agent_run=_run(),
        context_pack=_context_pack(workspace),
        memory_decision=decision,
        base_workspace_version=workspace.workspace_version,
        instruction="",
        settings=_Settings(),
        response_usage={},
        evaluator_usage={},
        llm_request_attempts=2,
    )

    assert result.gate.decision == "auto_apply"
    updated = apply_workspace_patch(workspace, materialize_workspace_patch(result.patch_draft))
    direction = updated.lead_direction_versions[updated.current_lead_direction_version_id]
    assert "老板本人" in direction.target_customer_types
    assert "HR负责人" not in direction.target_customer_types
    assert "培训负责人" not in direction.target_customer_types
    assert "大型企业" in direction.excluded_customer_types


def test_debug_or_fallback_content_is_rejected() -> None:
    workspace = _workspace_with_direction()
    message = _message(message_type="lead_direction_update", content="那我怎么找到这些老板？")
    decision = MemoryDecision.model_validate(
        {
            "decision": "auto_apply",
            "proposals": [
                {
                    "object_type": "lead_direction",
                    "intent": "enrich",
                    "field_updates": {
                        "priority_constraints": {
                            "add": [
                                "LLM output omitted lead direction operation; backend kept a reviewable customer-finding draft"
                            ]
                        }
                    },
                    "source_evidence": [{"message_id": message.id, "quote": message.content}],
                    "confidence": 0.8,
                    "risk_flags": [],
                }
            ],
            "reasoning_summary": "bad fallback",
        }
    )

    result = build_memory_patch_draft(
        workspace=workspace,
        source_message=message,
        agent_run=_run(),
        context_pack=_context_pack(workspace),
        memory_decision=decision,
        base_workspace_version=workspace.workspace_version,
        instruction="",
        settings=_Settings(),
        response_usage={},
        evaluator_usage={},
        llm_request_attempts=2,
    )

    assert result.patch_draft is None
    assert result.gate.decision == "reject"
    assert "forbidden_or_debug_content" in result.gate.rejected_reasons


def test_inferred_direction_goes_to_review_instead_of_auto_apply() -> None:
    workspace = _workspace_with_product()
    message = _message(message_type="lead_direction_update", content="我想先找小企业。")
    decision = MemoryDecision.model_validate(
        {
            "decision": "review_required",
            "proposals": [
                {
                    "object_type": "lead_direction",
                    "intent": "enrich",
                    "field_updates": {
                        "priority_industries": {"add": ["本地生活服务", "B2B 服务商"]},
                        "target_customer_types": {"add": ["小企业老板"]},
                    },
                    "source_evidence": [{"message_id": message.id, "quote": message.content}],
                    "confidence": 0.74,
                    "risk_flags": ["inferred_from_assistant_advice"],
                }
            ],
            "reasoning_summary": "方向包含模型推断。",
        }
    )

    result = build_memory_patch_draft(
        workspace=workspace,
        source_message=message,
        agent_run=_run(),
        context_pack=_context_pack(workspace),
        memory_decision=decision,
        base_workspace_version=workspace.workspace_version,
        instruction="",
        settings=_Settings(),
        response_usage={},
        evaluator_usage={},
        llm_request_attempts=2,
    )

    assert result.patch_draft is not None
    assert result.gate.decision == "review_required"


def test_auto_apply_default_direction_without_user_support_is_rejected() -> None:
    workspace = _workspace_with_product()
    message = _message(message_type="lead_direction_update", content="我的客户是什么？我现在应该怎么找第一批客户？")
    decision = MemoryDecision.model_validate(
        {
            "decision": "auto_apply",
            "proposals": [
                {
                    "object_type": "lead_direction",
                    "intent": "enrich",
                    "field_updates": {
                        "priority_industries": {"add": ["本地生活服务", "B2B 服务商", "小型制造或贸易公司"]},
                        "target_customer_types": {"add": ["1-20 人小企业老板"]},
                        "excluded_customer_types": {"add": ["已有成熟销售自动化团队的企业"]},
                    },
                    "source_evidence": [{"message_id": message.id, "quote": message.content}],
                    "confidence": 0.74,
                    "risk_flags": [],
                }
            ],
            "reasoning_summary": "错误地将模型默认方向作为用户事实。",
        }
    )

    result = build_memory_patch_draft(
        workspace=workspace,
        source_message=message,
        agent_run=_run(),
        context_pack=_context_pack(workspace),
        memory_decision=decision,
        base_workspace_version=workspace.workspace_version,
        instruction="",
        settings=_Settings(),
        response_usage={},
        evaluator_usage={},
        llm_request_attempts=2,
    )

    assert result.patch_draft is None
    assert result.gate.decision == "reject"
    assert "empty_lead_direction_update" in result.gate.rejected_reasons


def _workspace_with_product() -> SalesWorkspace:
    product = ProductProfileRevision(
        id="ppr_current",
        workspace_id="ws_memory",
        product_name="本地企业销售管理培训",
        one_liner="面向本地企业的销售管理能力提升培训，以线下课形式交付",
        target_customers=["本地中小企业"],
        constraints=["苏州 50 公里内"],
    )
    return SalesWorkspace(
        id="ws_memory",
        name="Memory Workspace",
        workspace_version=1,
        current_product_profile_revision_id=product.id,
        product_profile_revisions={product.id: product},
    )


def _workspace_with_direction() -> SalesWorkspace:
    workspace = _workspace_with_product()
    direction = LeadDirectionVersion(
        id="dir_current",
        workspace_id=workspace.id,
        priority_industries=["制造业"],
        target_customer_types=["HR负责人", "培训负责人", "年营收亿元以上的企业"],
        excluded_customer_types=[],
    )
    return workspace.model_copy(
        update={
            "current_lead_direction_version_id": direction.id,
            "lead_direction_versions": {direction.id: direction},
        },
        deep=True,
    )


def _message(*, message_type: str, content: str) -> ConversationMessage:
    return ConversationMessage(
        id="msg_user_memory_001",
        workspace_id="ws_memory",
        role="user",
        message_type=message_type,
        content=content,
    )


def _run() -> SalesAgentTurnRun:
    return SalesAgentTurnRun(id="run_memory_001", workspace_id="ws_memory", status="running")


def _context_pack(workspace: SalesWorkspace) -> SalesAgentTurnContextPack:
    return SalesAgentTurnContextPack(
        id="ctx_memory_001",
        workspace_id=workspace.id,
        agent_run_id="run_memory_001",
        workspace_summary="Memory Workspace",
        current_product_profile_revision=workspace.product_profile_revisions[
            workspace.current_product_profile_revision_id
        ].model_dump(mode="json")
        if workspace.current_product_profile_revision_id
        else None,
        current_lead_direction_version=workspace.lead_direction_versions[
            workspace.current_lead_direction_version_id
        ].model_dump(mode="json")
        if workspace.current_lead_direction_version_id
        else None,
        source_versions={
            "workspace_version": workspace.workspace_version,
            "current_product_profile_revision_id": workspace.current_product_profile_revision_id,
            "current_lead_direction_version_id": workspace.current_lead_direction_version_id,
        },
    )
