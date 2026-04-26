from __future__ import annotations

from typing import Any

from backend.sales_workspace.ranking import derive_candidate_ranking
from backend.sales_workspace.schemas import (
    CandidateObservation,
    CompanyCandidate,
    LeadDirectionVersion,
    ProductProfileRevision,
    ResearchRound,
    ResearchSource,
    SalesWorkspace,
    WorkspaceCommit,
    WorkspacePatch,
    utc_now,
)


class WorkspacePatchError(ValueError):
    pass


class WorkspaceVersionConflict(WorkspacePatchError):
    pass


ALLOWED_OPERATION_TYPES = {
    "upsert_product_profile_revision",
    "upsert_lead_direction_version",
    "upsert_research_round",
    "upsert_research_source",
    "upsert_company_candidate",
    "upsert_candidate_observation",
    "archive_candidate",
    "set_active_lead_direction",
}


def apply_workspace_patch(workspace: SalesWorkspace, patch: WorkspacePatch) -> SalesWorkspace:
    if patch.workspace_id != workspace.id:
        raise WorkspacePatchError("patch workspace_id does not match workspace")
    if patch.base_workspace_version != workspace.workspace_version:
        raise WorkspaceVersionConflict(
            f"base_workspace_version {patch.base_workspace_version} does not match current "
            f"workspace_version {workspace.workspace_version}"
        )

    working = workspace.model_copy(deep=True)
    changed_refs: list[str] = []

    for operation in patch.operations:
        if operation.type not in ALLOWED_OPERATION_TYPES:
            raise WorkspacePatchError(f"unsupported workspace operation: {operation.type}")

        changed_refs.extend(_apply_operation(working, operation.type, operation.payload))

    working.workspace_version += 1
    working.updated_at = utc_now()
    working.ranking_board = derive_candidate_ranking(working)
    working.current_candidate_ranking_board_id = working.ranking_board.id
    working.commits.append(
        WorkspaceCommit(
            id=f"commit_v{working.workspace_version}",
            workspace_id=working.id,
            patch_id=patch.id,
            workspace_version=working.workspace_version,
            message=patch.message,
            changed_object_refs=changed_refs,
        )
    )
    return working


def _apply_operation(workspace: SalesWorkspace, operation_type: str, payload: dict[str, Any]) -> list[str]:
    if operation_type == "upsert_product_profile_revision":
        revision = ProductProfileRevision(**_with_workspace_id(workspace, payload))
        workspace.product_profile_revisions[revision.id] = revision
        workspace.current_product_profile_revision_id = revision.id
        return [f"ProductProfileRevision:{revision.id}"]

    if operation_type == "upsert_lead_direction_version":
        direction = LeadDirectionVersion(**_with_workspace_id(workspace, payload))
        workspace.lead_direction_versions[direction.id] = direction
        workspace.current_lead_direction_version_id = direction.id
        return [f"LeadDirectionVersion:{direction.id}"]

    if operation_type == "set_active_lead_direction":
        direction_id = _require(payload, "lead_direction_version_id")
        if direction_id not in workspace.lead_direction_versions:
            raise WorkspacePatchError(f"unknown lead direction: {direction_id}")
        workspace.current_lead_direction_version_id = direction_id
        return [f"LeadDirectionVersion:{direction_id}"]

    if operation_type == "upsert_research_round":
        research_round = ResearchRound(**_with_workspace_id(workspace, payload))
        workspace.research_rounds[research_round.id] = research_round
        workspace.latest_research_round_id = research_round.id
        return [f"ResearchRound:{research_round.id}"]

    if operation_type == "upsert_research_source":
        source = ResearchSource(**_with_workspace_id(workspace, payload))
        if source.round_id not in workspace.research_rounds:
            raise WorkspacePatchError(f"source references unknown research round: {source.round_id}")
        workspace.research_sources[source.id] = source
        _append_unique(workspace.research_rounds[source.round_id].source_ids, source.id)
        return [f"ResearchSource:{source.id}"]

    if operation_type == "upsert_company_candidate":
        candidate = CompanyCandidate(**_with_workspace_id(workspace, payload))
        existing = workspace.company_candidates.get(candidate.id)
        if existing:
            candidate.created_at = existing.created_at
            candidate.round_ids = sorted(set(existing.round_ids + candidate.round_ids))
        workspace.company_candidates[candidate.id] = candidate
        for round_id in candidate.round_ids:
            if round_id not in workspace.research_rounds:
                raise WorkspacePatchError(f"candidate references unknown research round: {round_id}")
            _append_unique(workspace.research_rounds[round_id].candidate_ids, candidate.id)
        return [f"CompanyCandidate:{candidate.id}"]

    if operation_type == "upsert_candidate_observation":
        observation = CandidateObservation(**_with_workspace_id(workspace, payload))
        if observation.candidate_id not in workspace.company_candidates:
            raise WorkspacePatchError(f"observation references unknown candidate: {observation.candidate_id}")
        if observation.source_id not in workspace.research_sources:
            raise WorkspacePatchError(f"observation references unknown source: {observation.source_id}")
        if observation.round_id not in workspace.research_rounds:
            raise WorkspacePatchError(f"observation references unknown research round: {observation.round_id}")
        workspace.candidate_observations[observation.id] = observation
        candidate = workspace.company_candidates[observation.candidate_id]
        _append_unique(candidate.round_ids, observation.round_id)
        _append_unique(workspace.research_rounds[observation.round_id].candidate_ids, observation.candidate_id)
        _append_unique(workspace.research_rounds[observation.round_id].source_ids, observation.source_id)
        return [f"CandidateObservation:{observation.id}"]

    if operation_type == "archive_candidate":
        candidate_id = _require(payload, "candidate_id")
        if candidate_id not in workspace.company_candidates:
            raise WorkspacePatchError(f"unknown candidate: {candidate_id}")
        candidate = workspace.company_candidates[candidate_id]
        workspace.company_candidates[candidate_id] = candidate.model_copy(
            update={"status": "archived", "updated_at": utc_now()}
        )
        return [f"CompanyCandidate:{candidate_id}"]

    raise WorkspacePatchError(f"unsupported workspace operation: {operation_type}")


def _with_workspace_id(workspace: SalesWorkspace, payload: dict[str, Any]) -> dict[str, Any]:
    merged = dict(payload)
    existing_workspace_id = merged.get("workspace_id")
    if existing_workspace_id and existing_workspace_id != workspace.id:
        raise WorkspacePatchError("operation payload workspace_id does not match workspace")
    merged["workspace_id"] = workspace.id
    return merged


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def _require(payload: dict[str, Any], key: str) -> Any:
    value = payload.get(key)
    if value is None:
        raise WorkspacePatchError(f"missing required payload field: {key}")
    return value
