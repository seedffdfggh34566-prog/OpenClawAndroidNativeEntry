# Task: V2 Sales Workspace Draft Review Contract

状态：done

更新时间：2026-04-27

## Objective

定义 V2 Sales Workspace 的 Draft persistence / review history contract。

该任务是下一阶段推荐任务，但当前尚未自动开放执行。

## Scope

本任务应定义：

- `WorkspacePatchDraft` 是否成为 backend 可持久化 review object。
- draft lifecycle：
  - `previewed`
  - `reviewed`
  - `applied`
  - `rejected`
  - `expired`
- draft review metadata：
  - reviewer
  - reviewed_at
  - instruction
  - runtime metadata
  - base workspace version
- apply result：
  - materialized patch id
  - resulting workspace version
  - ranking impact summary
  - failure reason
- stale draft / version conflict 语义。
- Android 后续是提交 `draft_id`，还是继续提交 raw `patch_draft`。
- JSON store prototype 是否足以支撑 draft review demo。
- 是否需要刷新 `ADR-007` persistence decision。

## Out Of Scope

- 不实现 backend route。
- 不改 `backend/sales_workspace` code。
- 不改 Android UI。
- 不接 LangGraph。
- 不接真实 LLM。
- 不做 search / contact / CRM。
- 不写 DB schema、SQLAlchemy model 或 Alembic migration。

## Expected Output

- 一份 draft review contract 文档，建议路径：
  - `docs/reference/api/sales-workspace-draft-review-contract.md`
- 必要时新增或更新 ADR addendum，说明 draft review contract 是否改变 persistence decision。
- 更新 `_active.md`，在任务完成后仍不自动开放 implementation。
- 新增 handoff，记录后续是否应进入 DB decision refresh 或 implementation task。

## Result

已完成：

- 新增 `docs/reference/api/sales-workspace-draft-review-contract.md`。
- 定义 `WorkspacePatchDraftReview` backend-managed review object 语义。
- 定义 draft lifecycle：`previewed`、`reviewed`、`applied`、`rejected`、`expired`。
- 定义 future draft review API contract，但未实现 route。
- 更新 ADR-007 addendum，允许 draft review contract，但不改变 persistence baseline。
- 明确 Android 未来推荐通过 `draft_review_id` apply；当前 prototype 仍可 raw `patch_draft` 回传。
- 明确 DB-backed persistence、SQLAlchemy / Alembic、LangGraph、LLM/search/contact/CRM 仍 blocked。

## Validation Criteria

- Contract 明确 draft lifecycle、错误语义、apply 边界和 Android / Runtime 责任边界。
- 明确 Runtime 仍只产出 draft，backend kernel 仍负责正式 workspace writeback。
- 明确是否允许 prototype JSON store 继续支撑下一轮 demo。
- 不引入 code change。

## Actual Validation

- `rg "sales-workspace-draft-review-contract.md|WorkspacePatchDraftReview|draft_review_id" docs`
- `rg "previewed|reviewed|applied|rejected|expired|workspace_version_conflict|stale draft" docs/reference/api/sales-workspace-draft-review-contract.md`
- `rg "不实现 backend route|不改 Android|不写 DB|不接 LangGraph" docs/delivery/tasks/task_v2_sales_workspace_draft_review_contract.md docs/delivery/handoffs/handoff_2026_04_27_v2_draft_review_contract.md`
- `git diff --check`
