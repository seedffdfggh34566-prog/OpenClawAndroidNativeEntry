---
name: backend-task-bootstrap
description: Use when a backend thread needs a task file, validation plan, or handoff structure before implementation so the work stays scoped to repo docs, backend rules, and a clear done definition.
---

# Backend Task Bootstrap

Use this skill before implementation whenever backend work does not already have a well-scoped task, or when the current thread needs a follow-up task instead of silently expanding an existing one.

Read these repo files first:

1. `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/README.md`
4. `docs/delivery/tasks/_active.md`
5. the closest related backend task and handoff

## When to use it

Trigger this skill when any of these are true:

- the backend change is non-trivial and no task file exists yet
- the requested work is a follow-up, not a clean extension of the current task
- the work touches API contract, runtime boundary, persistence, migration, observability, or environment assumptions
- the implementation needs a clear validation ladder and handoff before coding starts

Do not use this skill for tiny typo fixes or docs-only edits that already fit an existing task without changing scope.

## What to produce

Create or update a backend task so it includes:

- objective
- in scope
- out of scope
- likely files
- validation criteria
- current status
- explicit risks or follow-up triggers

Also prepare a matching handoff outline with:

- what changed
- what was validated
- known limits
- next recommended step

## Workflow

1. Confirm whether the current backend request belongs to an existing task or needs a new follow-up task.
2. If the current task would be stretched by new scope, split a new backend follow-up task instead of appending hidden requirements.
3. Draft the smallest task that is decision-complete for the intended change.
4. Choose the minimum validation level using `backend/AGENTS.md`.
5. Record the expected handoff points before implementation starts.

## Validation template

Pick the lightest meaningful validation:

- docs-only: `git diff --check`
- low-risk backend logic: `backend/.venv/bin/python -m pytest backend/tests`
- API or persistence wiring: tests + `backend/.venv/bin/alembic upgrade head` + backend startup + `/health`
- runtime boundary work: tests + backend startup + one manual API flow check
- storage, observability, MCP, or environment changes: dedicated task and explicit risk notes

## Output checklist

Your bootstrap result should explicitly answer:

- why this work belongs in the chosen task
- what is deliberately out of scope
- which backend skill should be used next
- what validation must run before the task can be called done
- what the handoff must mention

## Stop conditions

Stop and escalate if the task would:

- redefine product direction or object semantics
- silently broaden V1 scope
- change database baseline, observability vendor, runtime framework, or MCP boundary without a dedicated task
- bundle multiple high-risk backend changes into one thread
