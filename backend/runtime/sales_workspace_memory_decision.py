from __future__ import annotations

import json
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from backend.api.config import Settings
from backend.runtime.sales_workspace_patchdraft import WorkspacePatchDraft, WorkspacePatchDraftOperation
from backend.sales_workspace.chat_first import ConversationMessage, SalesAgentTurnContextPack, SalesAgentTurnRun
from backend.sales_workspace.schemas import LeadDirectionVersion, ProductProfileRevision, SalesWorkspace


MemoryDecisionValue = Literal["auto_apply", "review_required", "reject"]
MemoryIntent = Literal["enrich", "correct", "replace", "exclude", "constraint_only", "execution_advice_only"]


class MemoryDecisionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MemorySourceEvidence(MemoryDecisionModel):
    message_id: str
    quote: str = Field(min_length=1)


class MemoryProposal(MemoryDecisionModel):
    object_type: Literal["product_profile", "lead_direction"]
    intent: MemoryIntent
    field_updates: dict[str, Any] = Field(default_factory=dict)
    remove_or_supersede: list[dict[str, Any]] = Field(default_factory=list)
    source_evidence: list[MemorySourceEvidence] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)
    risk_flags: list[str] = Field(default_factory=list)


class MemoryDecision(MemoryDecisionModel):
    decision: MemoryDecisionValue
    proposals: list[MemoryProposal] = Field(default_factory=list)
    reasoning_summary: str = ""

    @model_validator(mode="after")
    def validate_decision(self) -> MemoryDecision:
        if self.decision == "reject" and self.proposals:
            raise ValueError("reject decision must not include proposals")
        return self


class MemoryGateResult(MemoryDecisionModel):
    decision: MemoryDecisionValue
    accepted_proposals: int = 0
    rejected_reasons: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)


class MemoryPatchBuildResult(MemoryDecisionModel):
    patch_draft: WorkspacePatchDraft | None = None
    gate: MemoryGateResult


def parse_memory_decision_json(content: str) -> dict[str, Any]:
    text = _strip_thinking_and_fences(content)
    decoder = json.JSONDecoder()
    first_object: dict[str, Any] | None = None
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
            raise ValueError("memory_decision_json_object_required")
        if first_object is None:
            first_object = parsed
        if "decision" in parsed:
            return parsed
    if first_object is not None:
        return first_object
    raise ValueError("memory_decision_json_object_not_found") from last_error


def build_memory_decision_messages(
    *,
    source_message: ConversationMessage,
    assistant_output: dict[str, Any],
    context_pack: SalesAgentTurnContextPack,
    workspace: SalesWorkspace,
) -> list[dict[str, str]]:
    schema = {
        "decision": "auto_apply | review_required | reject",
        "proposals": [
            {
                "object_type": "product_profile | lead_direction",
                "intent": "enrich | correct | replace | exclude | constraint_only | execution_advice_only",
                "field_updates": {
                    "field_name": {"add": ["value"], "set": "value"}
                },
                "remove_or_supersede": [{"field": "field_name", "values": ["old value"], "reason": "why"}],
                "source_evidence": [{"message_id": source_message.id, "quote": "用户原话"}],
                "confidence": "0 到 1",
                "risk_flags": ["inferred_from_assistant_advice"],
            }
        ],
        "reasoning_summary": "短摘要，不要输出 chain-of-thought",
    }
    runtime_input = {
        "workspace": {
            "id": workspace.id,
            "workspace_version": workspace.workspace_version,
            "current_product_profile_revision_id": workspace.current_product_profile_revision_id,
            "current_lead_direction_version_id": workspace.current_lead_direction_version_id,
        },
        "context_pack": context_pack.model_dump(mode="json"),
        "user_message": source_message.model_dump(mode="json"),
        "assistant_output": assistant_output,
    }
    return [
        {
            "role": "system",
            "content": (
                "你是 OpenClaw V2.1 的 MemoryEvaluator。"
                "你只判断本轮对话中哪些信息可以作为销售工作区记忆候选。"
                "不要把 assistant 自己推断的行业、渠道、执行计划当作用户事实。"
                "只有用户原话明确表达的事实、偏好、纠错、约束才可以 auto_apply。"
                "assistant 给出的方向建议、行业推断或执行动作最多 review_required。"
                "fallback、默认行业、runtime/debug 文案、没有用户原话证据的正式字段必须 reject。"
                "source_evidence.quote 必须逐字来自 user_message.content。"
                "只输出单个 JSON object，不要输出 markdown、解释或额外文本。"
            ),
        },
        {
            "role": "user",
            "content": (
                "请评估本轮是否应该沉淀到正式 workspace。\n"
                f"output_schema:\n{json.dumps(schema, ensure_ascii=False)}\n\n"
                f"runtime_input:\n{json.dumps(runtime_input, ensure_ascii=False)}"
            ),
        },
    ]


def build_memory_patch_draft(
    *,
    workspace: SalesWorkspace,
    source_message: ConversationMessage,
    agent_run: SalesAgentTurnRun,
    context_pack: SalesAgentTurnContextPack,
    memory_decision: MemoryDecision,
    base_workspace_version: int,
    instruction: str,
    settings: Settings,
    response_usage: dict[str, Any],
    evaluator_usage: dict[str, Any],
    llm_request_attempts: int,
) -> MemoryPatchBuildResult:
    if memory_decision.decision == "reject":
        return MemoryPatchBuildResult(
            gate=MemoryGateResult(decision="reject", rejected_reasons=["memory_decision_rejected"])
        )

    accepted_operations: list[WorkspacePatchDraftOperation] = []
    rejected_reasons: list[str] = []
    risk_flags: list[str] = []
    next_workspace_version = workspace.workspace_version + 1
    current_product = (
        workspace.product_profile_revisions.get(workspace.current_product_profile_revision_id)
        if workspace.current_product_profile_revision_id
        else None
    )
    current_direction = (
        workspace.lead_direction_versions.get(workspace.current_lead_direction_version_id)
        if workspace.current_lead_direction_version_id
        else None
    )
    product_payload: dict[str, Any] | None = None
    direction_payload: dict[str, Any] | None = None
    direction_id: str | None = None

    for proposal in memory_decision.proposals:
        proposal_risks = list(proposal.risk_flags)
        evidence_check = _validate_source_evidence(proposal, source_message)
        if evidence_check:
            rejected_reasons.append(evidence_check)
            continue
        if _proposal_has_forbidden_content(proposal):
            rejected_reasons.append("forbidden_or_debug_content")
            continue
        risk_flags.extend(proposal_risks)
        if proposal.object_type == "product_profile":
            payload = _product_payload_from_proposal(
                workspace=workspace,
                current_product=current_product,
                proposal=proposal,
                next_workspace_version=next_workspace_version,
            )
            if payload is None:
                rejected_reasons.append("empty_product_profile_update")
                continue
            product_payload = payload
        elif proposal.object_type == "lead_direction":
            payload = _lead_direction_payload_from_proposal(
                workspace=workspace,
                current_direction=current_direction,
                proposal=proposal,
                source_message=source_message,
                decision=memory_decision.decision,
                next_workspace_version=next_workspace_version,
            )
            if payload is None:
                rejected_reasons.append("empty_lead_direction_update")
                continue
            direction_payload = payload

    if product_payload is not None:
        accepted_operations.append(
            WorkspacePatchDraftOperation(type="upsert_product_profile_revision", payload=product_payload)
        )
    if direction_payload is not None:
        direction_id = str(direction_payload["id"])
        accepted_operations.append(
            WorkspacePatchDraftOperation(type="upsert_lead_direction_version", payload=direction_payload)
        )
        accepted_operations.append(
            WorkspacePatchDraftOperation(
                type="set_active_lead_direction",
                payload={"lead_direction_version_id": direction_id},
            )
        )

    if not accepted_operations:
        return MemoryPatchBuildResult(
            gate=MemoryGateResult(
                decision="reject",
                accepted_proposals=0,
                rejected_reasons=rejected_reasons or ["no_accepted_memory_update"],
                risk_flags=_dedupe(risk_flags),
            )
        )

    gate_decision: MemoryDecisionValue = (
        "auto_apply" if memory_decision.decision == "auto_apply" and not risk_flags else "review_required"
    )
    patch_draft = WorkspacePatchDraft(
        id=f"draft_sales_turn_memory_v{next_workspace_version}",
        workspace_id=workspace.id,
        base_workspace_version=base_workspace_version,
        author="sales_agent_turn_memory_pipeline",
        instruction=instruction or f"memory decision for {source_message.message_type}",
        runtime_metadata={
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "prompt_version": settings.sales_agent_llm_prompt_version,
            "mode": "real_llm_memory_decision_no_langgraph",
            "intent": source_message.message_type,
            "agent_run_id": agent_run.id,
            "context_pack_id": context_pack.id,
            "source_message_ids": [source_message.id],
            "response_llm_usage": _normalize_usage(response_usage),
            "memory_evaluator_llm_usage": _normalize_usage(evaluator_usage),
            "llm_request_attempts": llm_request_attempts,
            "memory_decision": memory_decision.model_dump(mode="json"),
            "memory_gate": {
                "decision": gate_decision,
                "rejected_reasons": rejected_reasons,
                "risk_flags": _dedupe(risk_flags),
            },
            "kernel_boundary": (
                "Runtime returns WorkspacePatchDraft; Sales Workspace Kernel validates and writes formal objects."
            ),
        },
        operations=accepted_operations,
    )
    return MemoryPatchBuildResult(
        patch_draft=patch_draft,
        gate=MemoryGateResult(
            decision=gate_decision,
            accepted_proposals=len(accepted_operations),
            rejected_reasons=rejected_reasons,
            risk_flags=_dedupe(risk_flags),
        ),
    )


def _product_payload_from_proposal(
    *,
    workspace: SalesWorkspace,
    current_product: ProductProfileRevision | None,
    proposal: MemoryProposal,
    next_workspace_version: int,
) -> dict[str, Any] | None:
    current = current_product.model_dump(mode="json") if current_product else {}
    payload = {
        "id": f"ppr_memory_v{next_workspace_version}",
        "workspace_id": workspace.id,
        "version": (current_product.version + 1) if current_product else 1,
        "product_name": current.get("product_name") or "",
        "one_liner": current.get("one_liner") or "",
        "target_customers": _coerce_list(current.get("target_customers")),
        "target_industries": _coerce_list(current.get("target_industries")),
        "pain_points": _coerce_list(current.get("pain_points")),
        "value_props": _coerce_list(current.get("value_props")),
        "constraints": _coerce_list(current.get("constraints")),
    }
    changed = False
    updates = proposal.field_updates
    for field in ("product_name", "one_liner"):
        value = _extract_set_value(updates.get(field))
        if not value or _is_unknown_text(value) or _has_forbidden_text(value):
            continue
        if current_product is not None and proposal.intent not in {"replace", "correct"} and payload[field]:
            continue
        if payload[field] != value:
            payload[field] = value
            changed = True
    for field in ("target_customers", "target_industries", "pain_points", "value_props", "constraints"):
        additions = _extract_add_values(updates.get(field))
        clean_additions = [value for value in additions if not _is_unknown_text(value) and not _has_forbidden_text(value)]
        before = list(payload[field])
        payload[field] = _merge_values(payload[field], clean_additions)
        changed = changed or payload[field] != before
    if not payload["product_name"]:
        payload["product_name"] = "待确认产品或服务"
    if not payload["one_liner"]:
        payload["one_liner"] = proposal.source_evidence[0].quote[:80]
    return payload if changed or current_product is None else None


def _lead_direction_payload_from_proposal(
    *,
    workspace: SalesWorkspace,
    current_direction: LeadDirectionVersion | None,
    proposal: MemoryProposal,
    source_message: ConversationMessage,
    decision: MemoryDecisionValue,
    next_workspace_version: int,
) -> dict[str, Any] | None:
    current = current_direction.model_dump(mode="json") if current_direction else {}
    payload = {
        "id": f"dir_memory_v{next_workspace_version}",
        "workspace_id": workspace.id,
        "version": (current_direction.version + 1) if current_direction else 1,
        "priority_industries": _coerce_list(current.get("priority_industries")),
        "target_customer_types": _coerce_list(current.get("target_customer_types")),
        "regions": _coerce_list(current.get("regions")),
        "company_sizes": _coerce_list(current.get("company_sizes")),
        "priority_constraints": _coerce_list(current.get("priority_constraints")),
        "excluded_industries": _coerce_list(current.get("excluded_industries")),
        "excluded_customer_types": _coerce_list(current.get("excluded_customer_types")),
        "change_reason": f"用户本轮明确更新记忆：{proposal.source_evidence[0].quote[:100]}",
    }
    changed = False
    updates = proposal.field_updates
    for field in (
        "priority_industries",
        "target_customer_types",
        "regions",
        "company_sizes",
        "priority_constraints",
        "excluded_industries",
        "excluded_customer_types",
    ):
        additions = _extract_add_values(updates.get(field))
        clean_additions = []
        for value in additions:
            if _is_unknown_text(value) or _has_forbidden_text(value):
                continue
            if decision == "auto_apply":
                if not _value_supported_by_user_message(value, source_message.content):
                    continue
            clean_additions.append(value)
        before = list(payload[field])
        payload[field] = _merge_values(payload[field], clean_additions)
        changed = changed or payload[field] != before
    for removal in proposal.remove_or_supersede:
        field = str(removal.get("field") or "").strip()
        values = _coerce_list(removal.get("values"))
        if field in payload and isinstance(payload[field], list):
            before = list(payload[field])
            payload[field] = _remove_matching_values(payload[field], values)
            changed = changed or payload[field] != before
    _remove_excluded_conflicts(payload)
    direction_fields = (
        "priority_industries",
        "target_customer_types",
        "regions",
        "company_sizes",
        "priority_constraints",
        "excluded_industries",
        "excluded_customer_types",
    )
    has_memory_values = any(payload[field] for field in direction_fields)
    return payload if changed and has_memory_values else None


def _validate_source_evidence(proposal: MemoryProposal, source_message: ConversationMessage) -> str | None:
    if not proposal.source_evidence:
        return "missing_source_evidence"
    for evidence in proposal.source_evidence:
        if evidence.message_id != source_message.id:
            return "source_evidence_wrong_message"
        if evidence.quote.strip() not in source_message.content:
            return "source_evidence_quote_not_in_user_message"
    return None


def _proposal_has_forbidden_content(proposal: MemoryProposal) -> bool:
    values = list(_walk_values(proposal.field_updates)) + list(_walk_values(proposal.remove_or_supersede))
    return any(_has_forbidden_text(value) for value in values)


def _walk_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        values: list[str] = []
        for item in value.values():
            values.extend(_walk_values(item))
        return values
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(_walk_values(item))
        return values
    return []


def _has_forbidden_text(value: str) -> bool:
    text = value.lower()
    forbidden = (
        "llm output omitted",
        "backend kept",
        "derived from message",
        "contextpack",
        "context_pack",
        "patch_operations",
        "runtime",
        "workspace_version",
    )
    return any(marker in text for marker in forbidden)


_UNKNOWN_TEXT_MARKERS = (
    "待确认",
    "未知",
    "未提供",
    "用户未说明",
    "用户未提供",
    "未说明",
    "未明确",
    "待补充",
    "需要确认",
    "尚不明确",
    "空值",
    "n/a",
    "none",
    "null",
)


def _is_unknown_text(value: str) -> bool:
    text = value.strip().lower()
    if not text or text in {"-", "—"}:
        return True
    return any(marker in text for marker in _UNKNOWN_TEXT_MARKERS)


def _extract_set_value(value: Any) -> str:
    if isinstance(value, dict):
        raw = value.get("set")
    else:
        raw = value
    return str(raw).strip() if raw is not None else ""


def _extract_add_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        raw = value.get("add", [])
    else:
        raw = value
    return _coerce_list(raw)


def _coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [str(item).strip() for item in value if item is not None and str(item).strip()]
    return [str(value).strip()]


def _merge_values(existing: list[str], incoming: list[str]) -> list[str]:
    result = list(existing)
    keys = {_canonical_key(value) for value in result}
    for value in incoming:
        key = _canonical_key(value)
        if key and key not in keys:
            result.append(value)
            keys.add(key)
    return result


def _remove_matching_values(existing: list[str], removals: list[str]) -> list[str]:
    removal_keys = {_canonical_key(value) for value in removals}
    return [value for value in existing if _canonical_key(value) not in removal_keys]


def _remove_excluded_conflicts(payload: dict[str, Any]) -> None:
    excluded_industries = _coerce_list(payload.get("excluded_industries"))
    excluded_customers = _coerce_list(payload.get("excluded_customer_types"))
    payload["priority_industries"] = [
        value for value in _coerce_list(payload.get("priority_industries")) if not _contradicted(value, excluded_industries)
    ]
    payload["target_customer_types"] = [
        value
        for value in _coerce_list(payload.get("target_customer_types"))
        if not _contradicted(value, excluded_customers)
    ]
    payload["company_sizes"] = [
        value
        for value in _coerce_list(payload.get("company_sizes"))
        if not _contradicted(value, excluded_customers)
    ]


def _contradicted(value: str, excluded_values: list[str]) -> bool:
    value_key = _canonical_key(value)
    for excluded in excluded_values:
        excluded_key = _canonical_key(excluded)
        if value_key == excluded_key:
            return True
        if "大型" in excluded or "大企业" in excluded or "亿元" in excluded:
            if "大型" in value or "大企业" in value or "亿元" in value:
                return True
        if "HR" in excluded.upper() or "培训负责人" in excluded:
            if "HR" in value.upper() or "培训负责人" in value:
                return True
    return False


def _value_supported_by_user_message(value: str, user_message: str) -> bool:
    value_key = _canonical_key(value)
    message_key = _canonical_key(user_message)
    if not value_key:
        return False
    if value_key in message_key:
        return True
    if "hr" in value_key and "hr" in message_key:
        return True
    if ("大型" in value or "大企业" in value) and ("大型" in user_message or "大企业" in user_message):
        return True
    important_terms = [term for term in re.split(r"[、,，/（）()\\s]+", value) if len(term) >= 2]
    return any(_canonical_key(term) in message_key for term in important_terms)


def _canonical_key(value: str) -> str:
    return re.sub(r"[\s　,，、/()（）\-]+", "", value.strip().lower())


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _normalize_usage(usage: dict[str, Any]) -> dict[str, int]:
    normalized: dict[str, int] = {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        value = usage.get(key)
        if isinstance(value, int) and value >= 0:
            normalized[key] = value
    return normalized


def _strip_thinking_and_fences(content: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE)
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()
