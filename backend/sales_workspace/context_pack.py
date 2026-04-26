from __future__ import annotations

from backend.sales_workspace.schemas import (
    ContextPack,
    ContextPackCandidate,
    SalesWorkspace,
)


def compile_context_pack(
    workspace: SalesWorkspace,
    *,
    task_type: str = "research_round",
    token_budget_chars: int = 6000,
    top_n_candidates: int = 5,
) -> ContextPack:
    if task_type != "research_round":
        raise ValueError("Sales Workspace Kernel v0 only supports task_type='research_round'")

    product_summary = _product_summary(workspace)
    current_direction = _current_direction(workspace)
    top_candidates = _top_candidates(workspace, top_n_candidates)
    recent_ranking_delta = _recent_ranking_delta(workspace)
    open_questions = _open_questions(workspace)

    pack = ContextPack(
        id=f"ctx_{workspace.id}_v{workspace.workspace_version}",
        workspace_id=workspace.id,
        task_type="research_round",
        token_budget_chars=token_budget_chars,
        product_summary=product_summary,
        current_direction=current_direction,
        top_candidates=top_candidates,
        recent_ranking_delta=recent_ranking_delta,
        open_questions=open_questions,
    )
    return _fit_budget(pack)


def _product_summary(workspace: SalesWorkspace) -> str:
    profile = workspace.product_profile_revisions.get(workspace.current_product_profile_revision_id or "")
    if not profile:
        return "No current product profile."
    parts = [
        profile.product_name,
        profile.one_liner,
        "Target customers: " + ", ".join(profile.target_customers),
        "Pain points: " + ", ".join(profile.pain_points),
        "Value props: " + ", ".join(profile.value_props),
    ]
    return " | ".join(part for part in parts if part and not part.endswith(": "))


def _current_direction(workspace: SalesWorkspace) -> str:
    direction = workspace.lead_direction_versions.get(workspace.current_lead_direction_version_id or "")
    if not direction:
        return "No current lead direction."
    return (
        "Industries: "
        + ", ".join(direction.priority_industries)
        + " | Customer types: "
        + ", ".join(direction.target_customer_types)
        + " | Regions: "
        + ", ".join(direction.regions)
        + " | Reason: "
        + direction.change_reason
    )


def _top_candidates(workspace: SalesWorkspace, top_n_candidates: int) -> list[ContextPackCandidate]:
    if not workspace.ranking_board:
        return []
    return [
        ContextPackCandidate(
            candidate_id=item.candidate_id,
            name=item.candidate_name,
            rank=item.rank,
            score=item.score,
            reason=item.reason,
            supporting_observation_ids=item.supporting_observation_ids,
        )
        for item in workspace.ranking_board.ranked_items[:top_n_candidates]
    ]


def _recent_ranking_delta(workspace: SalesWorkspace) -> list[str]:
    if not workspace.ranking_board:
        return []
    return [delta.reason for delta in workspace.ranking_board.deltas]


def _open_questions(workspace: SalesWorkspace) -> list[str]:
    questions: list[str] = []
    if not workspace.product_profile_revisions:
        questions.append("Confirm product profile before research.")
    if not workspace.lead_direction_versions:
        questions.append("Confirm lead direction before research.")
    if not workspace.research_sources:
        questions.append("Collect source-backed evidence before accepting candidates.")
    return questions


def _fit_budget(pack: ContextPack) -> ContextPack:
    if len(pack.model_dump_json()) <= pack.token_budget_chars:
        return pack

    trimmed = pack.model_copy(deep=True)
    trimmed.top_candidates = [
        candidate.model_copy(update={"reason": candidate.reason[:120]})
        for candidate in trimmed.top_candidates
    ]
    while trimmed.top_candidates and len(trimmed.model_dump_json()) > trimmed.token_budget_chars:
        trimmed.top_candidates.pop()
    if len(trimmed.model_dump_json()) > trimmed.token_budget_chars:
        trimmed.recent_ranking_delta = [item[:160] for item in trimmed.recent_ranking_delta[:1]]
    return trimmed
