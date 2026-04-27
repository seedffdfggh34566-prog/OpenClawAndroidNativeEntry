# Handoff: V2 Sales Workspace Postgres Persistence Chain

日期：2026-04-27

## Summary

本次长线程完成从 schema migration 到 Draft Review persistence 的 Postgres persistence chain。四个任务按顺序完成并分别提交：migration v0、repository layer v0、API Postgres store v0、Draft Review persistence v0。

## Completed Tasks

- `task_v2_sales_workspace_persistence_migration_v0.md`
- `task_v2_sales_workspace_repository_layer_v0.md`
- `task_v2_sales_workspace_api_postgres_store_v0.md`
- `task_v2_sales_workspace_draft_review_persistence_v0.md`

## Current State

- V2 MVP persistence baseline 仍为 Postgres / Alembic。
- SQLite 仍只是 legacy / test path，不是 V2 runtime fallback。
- memory / JSON store path 保留为 prototype / demo continuity。
- 显式 `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND=postgres` 时，workspace API 和 Draft Review routes 使用 Postgres-backed stores。
- Android API response shape 未改变。

## Validation Summary

本链路阶段性验证覆盖：

- Postgres / SQLite Alembic upgrade。
- Sales Workspace schema inspection。
- repository create / get / save / apply。
- API default memory/json path。
- API postgres mode create / patch / ranking / projection / ContextPack。
- Draft Review postgres mode create / get / accept / reject / apply / stale apply。
- Draft Review lifecycle append-only events。

## Known Limitations

- 尚未实现 Draft Review history read API。
- 尚未实现 Android review history view。
- 尚未做正式 Runtime / LangGraph integration。
- 未接真实 LLM、search、CRM、contact。
- 未实现多用户权限边界。

## Recommended Next Step

建议先做 post-persistence chain review，再选择一个方向：

- Runtime / LangGraph design。
- Android review history view。
- DB hardening / repository reconstruction from relational rows。
