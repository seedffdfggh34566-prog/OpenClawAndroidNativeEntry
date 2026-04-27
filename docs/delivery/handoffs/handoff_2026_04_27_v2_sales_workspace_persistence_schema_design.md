# Handoff: V2 Sales Workspace Persistence Schema Design

日期：2026-04-27

## Summary

本次完成 Sales Workspace persistence schema design。schema 采用 relational core + JSONB payload snapshots，面向 Postgres / Alembic MVP baseline，但未实现 SQLAlchemy ORM 或 Alembic migration。

## Changed

- 新增 `docs/architecture/workspace/sales-workspace-persistence-schema.md`。
- 更新 `docs/architecture/README.md`、`docs/README.md`、`docs/delivery/README.md`、`docs/delivery/tasks/_active.md`。
- 将 `task_v2_sales_workspace_persistence_schema_design.md` 标记为 done。
- 新增 planned / blocked follow-up tasks：
  - `task_v2_sales_workspace_persistence_migration_v0.md`
  - `task_v2_sales_workspace_repository_layer_v0.md`
  - `task_v2_sales_workspace_api_postgres_store_v0.md`
  - `task_v2_sales_workspace_draft_review_persistence_v0.md`

## Decisions

- `sales_workspaces` 是 root table。
- `workspace_version` 是 optimistic concurrency basis。
- `sales_workspace_patch_commits` 是 append-only formal write audit。
- `sales_workspace_draft_reviews` 保存当前 review object 状态。
- `sales_workspace_draft_review_events` 保存 append-only lifecycle audit history。
- RankingBoard、Markdown projection、ContextPack 是 derived outputs，不是 v0 formal truth tables。
- `tenant_id`、`created_by`、`updated_by` 只作为 nullable metadata 预留，不实现权限模型。

## DB Risk Classification

- Risk category：schema shape design only。
- Schema / migration files changed：no。
- SQLAlchemy model changed：no。
- Alembic versions changed：no。
- Postgres involved：yes，design target only。
- pgvector involved：no。
- Dedicated follow-up required：yes，migration / repository / API store tasks remain blocked。

## Validation

- `rg "sales-workspace-persistence-schema.md|sales_workspaces|sales_workspace_patch_commits|sales_workspace_draft_reviews" docs`
- `rg "relational core|JSONB|workspace_version|optimistic concurrency|append-only|derived outputs" docs/architecture/workspace/sales-workspace-persistence-schema.md`
- `rg "不写 SQLAlchemy|不写 Alembic|不改 Android|不接 LangGraph" docs/delivery/tasks docs/delivery/handoffs`
- `git diff --check`
- `git status --short`

## Known Limitations

- No SQLAlchemy ORM was added.
- No Alembic migration was added.
- No backend API route changed.
- No Android code changed.
- No Runtime / LangGraph / LLM / search integration was opened.

## Recommended Next Step

人工 review schema design。合并后再决定是否开放 `task_v2_sales_workspace_persistence_migration_v0.md`。
