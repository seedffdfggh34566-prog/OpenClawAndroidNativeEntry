from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class KernelModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProductProfileRevision(KernelModel):
    id: str
    workspace_id: str
    version: int = 1
    product_name: str
    one_liner: str = ""
    target_customers: list[str] = Field(default_factory=list)
    target_industries: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    value_props: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class LeadDirectionVersion(KernelModel):
    id: str
    workspace_id: str
    version: int = 1
    priority_industries: list[str] = Field(default_factory=list)
    target_customer_types: list[str] = Field(default_factory=list)
    regions: list[str] = Field(default_factory=list)
    company_sizes: list[str] = Field(default_factory=list)
    priority_constraints: list[str] = Field(default_factory=list)
    excluded_industries: list[str] = Field(default_factory=list)
    excluded_customer_types: list[str] = Field(default_factory=list)
    change_reason: str = ""
    created_at: datetime = Field(default_factory=utc_now)


class ResearchRound(KernelModel):
    id: str
    workspace_id: str
    round_index: int
    objective: str
    summary: str = ""
    limitations: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    candidate_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class ResearchSource(KernelModel):
    id: str
    workspace_id: str
    round_id: str
    title: str
    url: str | None = None
    source_type: str = "public_web"
    reliability: Literal["low", "medium", "high"] = "medium"
    excerpt: str = ""
    collected_at: datetime = Field(default_factory=utc_now)


class CompanyCandidate(KernelModel):
    id: str
    workspace_id: str
    name: str
    summary: str = ""
    industry: str = ""
    region: str = ""
    company_size: str = ""
    status: Literal["active", "archived"] = "active"
    round_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class CandidateObservation(KernelModel):
    id: str
    workspace_id: str
    candidate_id: str
    source_id: str
    round_id: str
    signal_type: Literal["fit", "pain", "timing", "region", "source_quality", "exclusion", "other"]
    summary: str
    polarity: Literal["positive", "negative"] = "positive"
    strength: int = Field(default=1, ge=1, le=5)
    created_at: datetime = Field(default_factory=utc_now)


class CandidateRankingItem(KernelModel):
    candidate_id: str
    candidate_name: str
    rank: int
    score: int
    status: Literal["active", "archived"]
    reason: str
    supporting_observation_ids: list[str] = Field(default_factory=list)
    score_breakdown: dict[str, int] = Field(default_factory=dict)


class RankingDelta(KernelModel):
    candidate_id: str
    previous_rank: int | None = None
    new_rank: int
    previous_score: int = 0
    new_score: int
    reason: str
    supporting_observation_ids: list[str] = Field(default_factory=list)


class CandidateRankingBoard(KernelModel):
    id: str
    workspace_id: str
    workspace_version: int
    ranked_items: list[CandidateRankingItem] = Field(default_factory=list)
    deltas: list[RankingDelta] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)


class WorkspaceOperation(KernelModel):
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class WorkspacePatch(KernelModel):
    id: str
    workspace_id: str
    base_workspace_version: int
    operations: list[WorkspaceOperation]
    author: str = "kernel_v0_test"
    message: str = ""
    created_at: datetime = Field(default_factory=utc_now)

    @field_validator("operations")
    @classmethod
    def operations_must_not_be_empty(cls, value: list[WorkspaceOperation]) -> list[WorkspaceOperation]:
        if not value:
            raise ValueError("WorkspacePatch.operations must not be empty")
        return value


class WorkspaceCommit(KernelModel):
    id: str
    workspace_id: str
    patch_id: str
    workspace_version: int
    message: str
    changed_object_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class SalesWorkspace(KernelModel):
    id: str
    workspace_key: str = "local_default"
    owner_id: str = "local_user"
    name: str
    goal: str = ""
    status: Literal["active", "archived"] = "active"
    workspace_version: int = 0
    current_product_profile_revision_id: str | None = None
    current_lead_direction_version_id: str | None = None
    current_candidate_ranking_board_id: str | None = None
    latest_research_round_id: str | None = None
    product_profile_revisions: dict[str, ProductProfileRevision] = Field(default_factory=dict)
    lead_direction_versions: dict[str, LeadDirectionVersion] = Field(default_factory=dict)
    research_rounds: dict[str, ResearchRound] = Field(default_factory=dict)
    research_sources: dict[str, ResearchSource] = Field(default_factory=dict)
    company_candidates: dict[str, CompanyCandidate] = Field(default_factory=dict)
    candidate_observations: dict[str, CandidateObservation] = Field(default_factory=dict)
    ranking_board: CandidateRankingBoard | None = None
    commits: list[WorkspaceCommit] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ContextPackCandidate(KernelModel):
    candidate_id: str
    name: str
    rank: int
    score: int
    reason: str
    supporting_observation_ids: list[str] = Field(default_factory=list)


class ContextPack(KernelModel):
    id: str
    workspace_id: str
    task_type: Literal["research_round"] = "research_round"
    token_budget_chars: int = 6000
    product_summary: str
    current_direction: str
    top_candidates: list[ContextPackCandidate] = Field(default_factory=list)
    recent_ranking_delta: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    kernel_boundary: str = (
        "Runtime / Product Sales Agent execution layer returns WorkspacePatchDraft; "
        "Sales Workspace Kernel validates and writes formal objects."
    )
    generated_at: datetime = Field(default_factory=utc_now)
