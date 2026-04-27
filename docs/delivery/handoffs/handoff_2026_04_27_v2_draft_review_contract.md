# Handoff: V2 Draft Review Contract

日期：2026-04-27

## Summary

本次完成 `WorkspacePatchDraft` review contract。

核心结论：

- `WorkspacePatchDraft` 应进入 backend-managed review object 语义。
- 新对象语义命名为 `WorkspacePatchDraftReview`。
- Draft lifecycle 为 `previewed`、`reviewed`、`applied`、`rejected`、`expired`。
- Android 未来推荐通过 `draft_review_id` 执行 review / apply。
- 当前 prototype 仍可继续 raw `patch_draft` 回传。
- Runtime / Product Sales Agent execution layer 仍只产出 draft。
- Sales Workspace Kernel 仍负责正式 workspace writeback。

## Files Changed

- `docs/reference/api/sales-workspace-draft-review-contract.md`
- `docs/reference/README.md`
- `docs/adr/ADR-007-v2-sales-workspace-persistence-decision.md`
- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_contract.md`
- `docs/delivery/tasks/_active.md`

## Contract Notes

Future API contract targets were defined but not implemented:

- `POST /sales-workspaces/{workspace_id}/draft-reviews`
- `GET /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}`
- `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/review`
- `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/apply`
- `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/reject`

The contract also defines:

- review metadata
- runtime metadata
- preview ranking
- materialized patch preview
- apply result
- stale draft / version conflict behavior
- rejected / applied terminal-state behavior

## Validation

- `rg "sales-workspace-draft-review-contract.md|WorkspacePatchDraftReview|draft_review_id" docs`
- `rg "previewed|reviewed|applied|rejected|expired|workspace_version_conflict|stale draft" docs/reference/api/sales-workspace-draft-review-contract.md`
- `rg "不实现 backend route|不改 Android|不写 DB|不接 LangGraph" docs/delivery/tasks/task_v2_sales_workspace_draft_review_contract.md docs/delivery/handoffs/handoff_2026_04_27_v2_draft_review_contract.md`
- `git diff --check`

## Still Blocked

- Backend route implementation。
- SQLAlchemy / Alembic / SQLite schema。
- Production persistence baseline。
- Formal LangGraph graph。
- Real LLM / search / contact / CRM。
- Android UI changes。

## Recommended Next Step

Choose one next task explicitly:

1. Persistence decision refresh for draft review object。
2. Prototype draft review routes using JSON store。
3. Formal Runtime / LangGraph integration design against `WorkspacePatchDraftReview`。
4. Android review UX expansion after backend review object exists。

