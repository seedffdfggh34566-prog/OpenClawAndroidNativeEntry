# Postgres Dev Environment Runbook

更新时间：2026-04-27

## Purpose

本 runbook 用于在 `jianglab` 上启动本地 Postgres，验证当前 backend Alembic baseline 可以跑在 Postgres 上，并为后续 Sales Workspace persistence schema design 做准备。

本 runbook 不代表已经实现 Sales Workspace 正式 DB schema。本阶段仍不写 Sales Workspace table、不改 API、不改 Android、不接 LangGraph / LLM / search。

## Start Postgres

```bash
docker compose -f compose.postgres.yml up -d
docker compose -f compose.postgres.yml ps
docker exec openclaw-postgres pg_isready -U openclaw -d openclaw_dev
```

默认本地连接信息：

```bash
export OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev
```

## Install Backend Dependency

```bash
backend/.venv/bin/pip install -e backend
```

## Run Alembic Baseline

```bash
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev \
  backend/.venv/bin/alembic -c alembic.ini upgrade head
```

## Verify Postgres Path

`backend/tests/test_persistence.py` 仍通过 repo fixture 验证 SQLite 临时数据库路径。Postgres dev environment 使用 opt-in 测试，避免普通测试套件依赖 Docker。

```bash
OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev \
  backend/.venv/bin/python -m pytest backend/tests/test_postgres_dev_environment.py -q
```

SQLite regression：

```bash
backend/.venv/bin/python -m pytest backend/tests/test_persistence.py -q
```

## Backend Health Smoke

```bash
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev \
  backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
```

另一个终端执行：

```bash
curl http://127.0.0.1:8013/health
```

## Stop Postgres

```bash
docker compose -f compose.postgres.yml down
```

该命令保留命名 volume `openclaw_postgres_data`，方便后续本地继续验证。需要重置本地数据库时再显式清理 volume。

## Boundaries

- JSON file store 仍只用于 prototype / demo continuity。
- Postgres / Alembic 是 V2 MVP persistence baseline 的推荐方向。
- 本 runbook 不创建 Sales Workspace table。
- 本 runbook 不开放 SQLAlchemy model、Alembic migration、backend API、Android write path 或 Runtime / LangGraph implementation。
