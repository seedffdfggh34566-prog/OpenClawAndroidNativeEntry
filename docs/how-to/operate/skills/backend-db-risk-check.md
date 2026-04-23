# Skill Spec: `backend-db-risk-check`

更新时间：2026-04-23

## Skill name

`backend-db-risk-check`

## Purpose

对 backend persistence、迁移、数据库工具层和数据库权限边界相关改动做风险分级与守门；同时吸收原 `schema_and_migration` 方案的正式对象演进与迁移约束。

## When to trigger

适用于以下改动：

- `backend/api/database.py`
- `backend/api/models.py`
- `backend/data/*`
- `backend/pyproject.toml` 中的 DB 依赖变化
- 涉及 `SQLite -> Postgres`
- 涉及 `pgvector`
- 涉及 `MCP Toolbox for Databases`

## Required repo docs

- 根 `AGENTS.md`
- `backend/AGENTS.md`
- `docs/README.md`
- `docs/architecture/backend/backend-agent-stack-phased-adoption.md`
- 当前 task
- 对应 handoff

## Allowed tools / commands

- `git diff -- backend/api/database.py backend/api/models.py backend/pyproject.toml`
- `rg "sqlite|postgres|pgvector|database|engine|session" backend docs`
- `backend/.venv/bin/python -m pytest backend/tests`
- `backend/.venv/bin/alembic upgrade head`
- `backend/.venv/bin/alembic check`

## Expected outputs / evidence

输出应至少包括：

- 这次改动是 schema shape、storage baseline、migration risk 还是 DB tooling risk
- 是否涉及新增或修改正式对象
- 是否需要 version / status 字段
- 是否触及 SQLite / Postgres / pgvector / DB tooling 边界
- 是否需要新 task 或新架构说明
- 当前最小验证做到了哪一步

## Stop / escalate conditions

遇到以下情况应停止并升级：

- 需要正式迁移数据库基线
- 涉及 destructive schema change 或数据迁移
- 计划给 agent / tool 放开 arbitrary SQL
- 计划引入 `pgvector` 但 retrieval 需求尚未进入正式 scope

## Bundled resources plan

本 Skill 后续允许补充：

- DB migration risk checklist
- least-privilege DB tooling checklist
- migration naming checklist
- SQLite 开发期限制说明
- 未来 PostgreSQL cutover 前的 schema anti-pattern 清单

本阶段不要求脚本实现。

## Non-goals

- 不替代正式数据库迁移 task
- 不直接执行数据库迁移
- 不自动批准 `Postgres`、`pgvector` 或 DB tool server 接入
- 不成为生产数据库操作入口
- 不单独再拆一个 `schema_and_migration` skill
