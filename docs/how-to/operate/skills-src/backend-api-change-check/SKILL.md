---
name: backend-api-change-check
description: Use when backend API, schema, request, response, or error behavior changes and you need to guard formal contract drift, breaking changes, and required test or docs updates.
---

# Backend API Change Check

Use this skill when a backend change may alter API contract, schema shape, status semantics, or error behavior.

Read these repo files first:

1. `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/reference/api/backend-v1-minimum-contract.md`
4. `docs/reference/schemas/v1-domain-model-baseline.md`
5. the current backend task and handoff

## Trigger conditions

Run this skill when changes touch:

- `backend/api/main.py`
- `backend/api/schemas.py`
- `backend/api/services.py`
- response envelopes, request bodies, status fields, or error payloads
- docs under `docs/reference/api/` or `docs/reference/schemas/`

## Review workflow

1. Identify every request and response model touched by the change.
2. Decide whether the change affects fields, status semantics, error semantics, or object aggregation.
3. Mark whether it is backward compatible, additive, or breaking.
4. Check which layers must stay aligned:
   - router
   - service
   - schema
   - tests
   - docs
5. Choose the smallest meaningful smoke test and local verification.

## Breaking-change guidance

Treat the change as breaking if it:

- removes or renames existing fields
- changes field meaning or type
- changes error shape or status semantics in a way current clients cannot ignore
- changes object aggregation or read/write expectations without a documented follow-up

## Minimum evidence

Report:

- whether formal contract is affected
- the affected request and response models
- whether the change is additive or breaking
- which docs must be synchronized
- the minimum smoke test that ran or still needs to run

## Stop conditions

Stop and escalate if:

- the change redefines formal object meaning
- the change extends V1 scope
- the change conflicts with product docs or ADRs
- the code would introduce a new API capability before contract approval
