#!/bin/bash
set -euo pipefail

# OpenClaw V3 Dev Environment Launcher
# Usage: ./scripts/start-dev.sh [--smoke]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_PORT=8013
WEB_PORT=5173
BACKEND_LOG="/tmp/openclaw_backend.log"
WEB_LOG="/tmp/openclaw_web.log"

cd "$REPO_ROOT"

# Check if ports are already in use
BACKEND_ALREADY_RUNNING=false
WEB_ALREADY_RUNNING=false
if lsof -i :"${BACKEND_PORT}" >/dev/null 2>&1; then
    echo "WARNING: Port ${BACKEND_PORT} is already in use. Backend may already be running."
    BACKEND_ALREADY_RUNNING=true
fi
if lsof -i :"${WEB_PORT}" >/dev/null 2>&1; then
    echo "WARNING: Port ${WEB_PORT} is already in use. Web may already be running."
    WEB_ALREADY_RUNNING=true
fi

# If both are already running, skip to smoke check / ready message
if [[ "$BACKEND_ALREADY_RUNNING" == true && "$WEB_ALREADY_RUNNING" == true ]]; then
    echo "==> Both services already running. Skipping start."
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    echo ""
    echo "========================================"
    echo "Dev Environment Already Running"
    echo "========================================"
    echo "Web /lab:  http://${LOCAL_IP}:${WEB_PORT}/lab"
    echo "Backend:   http://127.0.0.1:${BACKEND_PORT}"
    echo ""
    echo "Stop: kill \$(lsof -t -i :${BACKEND_PORT}) \$(lsof -t -i :${WEB_PORT})"
    if [[ "${1:-}" == "--smoke" ]]; then
        echo ""
        echo "==> Level A smoke check..."
        curl -sf "http://127.0.0.1:${BACKEND_PORT}/health" >/dev/null || { echo "ERROR: Backend health check failed"; exit 1; }
        curl -sf "http://127.0.0.1:${WEB_PORT}/lab" >/dev/null || { echo "ERROR: Web /lab check failed"; exit 1; }
        echo "==> Level A smoke check passed"
    fi
    exit 0
fi

# Check .env exists
if [[ ! -f backend/.env ]]; then
    echo "WARNING: backend/.env not found. Backend may fail to start."
fi

# Run Alembic migrations
echo "==> Running Alembic migrations..."
backend/.venv/bin/alembic -c alembic.ini upgrade head

# Start backend (only if not already running)
if [[ "$BACKEND_ALREADY_RUNNING" == false ]]; then
    echo "==> Starting backend (127.0.0.1:${BACKEND_PORT})..."
    cd backend
    nohup .venv/bin/python -m uvicorn backend.api.main:app \
        --host 127.0.0.1 --port "${BACKEND_PORT}" --reload \
        > "${BACKEND_LOG}" 2>&1 &
    BACKEND_PID=$!
    cd ..
fi

# Start web (only if not already running)
if [[ "$WEB_ALREADY_RUNNING" == false ]]; then
    echo "==> Starting web (0.0.0.0:${WEB_PORT})..."
    cd web
    nohup npx vite --host 0.0.0.0 --port "${WEB_PORT}" \
        > "${WEB_LOG}" 2>&1 &
    WEB_PID=$!
    cd ..
fi

# Wait for readiness
echo "==> Waiting for readiness..."
for i in {1..30}; do
    if curl -sf "http://127.0.0.1:${BACKEND_PORT}/health" >/dev/null 2>&1; then
        echo "==> Backend ready (PID: ${BACKEND_PID})"
        break
    fi
    sleep 1
done

for i in {1..30}; do
    if curl -sf "http://127.0.0.1:${WEB_PORT}/" >/dev/null 2>&1; then
        echo "==> Web ready (PID: ${WEB_PID})"
        break
    fi
    sleep 1
done

LOCAL_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "========================================"
echo "Dev Environment Ready"
echo "========================================"
echo "Web /lab:  http://${LOCAL_IP}:${WEB_PORT}/lab"
echo "Backend:   http://127.0.0.1:${BACKEND_PORT}"
echo ""
echo "PIDs: backend=${BACKEND_PID}, web=${WEB_PID}"
echo "Logs: backend=${BACKEND_LOG}, web=${WEB_LOG}"
echo ""
echo "Stop: kill ${BACKEND_PID} ${WEB_PID}"

# Level A smoke check if requested
if [[ "${1:-}" == "--smoke" ]]; then
    echo ""
    echo "==> Level A smoke check..."
    curl -sf "http://127.0.0.1:${BACKEND_PORT}/health" >/dev/null || {
        echo "ERROR: Backend health check failed"
        exit 1
    }
    curl -sf "http://127.0.0.1:${WEB_PORT}/lab" >/dev/null || {
        echo "ERROR: Web /lab check failed"
        exit 1
    }
    echo "==> Level A smoke check passed"
fi
