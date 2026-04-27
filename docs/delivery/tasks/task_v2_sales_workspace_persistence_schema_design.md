# Task: V2 Sales Workspace Persistence Schema Design

状态：done

更新时间：2026-04-27

## Objective

在 Postgres / Alembic persistence baseline 与本地 Postgres dev environment 都完成后，设计 Sales Workspace 正式 persistence schema。

本任务只做 schema design，不写 SQLAlchemy model、不写 Alembic migration、不改 backend route。

## Scope

- 定义 Sales Workspace persistence schema 的正式对象边界：
  - workspace。
  - product profile revision。
  - lead direction。
  - lead candidate。
  - research source。
  - research observation。
  - workspace patch / commit record。
  - draft review audit history 的承载边界。
- 定义 workspace version、optimistic concurrency、archive / status 字段。
- 定义 multi-workspace baseline 与 future multi-user metadata 预留。
- 明确 derived outputs 的处理方式：
  - ranking board。
  - Markdown projection。
  - ContextPack。
- 输出后续 implementation task 的前置条件。

## Out Of Scope

- 不写 SQLAlchemy ORM。
- 不写 Alembic migration。
- 不修改 `backend/api/models.py`。
- 不修改 `backend/alembic/`。
- 不新增或修改 FastAPI route。
- 不改 Android。
- 不接 LangGraph / LLM / search / CRM / contact。
- 不做生产部署。

## Deliverables

- schema design 文档或现有 persistence baseline 文档扩展。
- 明确 Draft Review persistence schema 是否拆成独立后续任务。
- 明确第一批 Alembic migration 的对象清单。
- 更新 task / handoff / `_active.md`。

## Result

已完成：

- 新增 schema design 文档：`docs/architecture/workspace/sales-workspace-persistence-schema.md`。
- 冻结 schema 方案为 relational core + JSONB payload snapshots。
- 明确 persisted table 边界：
  - `sales_workspaces`
  - `sales_workspace_product_profile_revisions`
  - `sales_workspace_lead_directions`
  - `sales_workspace_lead_candidates`
  - `sales_workspace_research_sources`
  - `sales_workspace_research_observations`
  - `sales_workspace_patch_commits`
  - `sales_workspace_draft_reviews`
  - `sales_workspace_draft_review_events`
- 明确 ranking board、Markdown projection、ContextPack 是 derived outputs，不作为 v0 formal truth。
- 明确 Draft Review audit history 纳入首版 schema design。
- 新增后续 planned / blocked tasks：
  - `task_v2_sales_workspace_persistence_migration_v0.md`
  - `task_v2_sales_workspace_repository_layer_v0.md`
  - `task_v2_sales_workspace_api_postgres_store_v0.md`
  - `task_v2_sales_workspace_draft_review_persistence_v0.md`
- 未写 SQLAlchemy ORM、Alembic migration、backend route、Android UI 或 Runtime / LangGraph integration。

## Validation Criteria

- 文档明确 schema 对象、字段边界和关系。
- 文档明确哪些对象是 persisted，哪些是 derived / recomputed。
- `_active.md` 不自动开放 migration implementation。
- `git diff --check` 通过。

## Actual Validation

- `rg "sales-workspace-persistence-schema.md|sales_workspaces|sales_workspace_patch_commits|sales_workspace_draft_reviews" docs`
- `rg "relational core|JSONB|workspace_version|optimistic concurrency|append-only|derived outputs" docs/architecture/workspace/sales-workspace-persistence-schema.md`
- `rg "不写 SQLAlchemy|不写 Alembic|不改 Android|不接 LangGraph" docs/delivery/tasks docs/delivery/handoffs`
- `git diff --check`
- `git status --short`

不运行 backend / Android build；本轮是 docs-only schema design。
