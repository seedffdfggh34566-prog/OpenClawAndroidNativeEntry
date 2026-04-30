---
name: backend-task-bootstrap
description: Use when a backend thread needs task scope, validation, or handoff structure before implementation, especially for V3 runtime, memory, sandbox working state, customer intelligence, API, or persistence work.
---

# Backend Task Bootstrap

Use this skill before backend implementation whenever work lacks a clear task, validation level, or handoff boundary.

Read these repo files first:

1. `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/README.md`
4. `docs/delivery/tasks/_active.md`
5. the closest related backend task and handoff

## When to use it

Trigger this skill when:

- backend work is non-trivial and no task clearly fits it
- the user request is a follow-up rather than a clean extension of the current task
- work touches API contract, runtime boundary, memory, sandbox working state, customer intelligence, persistence, migration, observability, or environment assumptions
- implementation needs a clear validation ladder and handoff before coding

Do not use this skill for tiny typo fixes or docs-only edits that already fit an existing task.

## Workflow

1. Confirm the authorization source: user request, `_active.md`, or an existing task.
2. Decide whether a new follow-up task is required.
3. Define objective, in scope, out of scope, likely files, and validation.
4. Split work if it bundles runtime, memory schema, API, and migration into one broad task.
5. Select follow-up guard skills such as `backend-runtime-boundary-guard`, `backend-api-change-check`, or `backend-db-risk-check`.
6. Record handoff expectations before implementation starts.

## Validation template

- docs-only: `git diff --check`
- backend logic: backend tests
- API / persistence: tests + migration + backend startup + `/health`
- runtime / memory / working-state boundary: tests + backend startup + one relevant API/manual flow
- storage, observability, MCP, or environment changes: dedicated task and explicit risk notes

## Stop conditions

Stop and escalate if the task would:

- redefine product direction or turn sandbox working state into formal object semantics
- start V3 runtime / memory implementation without explicit task authorization
- silently bundle LangGraph, memory schema, API contract, and persistence migration
- switch database, observability, MCP, or deployment assumptions without a dedicated task
- require secrets or irreversible Git operations
