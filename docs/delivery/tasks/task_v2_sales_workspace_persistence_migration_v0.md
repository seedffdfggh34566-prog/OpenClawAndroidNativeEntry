# Task: V2 Sales Workspace Persistence Migration v0

状态：done

更新时间：2026-04-27

## Objective

根据 `docs/architecture/workspace/sales-workspace-persistence-schema.md` 实现首版 Sales Workspace Postgres / Alembic migration。

## Blocker

已由长线程执行计划开放。

## Scope Placeholder

- 新增 Alembic revision。
- 创建 Sales Workspace persistence schema 首批表、约束和索引。
- 不改变 API 行为。
- 不切换当前 prototype store。

## Result

已完成：

- 新增 Alembic revision：`backend/alembic/versions/20260427_0002_sales_workspace_persistence.py`。
- 创建首批 9 张 Sales Workspace persistence tables。
- Postgres 使用 JSONB payload snapshots。
- SQLite Alembic test path 继续使用 JSON 并可 upgrade。
- 新增 schema inspection test：`backend/tests/test_sales_workspace_persistence_schema.py`。
- 未写 repository layer、未改 FastAPI route、未改 Android、未接 Runtime / LangGraph。

## Actual Validation

- `docker compose -f compose.postgres.yml up -d`
- `docker exec openclaw-postgres pg_isready -U openclaw -d openclaw_dev`
- `OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/alembic -c alembic.ini upgrade head`
- `backend/.venv/bin/alembic -c alembic.ini upgrade head`
- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_persistence_schema.py backend/tests/test_persistence.py -q`
- `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_postgres_dev_environment.py -q`
- `git diff --check`

## Out Of Scope Until Unblocked

- 不写 repository layer。
- 不改 FastAPI route。
- 不改 Android。
- 不接 Runtime / LangGraph。
- 不接 LLM / search / CRM / contact。
