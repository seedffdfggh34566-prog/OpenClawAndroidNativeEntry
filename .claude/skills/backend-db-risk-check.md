---
name: backend-db-risk-check
description: Use when backend models, migrations, storage assumptions, or database tooling change and you need to classify schema risk, migration risk, and follow-up task requirements.
---

# Backend DB Risk Check

Use this skill when backend work touches persistence shape, migration history, storage baseline, or database tooling boundaries.

Read these repo files first:

1. `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/architecture/backend/backend-agent-stack-phased-adoption.md`
4. the current backend task and handoff

## Trigger conditions

Run this skill when changes touch:

- `backend/api/database.py`
- `backend/api/models.py`
- `backend/alembic/`
- `backend/pyproject.toml` database dependencies
- storage-baseline work such as `SQLite -> Postgres`
- future `pgvector` or MCP database tooling discussions

## Review workflow

1. Classify the change:
   - schema shape
   - migration risk
   - storage baseline change
   - DB tooling or permission boundary
2. Decide whether a new formal object, status field, or version field is required.
3. Check whether migration naming and revision handling are clear.
4. Confirm SQLite-specific assumptions are not being hard-coded into a future Postgres path.
5. Choose the minimum validation:
   - tests
   - `alembic upgrade head`
   - `alembic check`

## Current guardrails

- Do not treat tracked DB files as source code.
- Do not hand-wave destructive changes as harmless local setup.
- Do not introduce arbitrary SQL execution for agents or tools.
- Do not pre-optimize for Postgres-specific or vector-specific patterns before the dedicated task exists.

## Minimum evidence

Report:

- which DB risk category applies
- whether schema or migration files changed
- whether SQLite, Postgres, pgvector, or DB tooling boundaries are involved
- whether a dedicated follow-up task is required
- what validation actually ran

## Stop conditions

Stop and escalate if:

- the change implies destructive schema evolution
- the storage baseline changes to Postgres
- pgvector enters scope without a retrieval task
- MCP database tools would expose unrestricted SQL
