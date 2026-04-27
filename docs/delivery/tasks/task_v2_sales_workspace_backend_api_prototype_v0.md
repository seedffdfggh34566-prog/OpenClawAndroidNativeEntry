# Task：V2 Sales Workspace Backend API prototype v0

更新时间：2026-04-27

## 1. 任务定位

- 任务名称：V2 Sales Workspace Backend API prototype v0
- 当前状态：`done`
- 优先级：P0

本任务在 contract examples 完成后，开放一个最小 no-DB FastAPI prototype。

本任务不是正式 persistence baseline，不开放 Android、Runtime / LangGraph、LLM、search 或 CRM。

---

## 2. 任务目标

把现有 `backend/sales_workspace` kernel 暴露为可调用的最小 backend API surface。

实现 endpoints：

- `POST /sales-workspaces`
- `GET /sales-workspaces/{workspace_id}`
- `POST /sales-workspaces/{workspace_id}/patches`
- `GET /sales-workspaces/{workspace_id}/ranking-board/current`
- `GET /sales-workspaces/{workspace_id}/projection`
- `POST /sales-workspaces/{workspace_id}/context-packs`

---

## 3. In Scope

- 新增独立 router：`backend/api/sales_workspace.py`。
- 在 `backend/api/main.py` 注册 router。
- 使用 app-local `InMemoryWorkspaceStore`。
- 使用 `docs/reference/api/examples/sales_workspace_kernel_v0/*.json` 作为 API contract smoke 输入。
- 补充 route tests：`backend/tests/test_sales_workspace_api.py`。
- 同步 `_active.md`、ADR addendum、backend README 与 handoff。

---

## 4. Out of Scope

- SQLAlchemy ORM。
- Alembic migration。
- SQLite schema change。
- Postgres / pgvector。
- Android UI。
- Runtime / LangGraph integration。
- 真实 LLM。
- 联网搜索 / search provider。
- CRM / ContactPoint / 自动触达。

---

## 5. 已实现行为

- `WorkspacePatch` 是唯一写入口。
- ranking board、Markdown projection、ContextPack 都是 derived outputs。
- route 内手动 Pydantic validation，避免改变 V1 API 的全局 validation error 行为。
- duplicate workspace create 返回 `409 workspace_already_exists`。
- path `workspace_id` 与 body `patch.workspace_id` 不一致返回 `422 validation_error`。
- version conflict 返回 `409 workspace_version_conflict`，且不改变 workspace state。

---

## 6. 已做验证

```bash
backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py -q
backend/.venv/bin/python -m pytest backend/tests -q
backend/.venv/bin/alembic upgrade head
OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_sales_workspace_api_prototype_smoke.db backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
curl http://127.0.0.1:8013/health
git diff --check
git status --short
```

结果：

- targeted API/kernel tests：`14 passed`。
- full backend tests：`61 passed`。
- Alembic upgrade head：通过。
- backend startup + `/health` smoke：通过，smoke 使用 `/tmp` 下临时 SQLite URL，未作为正式 persistence baseline。

---

## 7. 后续状态

本任务完成后仍无自动排定下一项任务。

后续若要继续推进，应由规划层明确创建任务，例如：

- Android read-only workspace view。
- persistence-backed API / DB schema。
- Runtime / LangGraph WorkspacePatchDraft integration。
