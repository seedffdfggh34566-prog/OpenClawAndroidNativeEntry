# Handoff: V2 Postgres Dev Environment Baseline

日期：2026-04-27

## Summary

本次完成 V2 Postgres dev environment baseline。仓库现在提供本地 Postgres Docker Compose 入口、Postgres driver dependency、runbook 和 opt-in Postgres verification test，可用于后续 Sales Workspace persistence schema / migration 工作。

本次没有写 Sales Workspace schema migration，也没有改变 backend API、Android 或 Runtime 行为。

## Changed

- 新增 `compose.postgres.yml`。
- 更新 `backend/pyproject.toml`，增加 `psycopg[binary]>=3.2,<4.0`。
- 新增 `backend/tests/test_postgres_dev_environment.py`。
- 新增 `docs/how-to/operate/postgres-dev-environment.md`。
- 更新 `backend/README.md`、`docs/how-to/README.md`、`docs/README.md`、`docs/delivery/README.md`。
- 更新 `docs/delivery/tasks/task_v2_postgres_dev_environment_baseline.md` 为 done。
- 新增 `docs/delivery/tasks/task_v2_sales_workspace_persistence_schema_design.md` 并设为当前唯一开放任务。
- 更新 `docs/delivery/tasks/_active.md`。

## DB Risk Classification

- Risk category：DB tooling / local environment baseline。
- Schema / migration files changed：no。
- SQLAlchemy model changed：no。
- Alembic versions changed：no。
- Postgres involved：yes，local dev environment and verification only。
- Dedicated follow-up required：yes，`task_v2_sales_workspace_persistence_schema_design.md`。

## Validation

- `docker compose -f compose.postgres.yml up -d`
- `docker compose -f compose.postgres.yml ps`
- `docker exec openclaw-postgres pg_isready -U openclaw -d openclaw_dev`
- `backend/.venv/bin/pip install -e backend`
- `OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/alembic -c alembic.ini upgrade head`
- `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_postgres_dev_environment.py -q`
- `backend/.venv/bin/python -m pytest backend/tests/test_persistence.py -q`
- backend startup + `/health` smoke against local Postgres
- `docker compose -f compose.postgres.yml down`
- `git diff --check`
- `git status --short`

## Known Limitations

- No Sales Workspace table exists yet.
- No SQLAlchemy model or Alembic migration was added.
- No persistence-backed Sales Workspace API is opened.
- `backend/tests/test_persistence.py` remains a SQLite fixture test; Postgres verification uses the opt-in `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` test.

## Recommended Next Step

执行 `task_v2_sales_workspace_persistence_schema_design.md`。先设计 schema，不直接写 migration。
