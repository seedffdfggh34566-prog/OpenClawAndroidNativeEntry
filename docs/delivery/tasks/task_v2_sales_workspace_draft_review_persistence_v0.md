# Task: V2 Sales Workspace Draft Review Persistence v0

状态：planned / blocked

更新时间：2026-04-27

## Objective

将 backend-managed Draft Review object 与 lifecycle events 落入 Postgres persistence。

## Blocker

必须等待 persistence migration v0 与 repository layer v0 完成。

## Scope Placeholder

- 持久化 `sales_workspace_draft_reviews`。
- 持久化 `sales_workspace_draft_review_events` append-only lifecycle log。
- 支持 previewed / reviewed / applied / rejected / expired 状态。
- 保留 Android Draft Review ID flow 的接口语义。

## Out Of Scope Until Unblocked

- 不新增 Android review history UI。
- 不接正式 Runtime / LangGraph。
- 不接 LLM / search / CRM / contact。
