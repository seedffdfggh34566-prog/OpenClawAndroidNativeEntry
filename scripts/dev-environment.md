# Dev Environment Contract

Current canonical local development environment for OpenClaw V3.

## Services

| Service | Command | Host | Port | Notes |
|---|---|---|---|---|
| Backend API | `uvicorn backend.api.main:app` | 127.0.0.1 | 8013 | FastAPI + SQLite |
| Web /lab | `npx vite` | 0.0.0.0 | 5173 | React + Vite proxy |

## Proxy Rules

- Web `/api/*` → `http://127.0.0.1:8013/*` (Vite dev server proxy)

## Database

- Type: SQLite
- Alembic config: `alembic.ini` (repo root)
- Migrations: `backend/alembic/versions/`

## Environment

- `.env` file: `backend/.env` (gitignored)
- Required: `OPENCLAW_BACKEND_LLM_API_KEY`
- Optional: `OPENCLAW_BACKEND_DATABASE_URL` (defaults to SQLite in repo root)

## Health Checks

- Backend: `GET http://127.0.0.1:8013/health` → `{"status":"ok"}`
- Web: `GET http://127.0.0.1:5173/` → HTML response

## Smoke Test Levels

| Level | Command | What it checks | Speed |
|---|---|---|---|
| A (light) | `make dev-smoke` | health + /lab accessible | ~5s |
| B (medium) | `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -x -q` | full sandbox turn with mock LLM | ~30s |
| C (heavy) | `OPENCLAW_BACKEND_RUN_LIVE_LLM_SMOKE=1 pytest backend/tests/...` | real LLM turn | ~60s+ |

## Maintenance Rule

Any change that affects the following MUST update this file AND `scripts/start-dev.sh`:
- Backend listen port or host
- Vite proxy target
- Alembic config location
- Required `.env` variables
- New parallel services (Redis, Celery, etc.)
