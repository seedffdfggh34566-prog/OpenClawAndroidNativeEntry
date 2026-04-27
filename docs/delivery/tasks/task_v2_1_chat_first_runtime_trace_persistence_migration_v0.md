# Task: V2.1 Chat-first Runtime Trace Persistence Migration v0

状态：done

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

## Outcome

- 新增 Alembic revision `20260427_0003_chat_first_trace_persistence.py`。
- 创建 V2.1 chat-first trace tables：
  - `sales_workspace_conversation_messages`
  - `sales_workspace_agent_runs`
  - `sales_workspace_context_packs`
- JSON payload 使用 Postgres JSONB variant 与 SQLite JSON fallback。
- 更新 schema inspection test，确认 trace tables 和核心字段存在。
- 本任务未新增 API behavior、runtime、Android、LangGraph、真实 LLM、search、ContactPoint 或 CRM。

## Validation

```bash
docker compose -f compose.postgres.yml up -d
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/alembic -c alembic.ini upgrade head
backend/.venv/bin/alembic -c alembic.ini upgrade head
backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_persistence_schema.py backend/tests/test_persistence.py -q
git diff --check
```
