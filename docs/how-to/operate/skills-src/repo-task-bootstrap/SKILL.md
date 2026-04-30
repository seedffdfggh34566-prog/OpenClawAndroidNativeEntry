---
name: repo-task-bootstrap
description: Use when a non-backend-specific repo task needs scope, validation, task, or handoff structure before implementation so the work stays tied to current docs without becoming a product-direction decision.
---

# Repo Task Bootstrap

Use this skill before implementation when repo work is non-trivial, not backend-specific, and lacks a clear current task or validation boundary.

Read these repo files first:

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/delivery/tasks/_active.md`
4. the closest related task and handoff, if any

## When to use it

Trigger this skill when any of these are true:

- the requested work is meaningful and no current task fits it
- the work changes docs workflow, repo operations, skills, or cross-cutting guardrails
- a follow-up task is safer than stretching an already completed task
- validation and handoff expectations need to be explicit before editing

Do not use this skill for tiny typo fixes or for backend-specific work; use `backend-task-bootstrap` for backend tasks.

## Workflow

1. Confirm the authorization source. The current user message can authorize work even when `_active.md` has no queued task.
2. Decide whether the work needs a new task file, an update to `_active.md`, and a handoff.
3. Define the smallest scope that satisfies the request.
4. List explicit out-of-scope items.
5. Choose the lightest meaningful validation.
6. Record wording guardrails: task/handoff docs must not casually claim V3 implementation, version completion, milestone completion, product phase completion, or production readiness.
7. Confirm historical V1/V2 docs are reference only unless the current task explicitly reopens them.

## Expected output

Produce or update a task structure with:

- objective
- in scope / out of scope
- affected areas
- validation plan
- current status
- handoff expectation

## Stop conditions

Stop and ask if the task would:

- redefine product direction without explicit user approval
- start V3 implementation when only docs or planning was requested
- treat historical V1/V2 docs as current truth
- require secrets, deployment changes, migrations, or irreversible Git actions
- decide release, milestone, or product-phase completion on behalf of the user
