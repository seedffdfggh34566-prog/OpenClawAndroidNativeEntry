# Handoff：V2 Sales Workspace Backend API prototype v0

- 日期：2026-04-27
- 状态：done
- 对应任务：`docs/delivery/tasks/task_v2_sales_workspace_backend_api_prototype_v0.md`

---

## 1. 本次变更

实现 no-DB Sales Workspace Backend API prototype v0：

- 新增 `backend/api/sales_workspace.py`。
- 在 `backend/api/main.py` 注册 Sales Workspace router。
- 使用 app-local `InMemoryWorkspaceStore`。
- 新增 `backend/tests/test_sales_workspace_api.py`，直接使用 contract examples 做 smoke 输入。
- 更新 `_active.md`、ADR-007、backend README 与 API contract 文档。

---

## 2. 已实现 API

- `POST /sales-workspaces`
- `GET /sales-workspaces/{workspace_id}`
- `POST /sales-workspaces/{workspace_id}/patches`
- `GET /sales-workspaces/{workspace_id}/ranking-board/current`
- `GET /sales-workspaces/{workspace_id}/projection`
- `POST /sales-workspaces/{workspace_id}/context-packs`

---

## 3. 仍未开放范围

- SQLAlchemy ORM。
- Alembic migration。
- SQLite schema change。
- Android UI。
- Runtime / LangGraph integration。
- LLM / search provider。
- CRM / ContactPoint / 自动触达。

---

## 4. 验证

已执行：

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

## 5. 建议下一步

不要自动继续扩展 API。

建议规划层在以下方向中选择一个单独开 task：

- Android read-only workspace view。
- persistence-backed API / DB schema。
- Runtime / LangGraph WorkspacePatchDraft integration。
