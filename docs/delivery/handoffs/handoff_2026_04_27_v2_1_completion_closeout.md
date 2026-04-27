# Handoff: V2.1 Completion Closeout

日期：2026-04-27

## Summary

本次完成 V2.1 baseline closeout。PR #24 已合入 `main`，Sales Workspace Kernel、Draft Review ID flow、Postgres persistence chain 和 Draft Review audit baseline 已作为 main 当前状态记录。

## Changed

- 新增 `docs/delivery/tasks/task_v2_1_completion_closeout.md`。
- 新增本 handoff。
- 更新 `README.md`、`docs/README.md`、`docs/delivery/README.md`、`docs/delivery/tasks/_active.md`、`backend/README.md`、`docs/product/roadmap.md`。
- 新增 V2.2 planned task placeholders：
  - `task_v2_2_runtime_langgraph_design.md`
  - `task_v2_2_android_review_history_planning.md`
  - `task_v2_2_search_evidence_boundary_design.md`

## V2.1 Closeout State

- Sales Workspace Kernel backend-only v0：done。
- no-DB FastAPI prototype：done。
- Android read-only workspace demo：done。
- Draft Review routes prototype：done。
- Android Draft Review ID flow prototype：done。
- Postgres / Alembic persistence baseline：done。
- Sales Workspace Postgres migration / repository / API store：done。
- Draft Review Postgres persistence and lifecycle events：done。

## Validation

Actual validation commands:

- `docker compose -f compose.postgres.yml up -d`
- `docker exec openclaw-postgres pg_isready -U openclaw -d openclaw_dev`
- `OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/alembic -c alembic.ini upgrade head`
- `backend/.venv/bin/alembic -c alembic.ini upgrade head`
- `backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py backend/tests/test_sales_workspace_draft_reviews_api.py -q`
- `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_repository.py backend/tests/test_sales_workspace_api_postgres_store.py backend/tests/test_sales_workspace_draft_reviews_postgres_store.py -q`
- `backend/.venv/bin/python -m pytest backend/tests -q`
- `OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND=postgres backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
- `curl http://127.0.0.1:8013/health`
- `./gradlew :app:assembleDebug`
- `./gradlew :app:lintDebug`
- `adb devices`
- `git diff --check`

## Known Limitations

- `adb devices` 检测到一台设备，但本次未安装 / 启动 app；本任务是 closeout 与 build-level verification，没有改 Android 行为。
- 未接真实 Runtime / LangGraph。
- 未接真实 LLM / search / CRM / contact。
- 未实现 Draft Review history read API 或 Android history view。
- 未实现多用户 / 权限 / tenant isolation。

## Recommended Next Step

优先做 `task_v2_2_runtime_langgraph_design.md`，不要直接接真实 LLM。先定义 Runtime / LangGraph 如何生成 `WorkspacePatchDraft`、如何进入 Draft Review、如何处理失败和证据边界。
