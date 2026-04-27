# Task: V2 Sales Workspace Persistence Schema Design

状态：planned / current

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

## Validation Criteria

- 文档明确 schema 对象、字段边界和关系。
- 文档明确哪些对象是 persisted，哪些是 derived / recomputed。
- `_active.md` 不自动开放 migration implementation。
- `git diff --check` 通过。
