# Task: V2 Sales Workspace API Postgres Store v0

状态：planned / blocked

更新时间：2026-04-27

## Objective

将 Sales Workspace API prototype 从 in-memory / JSON prototype store 切到 Postgres-backed repository。

## Blocker

必须等待 persistence migration v0 与 repository layer v0 完成。

## Scope Placeholder

- 保持已冻结 API contract。
- 使用 Postgres repository 作为 formal persistence。
- 保留 prototype store 的本地 demo 兼容策略需另行确认。
- 覆盖 version conflict、not found、validation error、derived output 读取。

## Out Of Scope Until Unblocked

- 不改 Android write flow。
- 不接 Runtime / LangGraph 正式 graph。
- 不接 LLM / search / CRM / contact。
- 不实现 multi-user permission。
