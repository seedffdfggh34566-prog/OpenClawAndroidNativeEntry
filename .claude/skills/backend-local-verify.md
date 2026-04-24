---
name: backend-local-verify
description: Use when backend work needs the lightest meaningful local verification, including pytest, Alembic upgrade, backend startup, health smoke checks, and a concise troubleshooting path.
---

# Backend Local Verify

Use this skill to choose and run the smallest safe local verification for backend work. This skill now also serves as the lightweight backend local runbook.

Read these repo files first:

1. `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/README.md`
4. the current backend task and handoff

If the change touches runtime or persistence boundaries, run `backend-runtime-boundary-guard` or `backend-db-risk-check` first to decide whether verification must be upgraded.

## Commands

Primary commands in this repo are:

- `backend/.venv/bin/python -m pytest backend/tests`
- `backend/.venv/bin/alembic upgrade head`
- `backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
- `curl http://127.0.0.1:8013/health`

Prefer the bundled script for deterministic execution:

```bash
python3 docs/how-to/operate/skills-src/backend-local-verify/scripts/run_backend_verify.py --workspace "$PWD" --mode tests
python3 docs/how-to/operate/skills-src/backend-local-verify/scripts/run_backend_verify.py --workspace "$PWD" --mode migrate
python3 docs/how-to/operate/skills-src/backend-local-verify/scripts/run_backend_verify.py --workspace "$PWD" --mode smoke
python3 docs/how-to/operate/skills-src/backend-local-verify/scripts/run_backend_verify.py --workspace "$PWD" --mode full
```

## Mode selection

- `tests`: low-risk schema or service changes
- `migrate`: persistence wiring or migration validation
- `smoke`: backend startup and `/health`
- `full`: API/persistence changes that need tests + migration + smoke

The script uses a temporary SQLite database unless `OPENCLAW_BACKEND_DATABASE_URL` is already set, so verification does not mutate tracked repository data by default.

## What to report

Always report:

- selected validation level
- commands that actually ran
- what passed
- what failed
- what was skipped
- why any step was skipped
- whether a higher validation level is still needed

## Short troubleshooting path

If verification fails:

1. read the first failing command and error message
2. check whether the failure is test, migration, startup, or health-smoke specific
3. confirm the backend virtualenv exists and dependencies are installed
4. confirm the failure is inside current task scope before fixing it

## Stop conditions

Stop and escalate if:

- the required verification level exceeds the current task authorization
- runtime, persistence, or environment boundaries changed unexpectedly
- the result depends on unresolved contract or schema decisions
- fixing the failure would broaden the task beyond local verification
