from backend.sales_workspace.projection import render_markdown_projection
from backend.tests.sales_workspace.test_sales_workspace_kernel_e2e import build_two_round_workspace


def test_markdown_projection_renders_v0_workspace_files():
    workspace = build_two_round_workspace()

    projection = render_markdown_projection(workspace)

    assert "product/current.md" in projection
    assert "directions/current.md" in projection
    assert "research/rounds/rr_001.md" in projection
    assert "research/rounds/rr_002.md" in projection
    assert "candidates/index.md" in projection
    assert "rankings/current.md" in projection
    assert "generated: true" in projection["product/current.md"]
    assert "| 1 | D Company |" in projection["candidates/index.md"]
    assert "obs_d_fit" in projection["rankings/current.md"]
