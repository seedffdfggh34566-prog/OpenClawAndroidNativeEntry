---
name: backend-db-risk-check
description: Use when backend models, migrations, memory storage, formal object storage, database tooling, or persistence assumptions change and you need to classify V3 schema and migration risk.
---

# Backend DB Risk Check

Use this skill when backend work touches persistence shape, migration history, memory storage, formal object storage, or database tooling boundaries.

Read these repo files first:

1. `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/README.md`
4. `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
5. `docs/architecture/v3/memory-native-sales-agent.md`
6. the current backend task and handoff

Use V1/V2 persistence docs only as historical or compatibility references.

## Trigger conditions

Run this skill when changes touch:

- `backend/api/database.py`
- `backend/api/models.py`
- `backend/alembic/`
- backend database dependencies
- memory tables, memory blocks, archival memory, embedding/retrieval storage
- formal business object storage
- SQLite, Postgres, pgvector, MCP database tooling, or DB permissions

## Review workflow

1. Classify the change: schema shape, migration risk, memory storage, formal object storage, storage baseline, or DB tooling.
2. Check whether cognitive memory and formal business objects are stored and governed separately.
3. Confirm LangGraph checkpoint is not treated as the only business memory store.
4. Decide whether status/version fields are needed for memory state changes.
5. Confirm SQLite-specific assumptions are not hard-coded into a future Postgres path.
6. Choose the minimum validation: tests, `alembic upgrade head`, or `alembic check`.

## Minimum evidence

Report:

- DB risk category
- whether schema or migration files changed
- whether memory storage or formal object storage changed
- whether SQLite, Postgres, pgvector, or DB tooling boundaries are involved
- whether a dedicated follow-up task is required
- validation run or still required

## Stop conditions

Stop and escalate if:

- memory schema or migration starts without a dedicated task
- cognitive memory and formal objects are collapsed into one unmanaged table or payload
- LangGraph checkpoints become the only long-term memory store
- destructive schema evolution is introduced
- pgvector enters scope without retrieval/embedding authorization
- DB tools expose unrestricted SQL to runtime or Product Sales Agent
