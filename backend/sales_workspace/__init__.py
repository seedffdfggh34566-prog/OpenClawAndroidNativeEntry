"""Backend-only Sales Workspace Kernel v0."""

from backend.sales_workspace.context_pack import compile_context_pack
from backend.sales_workspace.patches import apply_workspace_patch
from backend.sales_workspace.projection import render_markdown_projection
from backend.sales_workspace.ranking import derive_candidate_ranking
from backend.sales_workspace.schemas import (
    CandidateObservation,
    CandidateRankingBoard,
    CompanyCandidate,
    ContextPack,
    LeadDirectionVersion,
    ProductProfileRevision,
    ResearchRound,
    ResearchSource,
    SalesWorkspace,
    WorkspaceCommit,
    WorkspaceOperation,
    WorkspacePatch,
)
from backend.sales_workspace.store import InMemoryWorkspaceStore

__all__ = [
    "CandidateObservation",
    "CandidateRankingBoard",
    "CompanyCandidate",
    "ContextPack",
    "InMemoryWorkspaceStore",
    "LeadDirectionVersion",
    "ProductProfileRevision",
    "ResearchRound",
    "ResearchSource",
    "SalesWorkspace",
    "WorkspaceCommit",
    "WorkspaceOperation",
    "WorkspacePatch",
    "apply_workspace_patch",
    "compile_context_pack",
    "derive_candidate_ranking",
    "render_markdown_projection",
]
