---
name: delivery-review
description: Review a completed task or commit for architecture compliance, docs sync, validation evidence, secret safety, and critical defects before handoff. Trigger phrases: "review this delivery", "check this commit before handoff", "delivery review", "review my changes".
---

# Delivery Review

Review the current branch's changes relative to `main` before handoff or task closeout. Focus on the V3 sandbox-first, memory-native backend (`backend/`, `web/`).

## Read first

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/delivery/tasks/_active.md`
4. The current task file and handoff, if any
5. `git diff main...HEAD`

## Review dimensions

1. **Architecture compliance**: Does the change align with V3 direction (ADR-009, sandbox-first, memory-native, working state)? Does it respect current runtime, API, and persistence boundaries?
2. **Docs sync**: Is the task/handoff updated to reflect what actually changed? Are relevant ADRs, architecture docs, or API contracts updated if affected?
3. **Validation evidence**: Were relevant tests or build checks run? Look for pytest results, gradle build output, or explicit validation notes. Flag missing evidence.
4. **Secret safety**: Scan the diff for accidental commits of `.env`, API keys, bearer tokens, private keys, or console metric IDs.
5. **Code quality**: Flag only severe defects (logic errors, race conditions, injection risks, unhandled exceptions at boundaries). Do not nitpick style or naming.

## Output

Report findings in the conversation. Do not enforce a fixed template, but cover all five dimensions explicitly. For each dimension, state:
- status (pass / concern / fail)
- brief evidence or reasoning

If the user passes `--save`, write the review to a file next to the current handoff or in `docs/delivery/reviews/` with a timestamped name.

## Stop conditions

Stop and escalate if:
- there is no current task or the diff is empty
- a secret appears to have been committed
- the change contradicts an active ADR or architecture boundary
