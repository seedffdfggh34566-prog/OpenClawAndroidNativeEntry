# Task: V2 Sales Workspace Draft Review Persistence Schema

状态：done / folded into persistence schema design

更新时间：2026-04-27

## Objective

为 `WorkspacePatchDraftReview` 设计正式 persistence schema。

## Result

已并入 `task_v2_sales_workspace_persistence_schema_design.md` 完成。

正式 schema design 见：

- `docs/architecture/workspace/sales-workspace-persistence-schema.md`

Draft Review 首版 schema 由以下表承载：

- `sales_workspace_draft_reviews`
- `sales_workspace_draft_review_events`

后续实现任务改为：

- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_persistence_v0.md`

## Scope Placeholder

- Draft Review lifecycle schema。
- review / apply result / failure reason persistence。
- base workspace version 与 stale draft 处理。
- audit trail 与 future Android review history 读取需求。

## Out Of Scope Until Unblocked

- 不写 SQLAlchemy model。
- 不写 Alembic migration。
- 不改 backend route。
- 不改 Android。
