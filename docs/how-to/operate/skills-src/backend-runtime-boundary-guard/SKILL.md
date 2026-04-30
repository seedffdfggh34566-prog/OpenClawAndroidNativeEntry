---
name: backend-runtime-boundary-guard
description: Use when backend runtime, LangGraph, memory tools, AgentRun, sandbox working state, or customer intelligence work may accidentally force V3 into formal object, PatchDraft, or Kernel flows.
---

# Backend Runtime Boundary Guard

Use this skill to protect the V3 sandbox-first boundary: runtime memory and working state should remain open, self-editable, and agent-maintained unless a later task explicitly opens formal governance.

Read these repo files first:

1. `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/README.md`
4. `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
5. `docs/architecture/v3/memory-native-sales-agent.md`
6. the current backend task and handoff

Use V1/V2 runtime docs only as historical reference.

## Trigger conditions

Run this skill when changes touch:

- `backend/runtime/`
- `AgentRun` or run-processing flow
- LangGraph / LangChain runtime adoption
- memory tools, self-editable memory, archival memory, or memory status labels
- sandbox workspace working state or customer intelligence working state
- attempts to reintroduce formal object / PatchDraft / Kernel as the default V3 path
- MCP, observability, or tool-server adoption that affects runtime authority

## V3 boundary

- Runtime memory can contain observed, inferred, hypothesis, confirmed, rejected, or superseded knowledge.
- Runtime memory and working state may be self-editable by the Product Sales Agent.
- V3 first-stage agent writes are sandbox working state, not formal business objects.
- Backend is initially runtime host, storage, trace, and API surface.
- LangGraph checkpoint is not the business memory source of truth.
- Do not reduce V3 runtime to a `WorkspacePatchDraft` generator or Sales Workspace Kernel feeder.

## Workflow

1. Classify whether the change affects runtime memory, sandbox working state, customer intelligence, or external actions.
2. Confirm runtime memory is allowed to store hypotheses and inferred knowledge.
3. Confirm V3 sandbox state is not prematurely modeled as formal objects.
4. Check whether LangGraph persistence is being confused with business memory storage.
5. Decide whether the work needs a dedicated V3 runtime, memory, working-state, or customer-intelligence task.
6. Choose the smallest validation path for the touched backend behavior.

## Minimum evidence

Report:

- whether sandbox-first assumptions changed
- which memory, working-state, customer-intelligence, or external-action concepts were touched
- whether runtime memory remains open and self-editable
- whether a follow-up task is required

## Stop conditions

Stop and escalate if:

- V3 sandbox working state is forced into formal object / PatchDraft / Kernel flow without an explicit task
- agent cognition is blocked merely because memory is inferred or hypothetical
- LangGraph checkpoints are made the only long-term business memory store
- V3 runtime implementation starts without an opened task
- MCP or DB tools expose unrestricted production CRM writes, external outreach, irreversible export, or broad SQL access
