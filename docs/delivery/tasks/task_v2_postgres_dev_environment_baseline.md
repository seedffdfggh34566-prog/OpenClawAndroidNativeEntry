# Task: V2 Postgres Dev Environment Baseline

状态：planned / current

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
- `backend/tests/test_persistence.py` passes against local Postgres。
- backend startup + `/health` smoke passes against local Postgres。
- Existing SQLite backend tests remain pass if dependency metadata changes。
- `git diff --check` passes。
