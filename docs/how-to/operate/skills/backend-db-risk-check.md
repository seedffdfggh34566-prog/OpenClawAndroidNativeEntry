# Skill Spec: `backend-db-risk-check`

更新时间：2026-04-29

## Purpose

对 backend persistence、memory storage、formal object storage、migration 和 DB tooling 做 V3 风险分级，避免 memory-native 方向落成不可治理的数据模型。

## When to trigger

- `backend/api/database.py`
- `backend/api/models.py`
- `backend/alembic/`
- backend DB dependency 变化
- memory blocks、archival memory、embedding / retrieval storage
- formal business object storage
- SQLite / Postgres / pgvector / MCP database tooling / DB permissions

## Required repo docs

- 根 `AGENTS.md`
- `backend/AGENTS.md`
- `docs/README.md`
- `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
- `docs/architecture/v3/memory-native-sales-agent.md`
- 当前 task / handoff

V1/V2 persistence docs 只作 historical / compatibility reference。

## Expected outputs / evidence

- DB risk category
- schema / migration 是否改变
- cognitive memory storage 与 formal object storage 是否分离
- SQLite / Postgres / pgvector / DB tooling 是否涉及
- LangGraph checkpoint 是否被误当成业务 memory 主存
- 是否需要 dedicated follow-up task
- 已执行或仍需执行的验证

## Stop / escalate conditions

- 未开放 task 就启动 memory schema / migration
- cognitive memory 和 formal objects 被合并成无治理表或 payload
- LangGraph checkpoint 成为唯一长期 memory store
- destructive schema evolution
- 未开放 retrieval / embedding task 就引入 pgvector
- DB tools 给 runtime 或 Product Sales Agent unrestricted SQL

## Non-goals

- 不替代数据库迁移 task。
- 不执行数据库迁移。
- 不批准 Postgres、pgvector 或 DB tool server 接入。
