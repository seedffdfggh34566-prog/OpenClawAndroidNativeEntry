from backend.sales_workspace.context_pack import compile_context_pack
from backend.sales_workspace.projection import render_markdown_projection
from backend.sales_workspace.schemas import WorkspaceOperation, WorkspacePatch
from backend.sales_workspace.store import InMemoryWorkspaceStore


def build_two_round_workspace():
    store = InMemoryWorkspaceStore()
    workspace = store.create_workspace(
        workspace_id="ws_demo",
        name="Demo sales workspace",
        goal="Find source-backed manufacturing ERP candidates",
    )

    workspace = store.apply_patch(
        WorkspacePatch(
            id="patch_product_direction",
            workspace_id=workspace.id,
            base_workspace_version=workspace.workspace_version,
            message="Add product and lead direction",
            operations=[
                WorkspaceOperation(
                    type="upsert_product_profile_revision",
                    payload={
                        "id": "prod_v1",
                        "product_name": "FactoryOps AI",
                        "one_liner": "AI assistant for factory operations and sales follow-up.",
                        "target_customers": ["manufacturing SMEs"],
                        "target_industries": ["industrial manufacturing"],
                        "pain_points": ["manual production follow-up", "slow quotation coordination"],
                        "value_props": ["reduce sales operations workload", "surface high-fit accounts"],
                        "constraints": ["China public-web source evidence required"],
                    },
                ),
                WorkspaceOperation(
                    type="upsert_lead_direction_version",
                    payload={
                        "id": "dir_v1",
                        "priority_industries": ["industrial manufacturing", "precision components"],
                        "target_customer_types": ["owner-led SME", "operations-heavy factory"],
                        "regions": ["Jiangsu", "Zhejiang"],
                        "company_sizes": ["50-500 employees"],
                        "priority_constraints": ["must show public evidence"],
                        "change_reason": "Focus on factories with operations pressure and buying urgency.",
                    },
                ),
            ],
        )
    )

    workspace = store.apply_patch(
        WorkspacePatch(
            id="patch_round_1",
            workspace_id=workspace.id,
            base_workspace_version=workspace.workspace_version,
            message="Round 1 candidates",
            operations=[
                WorkspaceOperation(
                    type="upsert_research_round",
                    payload={
                        "id": "rr_001",
                        "round_index": 1,
                        "objective": "Find initial manufacturing candidates.",
                        "summary": "Candidate A shows clear fit; B is weaker.",
                    },
                ),
                WorkspaceOperation(
                    type="upsert_research_source",
                    payload={
                        "id": "src_a_1",
                        "round_id": "rr_001",
                        "title": "A company manufacturing profile",
                        "url": "https://example.com/a",
                        "reliability": "medium",
                        "excerpt": "A company describes production coordination needs.",
                    },
                ),
                WorkspaceOperation(
                    type="upsert_research_source",
                    payload={
                        "id": "src_b_1",
                        "round_id": "rr_001",
                        "title": "B company directory entry",
                        "url": "https://example.com/b",
                        "reliability": "low",
                        "excerpt": "B company is listed as a generic manufacturer.",
                    },
                ),
                WorkspaceOperation(
                    type="upsert_company_candidate",
                    payload={
                        "id": "cand_a",
                        "name": "A Company",
                        "summary": "Manufacturing SME with visible operations pain.",
                        "industry": "industrial manufacturing",
                        "region": "Jiangsu",
                        "company_size": "100 employees",
                        "round_ids": ["rr_001"],
                    },
                ),
                WorkspaceOperation(
                    type="upsert_company_candidate",
                    payload={
                        "id": "cand_b",
                        "name": "B Company",
                        "summary": "Generic manufacturer with weak evidence.",
                        "industry": "industrial manufacturing",
                        "region": "Shanghai",
                        "company_size": "80 employees",
                        "round_ids": ["rr_001"],
                    },
                ),
                WorkspaceOperation(
                    type="upsert_candidate_observation",
                    payload={
                        "id": "obs_a_fit",
                        "candidate_id": "cand_a",
                        "source_id": "src_a_1",
                        "round_id": "rr_001",
                        "signal_type": "fit",
                        "strength": 3,
                        "summary": "A matches target manufacturing SME profile.",
                    },
                ),
                WorkspaceOperation(
                    type="upsert_candidate_observation",
                    payload={
                        "id": "obs_a_pain",
                        "candidate_id": "cand_a",
                        "source_id": "src_a_1",
                        "round_id": "rr_001",
                        "signal_type": "pain",
                        "strength": 2,
                        "summary": "A shows manual production follow-up pain.",
                    },
                ),
                WorkspaceOperation(
                    type="upsert_candidate_observation",
                    payload={
                        "id": "obs_b_fit",
                        "candidate_id": "cand_b",
                        "source_id": "src_b_1",
                        "round_id": "rr_001",
                        "signal_type": "fit",
                        "strength": 1,
                        "summary": "B is in a relevant industry but evidence is thin.",
                    },
                ),
            ],
        )
    )

    assert workspace.ranking_board.ranked_items[0].candidate_id == "cand_a"

    workspace = store.apply_patch(
        WorkspacePatch(
            id="patch_round_2",
            workspace_id=workspace.id,
            base_workspace_version=workspace.workspace_version,
            message="Round 2 stronger candidate",
            operations=[
                WorkspaceOperation(
                    type="upsert_research_round",
                    payload={
                        "id": "rr_002",
                        "round_index": 2,
                        "objective": "Find stronger candidates in Jiangsu/Zhejiang.",
                        "summary": "D has stronger evidence across fit, pain, timing, region, and source quality.",
                    },
                ),
                WorkspaceOperation(
                    type="upsert_research_source",
                    payload={
                        "id": "src_d_1",
                        "round_id": "rr_002",
                        "title": "D company public case page",
                        "url": "https://example.com/d",
                        "reliability": "high",
                        "excerpt": "D company publicly describes urgent digital operations needs in Zhejiang.",
                    },
                ),
                WorkspaceOperation(
                    type="upsert_company_candidate",
                    payload={
                        "id": "cand_d",
                        "name": "D Company",
                        "summary": "Zhejiang manufacturer with urgent operations digitization pressure.",
                        "industry": "precision components",
                        "region": "Zhejiang",
                        "company_size": "200 employees",
                        "round_ids": ["rr_002"],
                    },
                ),
                *[
                    WorkspaceOperation(
                        type="upsert_candidate_observation",
                        payload={
                            "id": f"obs_d_{signal}",
                            "candidate_id": "cand_d",
                            "source_id": "src_d_1",
                            "round_id": "rr_002",
                            "signal_type": signal,
                            "strength": strength,
                            "summary": f"D has strong {signal} evidence.",
                        },
                    )
                    for signal, strength in [
                        ("fit", 3),
                        ("pain", 3),
                        ("timing", 2),
                        ("region", 2),
                        ("source_quality", 1),
                    ]
                ],
            ],
        )
    )
    return workspace


def test_workspace_kernel_v0_two_round_research_reranks_candidate():
    workspace = build_two_round_workspace()

    top_item = workspace.ranking_board.ranked_items[0]
    assert top_item.candidate_id == "cand_d"

    d_delta = next(delta for delta in workspace.ranking_board.deltas if delta.candidate_id == "cand_d")
    assert d_delta.new_rank == 1
    assert d_delta.supporting_observation_ids

    projection = render_markdown_projection(workspace)
    assert len(projection) >= 5
    assert "rankings/current.md" in projection
    assert "D Company" in projection["rankings/current.md"]

    context_pack = compile_context_pack(workspace)
    assert context_pack.top_candidates[0].candidate_id == "cand_d"
    assert "FactoryOps AI" in context_pack.product_summary
    assert "Zhejiang" in context_pack.current_direction
