# Backend AGENTS

## 1. Scope

This file applies to work under `backend/`.

When a task touches `backend/`, agents must still read:

1. root `AGENTS.md`
2. `docs/README.md`
3. `docs/delivery/tasks/_active.md`
4. the current task / handoff

This file adds backend-specific rules. It does not replace repository-level workflow rules.

---

## 2. Current Backend Role

The backend is the current formal product truth layer for V1.

At the current stage:

- `FastAPI` remains the API edge
- `backend/api/services.py` remains the main product-backend coordination layer
- `backend/runtime/` is the execution boundary, not the product truth layer
- the shipped persistence baseline is still `SQLite`

Agents must not silently turn the current minimal backend into a broad platform rewrite.

---

## 3. Current Default Backend Architecture

Unless a task explicitly changes the architecture baseline, prefer the following defaults:

- keep `FastAPI + SQLAlchemy + Pydantic v2` as the minimum formal backend stack
- keep product object truth in backend models and services, not in runtime session state
- keep runtime orchestration concerns under `backend/runtime/`
- keep API schemas, runtime payload schemas, and persisted JSON payload validation centered on `Pydantic`

Current tooling decisions for backend follow-up work are:

- `Pydantic` is the schema core now
- `LangGraph` is allowed only as a future runtime/orchestration layer under `backend/runtime/`
- `MCP` is allowed only as a tool / resource protocol boundary, not as the internal backend service boundary
- `Langfuse` is the preferred observability direction for the current repo stage
- `Postgres` is the next recommended persistence baseline, but it is not the current default yet
- `pgvector` is optional and should only be introduced when retrieval / embedding use cases enter scope
- `MCP Toolbox for Databases` must be treated as developer / ops augmentation or least-privilege custom tooling, not as unrestricted production agent SQL access

Avoid by default:

- moving all backend flow into `LangGraph` before a dedicated runtime task exists
- treating `MCP` as a replacement for direct Python service calls
- introducing `LangSmith` and `Langfuse` together without an explicit observability decision
- switching to `Postgres` or `pgvector` without a dedicated migration task and docs update
- exposing arbitrary SQL execution to product runtime agents

---

## 4. Backend Tool Boundaries

Backend work should prefer the smallest relevant local commands.

Typical commands:

```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install -e backend
backend/.venv/bin/python -m pytest backend/tests
backend/.venv/bin/alembic upgrade head
backend/.venv/bin/alembic check
backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
curl http://127.0.0.1:8013/health
```

Use only the subset relevant to the task.

Do not claim backend validation passed unless the command or smoke check actually succeeded.

### Backend secrets and LLM keys

Backend LLM secrets are allowed only through process environment variables or local `backend/.env` files that remain ignored by Git.

- Do not read or print `backend/.env` contents. Presence checks are enough.
- Do not echo `OPENCLAW_BACKEND_LLM_API_KEY`, Authorization headers, or provider secrets in shell output, logs, docs, task files, handoffs, PR descriptions, or final answers.
- Do not run backend commands with shell tracing (`set -x`) when `.env` is sourced or secret-bearing environment variables are present.
- Before real LLM smoke/eval/demo work, confirm `backend/.env` is ignored with `git check-ignore -v backend/.env` if there is any doubt.
- LLM traces may contain model output for local development, but must not record API keys, Authorization headers, full request bodies, or complete prompt messages unless a future task explicitly changes that policy.
- Do not stage local DBs, trace JSON, `.env` files, or provider console exports that contain secret-like identifiers.

---

## 5. Backend Validation Ladder

Use the lightest meaningful validation that matches the risk level.

### Level 0: Docs / rules only

Use when only `docs/`, task, handoff, or backend guardrails change.

Minimum expectation:

- document consistency checks such as `git diff --check`

### Level 1: Low-risk backend source edits

Use for:

- serializer-only changes
- low-risk schema shaping
- small service logic changes without contract changes

Minimum expectation:

- `backend/.venv/bin/python -m pytest backend/tests`

### Level 2: API / contract / persistence wiring changes

Use for:

- `schemas.py`
- `main.py`
- `database.py`
- `services.py` changes that affect API behavior

Minimum expectation:

- backend tests
- `alembic upgrade head` on the relevant local database
- backend startup
- `/health` smoke check

### Level 3: Runtime boundary / write-path changes

Use for:

- `backend/runtime/` changes
- `AgentRun` flow changes
- formal object writeback changes

Minimum expectation:

- backend tests
- backend startup
- at least one manual API flow check relevant to the changed path

### Level 4: Storage / migration / environment-sensitive changes

Use for:

- SQLite to Postgres migration work
- `pgvector` introduction
- observability vendor integration
- `MCP` tool server / DB tool exposure
- config / secret / deployment assumption changes

Minimum expectation:

- a dedicated task or spec
- explicit risk notes
- environment-specific verification evidence

If Level 4 conditions are present and the task does not already authorize them, stop and escalate.

---

## 6. High-Risk Backend Files And Areas

Be conservative when touching:

- `backend/api/main.py`
- `backend/api/services.py`
- `backend/api/models.py`
- `backend/api/schemas.py`
- `backend/api/database.py`
- `backend/api/config.py`
- `backend/api/logging_utils.py`
- `backend/alembic/*`
- `backend/runtime/*`
- `backend/pyproject.toml`
- `backend/data/app.db`

Special care is required because these files define:

- public API behavior
- formal object shape
- persistence assumptions
- runtime execution boundary
- local environment behavior

Do not hand-edit `backend/data/app.db` as if it were source code.

---

## 7. Stop / Escalate Conditions

Stop and explicitly surface the issue when work would:

- change the meaning of the formal backend API contract
- change product direction, scope, or object semantics
- introduce destructive persistence changes or ad-hoc migrations
- move orchestration into `LangGraph` outside `backend/runtime/`
- use `MCP` as the internal backend architecture instead of the tool boundary
- give unrestricted SQL capability to runtime agents or database tools
- switch observability direction without a decision record or task
- require deployment, secret, or production environment changes

When in doubt, prefer documenting the proposed follow-up task instead of silently broadening the implementation.

---

## 8. Backend Definition Of Done

A backend task is not complete unless:

1. the task stayed within the documented scope
2. the smallest relevant validation actually ran, or the missing validation is stated explicitly
3. affected backend docs, task notes, and handoff notes were updated
4. any contract, persistence, or runtime boundary changes are documented
5. the final note clearly states remaining risks or follow-ups

For docs-only backend tasks, completion still requires task / handoff / navigation consistency.
