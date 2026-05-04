---
name: backend-contract-sync
description: Use when backend work is closing out and you need to sync API, runtime, memory, persistence, architecture, task, handoff, and validation notes without replacing general task-handoff-sync.
---

# Backend Contract Sync

Use this skill at the end of meaningful backend work to align backend-specific contracts and docs with code and validation evidence.

Read these repo files first:

1. `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/README.md`
4. the current backend task and handoff
5. touched backend reference, architecture, or V3 docs

Use `task-handoff-sync` for general task/handoff wording. Use this skill for backend API, runtime, memory, persistence, working-state, and customer-intelligence contracts.

## Workflow

1. Review the backend diff and list contract, persistence, runtime, memory, working-state, customer-intelligence, or external-action assumptions changed.
2. Check whether the current task reflects the real outcome.
3. Check whether backend docs need synchronization.
4. Confirm V3 sandbox-first assumptions are described consistently and not replaced by formal object / PatchDraft / Kernel defaults.
5. Confirm validation evidence is recorded.
6. Run `git diff --check` before closeout.

## Must-sync areas

When relevant, check:

- `docs/architecture/v3/`
- `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
- `docs/reference/api/`
- `docs/reference/schemas/`
- `docs/delivery/tasks/`
- `docs/delivery/handoffs/`

## Output checklist

Report:

- backend contract/docs updated
- backend docs still needing follow-up
- task and handoff agreement with actual work
- V3 sandbox-first consistency
- validation evidence status

## Stop conditions

Stop and escalate if:

- direction-layer docs need semantic changes
- implementation conflicts with ADR-009 or V3 architecture
- backend task/handoff claims V3 implementation, milestone, or production readiness without review
- there is no legitimate task for the backend work being closed out
