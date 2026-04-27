# Task: V2 Sales Workspace Draft Review Persistence v0

状态：done

更新时间：2026-04-27

## Objective

将 backend-managed Draft Review object 与 lifecycle events 落入 Postgres persistence。

## Blocker

已由长线程执行计划开放，且 persistence migration v0、repository layer v0、API Postgres store v0 已完成。

## Scope

- 持久化 `sales_workspace_draft_reviews`。
- 持久化 `sales_workspace_draft_review_events` append-only lifecycle log。
- 支持 previewed / reviewed / applied / rejected / expired 状态。
- 保留 Android Draft Review ID flow 的接口语义。

## Result

已完成：

- 新增 `PostgresDraftReviewStore`。
- `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND=postgres` 时，Draft Review routes 使用 Postgres review store。
- `sales_workspace_draft_reviews` 保存当前 backend-managed review object。
- `sales_workspace_draft_review_events` 记录 append-only lifecycle events。
- 覆盖事件类型：`created`、`reviewed`、`rejected`、`applied`、`expired`、`apply_failed`。
- Android review-id flow 的 endpoint、request / response shape 与既有语义保持不变。
- memory / JSON prototype path 保持不变。

## Actual Validation

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_draft_reviews_api.py -q`
- `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_draft_reviews_postgres_store.py -q`
- `git diff --check`

## Out Of Scope Until Unblocked

- 不新增 Android review history UI。
- 不接正式 Runtime / LangGraph。
- 不接 LLM / search / CRM / contact。
