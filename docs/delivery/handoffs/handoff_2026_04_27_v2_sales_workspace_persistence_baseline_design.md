# Handoff: V2 Sales Workspace Persistence Baseline Design

日期：2026-04-27

## Summary

本次完成 Sales Workspace persistence baseline design。结论是 V2 MVP 使用 Postgres / Alembic 作为正式 persistence baseline；JSON file store 继续作为 prototype / demo continuity；SQLite 不作为 V2 runtime fallback。

## Changed

- 新增架构文档：`docs/architecture/workspace/sales-workspace-persistence-baseline.md`
- 更新 ADR-007 addendum。
- 更新 task：`task_v2_sales_workspace_persistence_baseline_design.md`
- 新增下一项任务：`task_v2_postgres_dev_environment_baseline.md`
- 更新 `docs/README.md`、`docs/architecture/README.md`、`docs/delivery/README.md`、`docs/delivery/tasks/_active.md`。

## Decisions

- V2 MVP persistence baseline：Postgres / Alembic。
- SQLite：不作为 V2 runtime fallback。
- JSON file store：prototype / demo continuity only。
- Draft Review：需要长期 audit history。
- Multi-workspace：baseline 必须支持。
- Multi-user / permission：暂不实现，只允许后续 schema design 预留 metadata。

## DB Risk Classification

- Risk category：storage baseline design only。
- Schema / migration files changed：no。
- SQLAlchemy / Alembic / SQLite / Postgres implementation changed：no。
- Dedicated follow-up required：yes，`task_v2_postgres_dev_environment_baseline.md`。

## Validation

- `rg "Postgres / Alembic|SQLite|JSON file store|Draft Review|audit history|multi-workspace" docs/architecture docs/adr docs/delivery docs/README.md`
- `rg "不写 Alembic|不实现 SQLAlchemy|不改 Android|不接 LangGraph|不接真实 LLM" docs/delivery/tasks/_active.md docs/delivery/tasks/task_v2_sales_workspace_persistence_baseline_design.md docs/delivery/handoffs`
- `rg "task_v2_sales_workspace_persistence_baseline_design.md|sales-workspace-persistence-baseline.md" docs/README.md docs/architecture/README.md docs/delivery/README.md docs/delivery/tasks/_active.md`
- `git diff --check`
- `git status --short`

## Known Limitations

- 本次没有实现 Postgres dev environment。
- 本次没有写 SQLAlchemy model 或 Alembic migration。
- 本次没有切换 backend runtime persistence。

## Recommended Next Step

执行 `task_v2_postgres_dev_environment_baseline.md`，只补本地 Postgres dev environment 和验证命令，不写 Sales Workspace schema migration。
