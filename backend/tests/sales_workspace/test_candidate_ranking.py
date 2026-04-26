from backend.sales_workspace.patches import apply_workspace_patch
from backend.sales_workspace.schemas import SalesWorkspace, WorkspaceOperation, WorkspacePatch


def test_archived_candidate_is_removed_from_derived_ranking():
    workspace = SalesWorkspace(id="ws_rank", name="Ranking workspace")
    workspace = apply_workspace_patch(
        workspace,
        WorkspacePatch(
            id="patch_rank",
            workspace_id=workspace.id,
            base_workspace_version=0,
            operations=[
                WorkspaceOperation(
                    type="upsert_research_round",
                    payload={"id": "rr_001", "round_index": 1, "objective": "Find candidates"},
                ),
                WorkspaceOperation(
                    type="upsert_research_source",
                    payload={
                        "id": "src_1",
                        "round_id": "rr_001",
                        "title": "Source",
                        "reliability": "high",
                    },
                ),
                WorkspaceOperation(
                    type="upsert_company_candidate",
                    payload={"id": "cand_live", "name": "Live Candidate", "round_ids": ["rr_001"]},
                ),
                WorkspaceOperation(
                    type="upsert_company_candidate",
                    payload={"id": "cand_archive", "name": "Archive Candidate", "round_ids": ["rr_001"]},
                ),
                WorkspaceOperation(
                    type="upsert_candidate_observation",
                    payload={
                        "id": "obs_live",
                        "candidate_id": "cand_live",
                        "source_id": "src_1",
                        "round_id": "rr_001",
                        "signal_type": "fit",
                        "summary": "Live candidate fits.",
                    },
                ),
                WorkspaceOperation(
                    type="upsert_candidate_observation",
                    payload={
                        "id": "obs_archive",
                        "candidate_id": "cand_archive",
                        "source_id": "src_1",
                        "round_id": "rr_001",
                        "signal_type": "fit",
                        "summary": "Archived candidate would fit.",
                    },
                ),
                WorkspaceOperation(type="archive_candidate", payload={"candidate_id": "cand_archive"}),
            ],
        ),
    )

    ranked_ids = [item.candidate_id for item in workspace.ranking_board.ranked_items]
    assert ranked_ids == ["cand_live"]


def test_tied_scores_are_sorted_by_candidate_id():
    workspace = SalesWorkspace(id="ws_rank", name="Ranking workspace")
    workspace = apply_workspace_patch(
        workspace,
        WorkspacePatch(
            id="patch_tie",
            workspace_id=workspace.id,
            base_workspace_version=0,
            operations=[
                WorkspaceOperation(
                    type="upsert_research_round",
                    payload={"id": "rr_001", "round_index": 1, "objective": "Find candidates"},
                ),
                WorkspaceOperation(
                    type="upsert_research_source",
                    payload={"id": "src_1", "round_id": "rr_001", "title": "Source"},
                ),
                WorkspaceOperation(
                    type="upsert_company_candidate",
                    payload={"id": "cand_b", "name": "B", "round_ids": ["rr_001"]},
                ),
                WorkspaceOperation(
                    type="upsert_company_candidate",
                    payload={"id": "cand_a", "name": "A", "round_ids": ["rr_001"]},
                ),
            ],
        ),
    )

    assert [item.candidate_id for item in workspace.ranking_board.ranked_items] == ["cand_a", "cand_b"]
