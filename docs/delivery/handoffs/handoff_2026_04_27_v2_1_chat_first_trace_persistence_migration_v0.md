# Handoff: V2.1 Chat-first Trace Persistence Migration v0

日期：2026-04-27

## 1. Changed

- Added Alembic migration for V2.1 chat-first trace persistence.
- Added tables for conversation messages, agent runs, and context packs.
- Extended schema inspection tests for the new trace tables.

## 2. Files

- `backend/alembic/versions/20260427_0003_chat_first_trace_persistence.py`
- `backend/tests/test_sales_workspace_persistence_schema.py`
- `docs/delivery/tasks/task_v2_1_chat_first_runtime_trace_persistence_migration_v0.md`

## 3. Validation

Passed:

```bash
docker compose -f compose.postgres.yml up -d
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/alembic -c alembic.ini upgrade head
OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v21_migration.sqlite backend/.venv/bin/alembic -c alembic.ini upgrade head
backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_persistence_schema.py backend/tests/test_persistence.py -q
git diff --check
```

Note: the first Postgres run exposed an index-name length issue. The migration was fixed by shortening new index names, then Postgres upgrade passed.

## 4. Limits

- Migration and tests only.
- No API behavior, Runtime implementation, Android UI, LangGraph, real LLM, search, ContactPoint, or CRM work.

## 5. Next

Proceed to `task_v2_1_chat_first_runtime_backend_prototype.md`.
