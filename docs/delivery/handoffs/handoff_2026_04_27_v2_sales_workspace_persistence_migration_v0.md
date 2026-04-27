# Handoff: V2 Sales Workspace Persistence Migration v0

日期：2026-04-27

## Summary

本次完成 Sales Workspace 首版 Postgres / Alembic migration。新增 9 张 persistence schema tables，Postgres payload 使用 JSONB，SQLite test path 继续可运行。

## Changed

- 新增 Alembic revision：`backend/alembic/versions/20260427_0002_sales_workspace_persistence.py`
- 新增 schema inspection test：`backend/tests/test_sales_workspace_persistence_schema.py`
- 更新 Postgres dev environment test，确认 Sales Workspace tables 存在。
- 更新 task：`task_v2_sales_workspace_persistence_migration_v0.md`
- 更新 `_active.md` 和 `docs/delivery/README.md`，下一项为 repository layer v0。

## DB Risk Classification

- Risk category：schema migration。
- Schema / migration files changed：yes。
- SQLAlchemy ORM changed：no。
- API route changed：no。
- Postgres involved：yes，official V2 target。
- SQLite involved：yes，legacy / test path verified with `sa.JSON` fallback.
- pgvector involved：no。

## Validation

- `docker compose -f compose.postgres.yml up -d`
- `docker exec openclaw-postgres pg_isready -U openclaw -d openclaw_dev`
- `OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/alembic -c alembic.ini upgrade head`
- `backend/.venv/bin/alembic -c alembic.ini upgrade head`
- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_persistence_schema.py backend/tests/test_persistence.py -q`
- `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_postgres_dev_environment.py -q`
- `git diff --check`

## Known Limitations

- No repository layer was implemented in this task.
- No FastAPI route uses these tables yet.
- Draft Review persistence tables exist but are not wired to routes yet.

## Recommended Next Step

Continue to `task_v2_sales_workspace_repository_layer_v0.md`.
