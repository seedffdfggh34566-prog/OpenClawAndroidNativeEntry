# Task: V2 Sales Workspace API Postgres Store v0

状态：done

更新时间：2026-04-27

## Objective

将 Sales Workspace API prototype 从 in-memory / JSON prototype store 切到 Postgres-backed repository。

## Blocker

已由长线程执行计划开放，且 persistence migration v0 与 repository layer v0 已完成。

## Scope

- 保持已冻结 API contract。
- 使用 Postgres repository 作为 explicit store backend。
- 保留 prototype store 的本地 demo 兼容策略。
- 覆盖 version conflict、not found、validation error、derived output 读取。

## Result

已完成：

- 新增配置 `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND=memory|json|postgres`。
- 未设置 backend 时保留原行为：
  - 无 `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR`：memory。
  - 有 `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR`：json。
- 显式 `postgres` 时，Sales Workspace API 使用 `PostgresWorkspaceStore`。
- API endpoint path、response envelope、error code 与既有 contract 保持不变。
- 新增 Postgres-mode API tests：`backend/tests/test_sales_workspace_api_postgres_store.py`。

## Actual Validation

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_api.py -q`
- `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_api_postgres_store.py -q`
- `git diff --check`

## Out Of Scope Until Unblocked

- 不改 Android write flow。
- 不接 Runtime / LangGraph 正式 graph。
- 不接 LLM / search / CRM / contact。
- 不实现 multi-user permission。
