# Task: V2 Postgres Dev Environment Baseline

状态：done

更新时间：2026-04-27

## Objective

为 V2 Sales Workspace 后续 Postgres / Alembic persistence implementation 准备本地开发环境入口和验证命令。

本任务只补 Postgres dev environment，不写 Sales Workspace schema migration。

## Scope

- 优先新增 Docker Compose 本地 Postgres 启动方式。
- 如 backend 当前缺少 Postgres driver，新增最小依赖。
- 补 runbook，记录：
  - 启动 / 停止 Postgres。
  - `OPENCLAW_BACKEND_DATABASE_URL` 示例。
  - `alembic upgrade head` 验证。
  - backend tests / `/health` smoke。
- 验证当前 baseline V1 schema 可在 Postgres 上 upgrade。
- 保持现有 SQLite test path 可用。

## Out Of Scope

- 不新增 Sales Workspace table。
- 不写 V2 schema migration。
- 不修改 Sales Workspace API。
- 不改 Android。
- 不接 LangGraph / LLM / search / CRM / contact。
- 不实现 production deployment。

## Validation Criteria

- Postgres startup command succeeds。
- `alembic upgrade head` passes against local Postgres。
- opt-in Postgres dev environment pytest passes against local Postgres。
- backend startup + `/health` smoke passes against local Postgres。
- Existing SQLite backend tests remain pass if dependency metadata changes。
- `git diff --check` passes。

## Result

已完成：

- 新增 `compose.postgres.yml`，提供本地 `postgres:16` dev service。
- 新增 Postgres driver dependency：`psycopg[binary]>=3.2,<4.0`。
- 新增 Postgres dev environment runbook：`docs/how-to/operate/postgres-dev-environment.md`。
- 新增 opt-in Postgres verification test：`backend/tests/test_postgres_dev_environment.py`。
- 保留现有 SQLite test path。
- 未新增 Sales Workspace table、SQLAlchemy model、Alembic migration、backend route、Android UI 或 Runtime / LangGraph integration。

## Actual Validation

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

说明：`backend/tests/test_persistence.py` 通过 repo fixture 固定验证临时 SQLite path；Postgres path 由新增 opt-in 测试验证，避免普通测试套件依赖 Docker。
