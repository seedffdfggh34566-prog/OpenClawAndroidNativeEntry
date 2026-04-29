# Handoff: V2.1 Sales Workspace Dev Diagnostics Inspector

日期：2026-04-28

## Changed

- Added a dev-only diagnostics flag: `OPENCLAW_BACKEND_DEV_SALES_WORKSPACE_DIAGNOSTICS_ENABLED=true`.
- Added read-only dev routes:
  - `GET /dev/sales-workspace-inspector`
  - `GET /dev/sales-workspaces`
  - `GET /dev/sales-workspaces/{workspace_id}/diagnostics`
- Added a lightweight HTML inspector for workspace state, formal objects, threads, recent messages, agent runs, context packs, draft reviews, projection files, and raw diagnostics JSON.
- Added store list methods for workspaces, chat agent runs, context packs, and draft reviews across in-memory, JSON file, and Postgres store paths.
- Kept diagnostics read-only; no write, review, apply, repair, schema, migration, or formal product API changes were added.

## Validation

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_diagnostics_inspector.py -q` passed: `3 passed`.
- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_diagnostics_inspector.py backend/tests/test_dev_llm_inspector.py -q` passed: `8 passed`.
- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q` passed: `19 passed, 1 skipped`.
- `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_diag_verify.db backend/.venv/bin/alembic upgrade head` passed.
- Temporary backend smoke on `127.0.0.1:8014` passed for `/health`, `/dev/sales-workspace-inspector`, and `/dev/sales-workspaces`.
- Optional Postgres diagnostics verification was skipped because `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` was not set.

## Known Limits

- The inspector is disabled by default and is intended for local development only.
- JSON store lists persisted workspaces and draft reviews, but chat trace remains process-local unless the Postgres chat trace store is used.
- The inspector does not expose mutation controls, production user UI, auth / tenant policy, CRM, V2.2 search/contact, or formal LangGraph behavior.
- This is task-level diagnostics evidence, not a V2.1 milestone completion claim.

## Recommended Next Step

For manual debugging, start backend with `OPENCLAW_BACKEND_DEV_SALES_WORKSPACE_DIAGNOSTICS_ENABLED=true` and open `http://127.0.0.1:8013/dev/sales-workspace-inspector` alongside Android testing.
