import pytest

from backend.sales_workspace.patches import WorkspacePatchError, WorkspaceVersionConflict, apply_workspace_patch
from backend.sales_workspace.schemas import SalesWorkspace, WorkspaceOperation, WorkspacePatch


def test_patch_increments_version_and_records_commit():
    workspace = SalesWorkspace(id="ws_patch", name="Patch workspace")
    patch = WorkspacePatch(
        id="patch_1",
        workspace_id=workspace.id,
        base_workspace_version=0,
        message="Add product",
        operations=[
            WorkspaceOperation(
                type="upsert_product_profile_revision",
                payload={
                    "id": "prod_1",
                    "product_name": "Demo Product",
                    "one_liner": "A test product.",
                },
            )
        ],
    )

    updated = apply_workspace_patch(workspace, patch)

    assert updated.workspace_version == 1
    assert updated.current_product_profile_revision_id == "prod_1"
    assert updated.commits[0].patch_id == "patch_1"
    assert workspace.workspace_version == 0


def test_version_mismatch_rejects_patch_without_mutating_workspace():
    workspace = SalesWorkspace(id="ws_patch", name="Patch workspace", workspace_version=2)
    patch = WorkspacePatch(
        id="patch_stale",
        workspace_id=workspace.id,
        base_workspace_version=1,
        operations=[
            WorkspaceOperation(
                type="upsert_product_profile_revision",
                payload={"id": "prod_1", "product_name": "Demo Product"},
            )
        ],
    )

    with pytest.raises(WorkspaceVersionConflict):
        apply_workspace_patch(workspace, patch)

    assert workspace.current_product_profile_revision_id is None


def test_observation_requires_existing_source():
    workspace = SalesWorkspace(
        id="ws_patch",
        name="Patch workspace",
        company_candidates={
            "cand_1": {
                "id": "cand_1",
                "workspace_id": "ws_patch",
                "name": "Candidate 1",
            }
        },
        research_rounds={
            "rr_001": {
                "id": "rr_001",
                "workspace_id": "ws_patch",
                "round_index": 1,
                "objective": "Find candidates",
            }
        },
    )
    patch = WorkspacePatch(
        id="patch_bad_observation",
        workspace_id=workspace.id,
        base_workspace_version=0,
        operations=[
            WorkspaceOperation(
                type="upsert_candidate_observation",
                payload={
                    "id": "obs_1",
                    "candidate_id": "cand_1",
                    "source_id": "missing_source",
                    "round_id": "rr_001",
                    "signal_type": "fit",
                    "summary": "Missing source should reject.",
                },
            )
        ],
    )

    with pytest.raises(WorkspacePatchError):
        apply_workspace_patch(workspace, patch)


def test_ranking_board_cannot_be_patched_directly():
    workspace = SalesWorkspace(id="ws_patch", name="Patch workspace")
    patch = WorkspacePatch(
        id="patch_ranking",
        workspace_id=workspace.id,
        base_workspace_version=0,
        operations=[
            WorkspaceOperation(
                type="upsert_candidate_ranking_board",
                payload={"id": "board_manual"},
            )
        ],
    )

    with pytest.raises(WorkspacePatchError):
        apply_workspace_patch(workspace, patch)
