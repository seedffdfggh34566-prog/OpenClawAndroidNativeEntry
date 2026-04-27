# Task：V2 Sales Workspace JSON file store prototype

更新时间：2026-04-27

## 1. 任务定位

- 任务名称：V2 Sales Workspace JSON file store prototype
- 当前状态：`done`
- 优先级：P0

本任务在 no-DB FastAPI prototype 和 Android read-only workspace demo 完成后，补一个可选的本地 JSON file store，让 `ws_demo` 可以跨 backend 重启保留。

本任务不是正式 persistence baseline，不开放 SQLite / Alembic、Postgres、Android write path、Runtime / LangGraph、LLM、search 或 CRM。

---

## 2. 任务目标

让 Sales Workspace Backend API prototype 在显式设置环境变量时使用 JSON 文件保存 workspace state：

```bash
OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR=/tmp/openclaw_sales_workspace_store
```

未设置该环境变量时，backend 继续使用原有 app-local `InMemoryWorkspaceStore`。

---

## 3. In Scope

- 增加 `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR` 配置。
- 增加 `JsonFileWorkspaceStore`。
- 每个 workspace 存为一个 JSON 文件。
- `get()` 支持从文件 lazy load。
- `save()` 使用临时文件加 atomic replace。
- 补充 API tests，覆盖跨 app/store 实例 reload、version conflict 不改文件、derived outputs reload 后仍可读。
- 同步 `_active.md`、ADR addendum 与 handoff。

---

## 4. Out of Scope

- 新增或扩展 Sales Workspace endpoint。
- 改变 API request / response contract。
- SQLAlchemy ORM。
- Alembic migration。
- SQLite schema change。
- Postgres / pgvector。
- Android 写入 UI。
- Runtime / LangGraph integration。
- 真实 LLM。
- 联网搜索 / search provider。
- CRM / ContactPoint / 自动触达。

---

## 5. 已实现行为

- 默认行为保持 app-local in-memory store。
- 设置 `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR` 后启用 JSON file store。
- 成功 create / patch 后写入 workspace JSON。
- backend 重启或新 app 实例可从同一目录读取 workspace。
- version conflict 返回 `409 workspace_version_conflict`，且不会改写 workspace JSON 文件。
- ranking board、Markdown projection、ContextPack 仍由结构化 workspace state 派生。

---

## 6. 已做验证

```bash
PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py -q
PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests -q
PYTHONPATH=$PWD OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_sales_workspace_json_store_alembic.db /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/alembic -c alembic.ini upgrade head
PYTHONPATH=$PWD OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_sales_workspace_json_store_smoke.db OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR=/tmp/openclaw_sales_workspace_store /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
curl http://127.0.0.1:8013/health
python3 scripts/seed_sales_workspace_demo.py --base-url http://127.0.0.1:8013 --workspace-id ws_demo
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/ranking-board/current
```

结果：

- targeted backend/API tests：`16 passed`。
- full backend tests：`63 passed`。
- Alembic upgrade head：通过；未修改 migration。
- backend startup + `/health` smoke：通过。
- seed script：成功写入 `ws_demo`，`cand_d` 排名第一，score=`230`。
- backend 重启后 ranking curl 仍返回 `cand_d` / `D Company` / `230`。

完整验证结果以 handoff 为准。

---

## 7. 后续状态

本任务完成后仍无自动排定下一项任务。

后续如果继续推进，应由规划层单独选择：

- 正式 persistence-backed API / DB schema。
- Runtime / LangGraph WorkspacePatchDraft integration。
- Android workspace 交互体验增强。
