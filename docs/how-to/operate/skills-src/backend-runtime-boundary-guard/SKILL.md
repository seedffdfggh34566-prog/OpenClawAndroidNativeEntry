---
name: backend-runtime-boundary-guard
description: Use when backend runtime flow, AgentRun behavior, or future LangGraph or MCP work may cross the boundary between execution logic and the formal product backend.
---

# Backend Runtime Boundary Guard

Use this skill to protect the line between the product backend and the runtime execution layer.

Read these repo files first:

1. `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/architecture/system-context.md`
4. `docs/architecture/backend/backend-agent-stack-phased-adoption.md`
5. the current backend task and handoff

## Trigger conditions

Run this skill when changes touch:

- `backend/runtime/`
- `backend/api/services.py` run-processing logic
- `AgentRun` writeback paths
- `input_refs`, `output_refs`, or `runtime_metadata`
- future `LangGraph`, `MCP`, observability, or tool-server adoption work

## Current lifecycle boundary

At the current repo stage, only a lightweight lifecycle is assumed. The implemented run flow is still centered on:

- `queued`
- `running`
- `succeeded`
- `failed`

Do not assume `waiting_for_user`, durable checkpoints, interrupt/resume, or queue-worker orchestration already exist.

## Review workflow

1. Confirm whether runtime is still only the execution layer.
2. Confirm whether formal object writeback still happens through product-backend services.
3. Check how inputs, outputs, and failures are recorded.
4. Decide whether retries or human review are being implicitly introduced.
5. Decide whether the work still belongs to the current task or needs a dedicated runtime-adoption follow-up.

## Minimum evidence

Report:

- whether the backend/runtime boundary changed
- which run states or references were touched
- how errors are recorded
- whether writeback ownership stayed in product backend code
- whether the change should be split into a dedicated runtime task

## Stop conditions

Stop and escalate if:

- runtime directly becomes the product truth layer
- the code assumes full LangGraph durable execution before that task exists
- MCP is being used as the internal service architecture
- HITL, resume, or manual review states are being added without an explicit lifecycle task
