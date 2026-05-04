.PHONY: dev dev-smoke test backend-test alembic clean

dev:
	./scripts/start-dev.sh

dev-smoke:
	./scripts/start-dev.sh --smoke

test:
	backend/.venv/bin/python -m pytest backend/tests -q

backend-test:
	backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -x -q

alembic:
	backend/.venv/bin/alembic -c alembic.ini upgrade head

clean:
	@echo "Stop dev servers: kill \$$(lsof -t -i :8013) \$$(lsof -t -i :5173) 2>/dev/null || true"
