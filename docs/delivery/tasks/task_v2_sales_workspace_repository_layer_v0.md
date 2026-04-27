# Task: V2 Sales Workspace Repository Layer v0

状态：planned / blocked

更新时间：2026-04-27

## Objective

在 Sales Workspace persistence migration v0 完成后，实现 Pydantic object 与 Postgres schema 之间的 repository layer。

## Blocker

必须等待 persistence schema design 与 migration v0 完成。

## Scope Placeholder

- 读写 `SalesWorkspace` 及其正式子对象。
- 维护 `workspace_version` optimistic concurrency。
- 写入 append-only patch commit record。
- 保持现有 API contract 语义。

## Out Of Scope Until Unblocked

- 不新增 API route。
- 不改 Android。
- 不接 Runtime / LangGraph。
- 不接 LLM / search / CRM / contact。
