---
name: task-handoff-sync
description: Use at the end of non-trivial Android, backend, docs, or workflow work to check task, handoff, docs navigation, validation notes, and closeout consistency.
---

# Task Handoff Sync

Use this skill as a final closeout check for meaningful repo work. It is a cross-workflow skill, not Android-specific.

Read these repo files first:

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/delivery/tasks/_active.md`
4. the current task
5. the matching handoff, if one exists

## Workflow

1. Confirm the current task exists and the work belongs to it.
2. Check that task status and actual outcome agree.
3. Check that a handoff exists for meaningful work.
4. Verify the handoff records:
   - what changed
   - what was validated
   - known limits
   - next recommended step
5. Check task and handoff wording:
   - allowed: task done, validation passed, evidence collected, known limits
   - avoid: V3 implementation done, version done, milestone done, product phase complete, production-ready
6. Check whether docs navigation or related specs need updates.
7. Check whether historical V1/V2 docs are being presented as current V3 truth.
8. Run `git diff --check` before closeout.

## What to report

Report:

- task status
- handoff status
- docs navigation status
- validation evidence status
- completion wording status
- V3 vs historical-doc wording status
- missing closeout items

## Stop conditions

Stop and escalate if:

- there is no current task for non-trivial work
- task and handoff disagree about what was completed
- task or handoff casually claims version, milestone, product phase, or product experience completion
- task or handoff claims V3 implementation started/done without a real implementation task
- historical V1/V2 docs are treated as current V3 direction
- direction-layer documents need semantic changes
- the closeout would require deciding product priority or scope
