---
name: backend-runtime-boundary-guard
description: Use when backend runtime, LangGraph, memory tools, AgentRun, or formal writeback work may blur V3 open cognitive memory with backend-governed formal business objects.
---

# Backend Runtime Boundary Guard

Use this skill to protect the V3 boundary between open runtime cognition and formal backend commitments.

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
- formal business object writeback from runtime output
- MCP, observability, or tool-server adoption that affects runtime authority

## V3 boundary

- Runtime memory can contain observed, inferred, hypothesis, confirmed, rejected, or superseded knowledge.
- Runtime memory may be self-editable by the Product Sales Agent.
- LangGraph checkpoint is not the business memory source of truth.
- Formal business objects still require backend / Sales Workspace Kernel governance.
- Do not reduce V3 runtime to a `WorkspacePatchDraft` generator.

## Workflow

1. Classify whether the change affects runtime memory, formal writeback, or both.
2. Confirm runtime memory is allowed to store hypotheses and inferred knowledge.
3. Confirm formal objects are not written directly without backend governance.
4. Check whether LangGraph persistence is being confused with business memory storage.
5. Decide whether the work needs a dedicated V3 runtime or memory task.
6. Choose the smallest validation path for the touched backend behavior.

## Minimum evidence

Report:

- whether the runtime/formal boundary changed
- which memory or writeback concepts were touched
- whether runtime memory remains open and self-editable
- whether formal object writeback remains backend-governed
- whether a follow-up task is required

## Stop conditions

Stop and escalate if:

- runtime memory is treated as a formal business object without governance
- formal writeback is blocked merely because memory is inferred or hypothetical
- LangGraph checkpoints are made the only long-term business memory store
- V3 runtime implementation starts without an opened task
- MCP or DB tools expose unrestricted formal-object writes
