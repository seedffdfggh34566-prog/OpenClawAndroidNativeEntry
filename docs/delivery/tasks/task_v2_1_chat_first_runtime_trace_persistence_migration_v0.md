# Task: V2.1 Chat-first Runtime Trace Persistence Migration v0

状态：planned / blocked by trace persistence schema design

更新时间：2026-04-27

## Objective

实现 V2.1 chat-first Runtime trace 的首版 Postgres / Alembic migration，让 ConversationMessage、AgentRun 和 ContextPack trace 能进入正式 persistence baseline。

## Required Precondition

- `task_v2_1_chat_first_runtime_trace_persistence_schema_design.md`

## Scope

- 新增 Alembic revision。
- 创建 schema design 中明确的 trace tables。
- Postgres 使用 JSONB；SQLite test path 使用 SQLAlchemy JSON fallback。
- 补 schema inspection / persistence tests。
- 不接 API behavior。
- 不实现 runtime。

## Out Of Scope

- 不新增 Sales Workspace API endpoint。
- 不改 Android。
- 不接真实 LLM。
- 不实现 LangGraph graph。
- 不接 search / ContactPoint / CRM。
- 不做 production hardening。

## Validation

- Postgres `alembic upgrade head`。
- SQLite `alembic upgrade head`。
- schema inspection tests。
- `git diff --check`。

## Recommended Next

- `task_v2_1_chat_first_runtime_backend_prototype.md`
