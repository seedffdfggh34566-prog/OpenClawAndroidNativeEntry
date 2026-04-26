from __future__ import annotations

from datetime import datetime

from backend.sales_workspace.schemas import SalesWorkspace, utc_now


def render_markdown_projection(
    workspace: SalesWorkspace,
    *,
    generated_at: datetime | None = None,
) -> dict[str, str]:
    generated_at = generated_at or utc_now()
    files = {
        "product/current.md": _render_product(workspace, generated_at),
        "directions/current.md": _render_direction(workspace, generated_at),
        "candidates/index.md": _render_candidates(workspace, generated_at),
        "rankings/current.md": _render_rankings(workspace, generated_at),
    }
    for research_round in sorted(workspace.research_rounds.values(), key=lambda item: item.round_index):
        files[f"research/rounds/{research_round.id}.md"] = _render_research_round(
            workspace, research_round.id, generated_at
        )
    return files


def _frontmatter(workspace: SalesWorkspace, object_type: str, object_id: str | None, generated_at: datetime) -> str:
    return (
        "---\n"
        "generated: true\n"
        f"workspace_id: {workspace.id}\n"
        f"workspace_version: {workspace.workspace_version}\n"
        f"object_type: {object_type}\n"
        f"object_id: {object_id or ''}\n"
        f"generated_at: {generated_at.isoformat()}\n"
        "---\n\n"
    )


def _render_product(workspace: SalesWorkspace, generated_at: datetime) -> str:
    profile = workspace.product_profile_revisions.get(workspace.current_product_profile_revision_id or "")
    body = "# Product\n\n"
    if not profile:
        body += "No current product profile.\n"
        return _frontmatter(workspace, "product_profile_revision", None, generated_at) + body

    body += (
        f"- Name: {profile.product_name}\n"
        f"- One-liner: {profile.one_liner}\n"
        f"- Target customers: {_join(profile.target_customers)}\n"
        f"- Target industries: {_join(profile.target_industries)}\n"
        f"- Pain points: {_join(profile.pain_points)}\n"
        f"- Value props: {_join(profile.value_props)}\n"
        f"- Constraints: {_join(profile.constraints)}\n"
    )
    return _frontmatter(workspace, "product_profile_revision", profile.id, generated_at) + body


def _render_direction(workspace: SalesWorkspace, generated_at: datetime) -> str:
    direction = workspace.lead_direction_versions.get(workspace.current_lead_direction_version_id or "")
    body = "# Lead Direction\n\n"
    if not direction:
        body += "No current lead direction.\n"
        return _frontmatter(workspace, "lead_direction_version", None, generated_at) + body

    body += (
        f"- Priority industries: {_join(direction.priority_industries)}\n"
        f"- Target customer types: {_join(direction.target_customer_types)}\n"
        f"- Regions: {_join(direction.regions)}\n"
        f"- Company sizes: {_join(direction.company_sizes)}\n"
        f"- Priority constraints: {_join(direction.priority_constraints)}\n"
        f"- Excluded industries: {_join(direction.excluded_industries)}\n"
        f"- Excluded customer types: {_join(direction.excluded_customer_types)}\n"
        f"- Change reason: {direction.change_reason}\n"
    )
    return _frontmatter(workspace, "lead_direction_version", direction.id, generated_at) + body


def _render_research_round(workspace: SalesWorkspace, round_id: str, generated_at: datetime) -> str:
    research_round = workspace.research_rounds[round_id]
    body = (
        f"# Research Round {research_round.round_index}\n\n"
        f"- Objective: {research_round.objective}\n"
        f"- Summary: {research_round.summary}\n"
        f"- Limitations: {_join(research_round.limitations)}\n\n"
        "## Sources\n\n"
    )
    for source_id in research_round.source_ids:
        source = workspace.research_sources[source_id]
        body += f"- {source.title} ({source.reliability})\n"
    body += "\n## Candidates\n\n"
    for candidate_id in research_round.candidate_ids:
        candidate = workspace.company_candidates[candidate_id]
        body += f"- {candidate.name}: {candidate.summary}\n"
    return _frontmatter(workspace, "research_round", research_round.id, generated_at) + body


def _render_candidates(workspace: SalesWorkspace, generated_at: datetime) -> str:
    body = "# Candidates\n\n| Rank | Candidate | Score | Status | Reason |\n|---:|---|---:|---|---|\n"
    board = workspace.ranking_board
    if board:
        for item in board.ranked_items:
            body += f"| {item.rank} | {item.candidate_name} | {item.score} | {item.status} | {item.reason} |\n"
    return _frontmatter(workspace, "company_candidate_index", "index", generated_at) + body


def _render_rankings(workspace: SalesWorkspace, generated_at: datetime) -> str:
    board = workspace.ranking_board
    body = "# Current Rankings\n\n"
    if not board:
        body += "No ranking board generated.\n"
        return _frontmatter(workspace, "candidate_ranking_board", None, generated_at) + body

    for item in board.ranked_items:
        body += (
            f"## #{item.rank} {item.candidate_name}\n\n"
            f"- Score: {item.score}\n"
            f"- Status: {item.status}\n"
            f"- Reason: {item.reason}\n"
            f"- Supporting observations: {_join(item.supporting_observation_ids)}\n\n"
        )
    body += "## Ranking Delta\n\n"
    for delta in board.deltas:
        body += f"- {delta.reason} Supporting observations: {_join(delta.supporting_observation_ids)}\n"
    return _frontmatter(workspace, "candidate_ranking_board", board.id, generated_at) + body


def _join(values: list[str]) -> str:
    return ", ".join(values) if values else "-"
