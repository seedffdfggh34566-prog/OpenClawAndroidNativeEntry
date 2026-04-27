# Handoff: V2 Sales Workspace Repository Layer v0

日期：2026-04-27

## Summary

本次完成 Sales Workspace Postgres repository layer v0。新增 `PostgresWorkspaceStore`，可将当前 Pydantic `SalesWorkspace` 对象持久化到 Postgres schema，并通过 kernel apply 写入 append-only patch commit。

本次没有切换 API 默认 store。

## Changed

- 新增 `backend/sales_workspace/repository.py`。
- 新增 `backend/tests/test_sales_workspace_repository.py`。
- 更新 task：`task_v2_sales_workspace_repository_layer_v0.md`。
- 更新 `_active.md` 和 `docs/delivery/README.md`，下一项为 API Postgres store v0。

## Behavior

- `create_workspace` / `get` / `save` 与现有 store 接口保持一致。
- `apply_patch` 使用数据库 transaction。
- version conflict 不 mutate workspace。
- patch commit 写入 `sales_workspace_patch_commits`，保持 append-only。
- derived outputs 可在 reload 后继续从 `SalesWorkspace` payload 生成。

## DB Risk Classification

- Risk category：repository / persistence wiring。
- Schema / migration files changed：no in this task。
- SQLAlchemy ORM changed：no；使用 SQLAlchemy Core。
- API route changed：no。
- Postgres involved：yes。
- SQLite runtime fallback：not introduced。

## Validation

- `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_repository.py -q`
- `backend/.venv/bin/python -m pytest backend/tests/sales_workspace -q`
- `git diff --check`

## Known Limitations

- API still uses memory / JSON store unless a later task wires postgres mode.
- Draft Review store is not persisted yet.
- Repository restores workspace from root `payload_json`; relation rows are v0 query / audit support, not the only reconstruction source.

## Recommended Next Step

Continue to `task_v2_sales_workspace_api_postgres_store_v0.md`.
