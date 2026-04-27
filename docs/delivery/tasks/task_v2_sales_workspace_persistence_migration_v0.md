# Task: V2 Sales Workspace Persistence Migration v0

状态：planned / blocked

更新时间：2026-04-27

## Objective

根据 `docs/architecture/workspace/sales-workspace-persistence-schema.md` 实现首版 Sales Workspace Postgres / Alembic migration。

## Blocker

必须等待 persistence schema design PR 合并并经人工确认后才能开放。

## Scope Placeholder

- 新增 Alembic revision。
- 创建 Sales Workspace persistence schema 首批表、约束和索引。
- 不改变 API 行为。
- 不切换当前 prototype store。

## Out Of Scope Until Unblocked

- 不写 repository layer。
- 不改 FastAPI route。
- 不改 Android。
- 不接 Runtime / LangGraph。
- 不接 LLM / search / CRM / contact。
