import pytest

from backend.sales_workspace.context_pack import compile_context_pack
from backend.tests.sales_workspace.test_sales_workspace_kernel_e2e import build_two_round_workspace


def test_context_pack_uses_structured_workspace_state():
    workspace = build_two_round_workspace()

    context_pack = compile_context_pack(workspace, token_budget_chars=6000, top_n_candidates=2)

    assert context_pack.task_type == "research_round"
    assert context_pack.top_candidates[0].candidate_id == "cand_d"
    assert context_pack.recent_ranking_delta
    assert "WorkspacePatchDraft" in context_pack.kernel_boundary


def test_context_pack_rejects_unknown_task_type():
    workspace = build_two_round_workspace()

    with pytest.raises(ValueError):
        compile_context_pack(workspace, task_type="report_generation")
