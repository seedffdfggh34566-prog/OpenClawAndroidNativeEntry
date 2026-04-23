---
name: backend-contract-sync
description: Use when backend work is closing out and you need to sync code changes with architecture, reference docs, task files, handoffs, and validation notes.
---

# Backend Contract Sync

Use this skill at the end of meaningful backend work to keep docs, task state, and handoff output aligned with the code and validation evidence.

Read these repo files first:

1. `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/README.md`
4. the current backend task and handoff
5. any touched backend reference or architecture docs

## Workflow

1. Review the backend diff and list all changed contract, persistence, runtime, or workflow assumptions.
2. Check whether the current task file reflects the real outcome and status.
3. Check whether the handoff includes:
   - what changed
   - validation run
   - known limits
   - next step
4. Check whether reference and architecture docs need updates.
5. Run `git diff --check` before closing out.

## Must-sync areas

Look at these areas first when relevant:

- `docs/reference/api/`
- `docs/reference/schemas/`
- `docs/architecture/backend/`
- `docs/how-to/operate/`
- `docs/delivery/tasks/`
- `docs/delivery/handoffs/`

## Output checklist

Report:

- which docs were updated
- which docs still need follow-up
- whether task and handoff agree with actual work
- whether validation is recorded clearly
- whether any boundary changes still lack written justification

## Stop conditions

Stop and escalate if:

- direction-layer docs would need semantic changes
- backend stack conclusions conflict with current architecture docs
- there is no legitimate task for the backend implementation being closed out
