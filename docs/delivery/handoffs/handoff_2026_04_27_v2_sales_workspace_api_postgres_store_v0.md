# Handoff: V2 Sales Workspace API Postgres Store v0

日期：2026-04-27

## Summary

本次完成 Sales Workspace API Postgres store v0。API contract 不变，默认 memory/json prototype path 保持兼容；只有显式设置 `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND=postgres` 时，Sales Workspace API 才使用 Postgres repository。

## Changed

- 更新 `backend/api/config.py`，新增 `sales_workspace_store_backend`。
- 更新 `backend/api/sales_workspace.py`，store factory 支持 `memory` / `json` / `postgres`。
- 更新 `backend/tests/conftest.py`，默认测试清理 store backend env。
- 新增 `backend/tests/test_sales_workspace_api_postgres_store.py`。
- 更新 task：`task_v2_sales_workspace_api_postgres_store_v0.md`。
- 更新 `_active.md` 和 `docs/delivery/README.md`，下一项为 Draft Review persistence v0。

## Behavior

- `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND` 未设置且无 store dir：使用 app-local memory store。
- `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND` 未设置且有 store dir：使用 JSON file store。
- 显式 `postgres`：使用 `PostgresWorkspaceStore`。
- API endpoint、response shape 和 error envelope 未改变。
- Draft Review store 本任务仍保持 memory/json path，Postgres persistence 由下一项任务完成。

## Validation

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_api.py -q`
- `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_api_postgres_store.py -q`
- `git diff --check`

## Known Limitations

- Draft Review lifecycle 仍未落入 Postgres。
- `postgres` store backend 是显式 opt-in，不自动替代 memory/json demo path。
- 本任务没有新增 API route、Android UI、Runtime / LangGraph、LLM / search / CRM / contact。

## Recommended Next Step

Continue to `task_v2_sales_workspace_draft_review_persistence_v0.md`.
