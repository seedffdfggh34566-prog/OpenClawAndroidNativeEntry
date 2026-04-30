---
name: backend-api-change-check
description: Use when backend API, schema, request, response, formal object, memory API, or error behavior changes and you need to guard V3 contract drift and backend governance boundaries.
---

# Backend API Change Check

Use this skill when a backend change may alter public API behavior, schema shape, runtime-memory API, formal object semantics, or error behavior.

Read these repo files first:

1. `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/README.md`
4. `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
5. `docs/architecture/v3/memory-native-sales-agent.md`
6. relevant API/reference docs
7. the current backend task and handoff

Use V1/V2 API docs only as compatibility or historical references.

## Trigger conditions

Run this skill when changes touch:

- `backend/api/main.py`
- `backend/api/schemas.py`
- `backend/api/services.py`
- request bodies, response envelopes, status fields, or error payloads
- memory APIs, formal object writeback, or runtime-to-backend contracts
- docs under `docs/reference/api/` or `docs/reference/schemas/`

## Review workflow

1. Identify every request and response model touched by the change.
2. Decide whether the change affects fields, status semantics, error semantics, memory semantics, or object aggregation.
3. Mark whether it is additive, compatible, or breaking.
4. Check whether runtime memory concepts are being forced into formal-object contracts too early.
5. Check whether formal business writeback bypasses backend governance.
6. Choose the smallest meaningful test or smoke path.

## Minimum evidence

Report:

- whether formal API contract is affected
- affected request and response models
- additive / compatible / breaking classification
- whether memory API and formal object writeback are separated
- which docs and tests must be synchronized
- validation run or still required

## Stop conditions

Stop and escalate if:

- the change redefines formal object meaning without direction docs
- V3 memory update is forced into old `patch_operations` or V2-only contracts
- inferred/hypothesis memory is treated as confirmed business truth
- a new API capability is introduced before task/contract approval
