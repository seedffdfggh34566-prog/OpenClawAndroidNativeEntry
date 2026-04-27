# Handoff：V2 Sales Workspace JSON file store prototype

日期：2026-04-27

## 1. 本次完成

- 合并 PR #8 后，从最新 `origin/main` 创建 `codex/v2-sales-workspace-json-store-prototype`。
- 新增可选 JSON file-backed prototype store。
- 增加 `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR` 配置。
- 默认未设置 env 时仍使用 app-local in-memory store。
- JSON store 支持 create / patch 后落盘，后续 app/store 实例 lazy load。
- version conflict 不改写 workspace JSON 文件。
- 同步 ADR-007 addendum、task 与 `_active.md`。

---

## 2. 主要文件

- `backend/api/config.py`
- `backend/api/sales_workspace.py`
- `backend/sales_workspace/store.py`
- `backend/tests/test_sales_workspace_api.py`
- `docs/adr/ADR-007-v2-sales-workspace-persistence-decision.md`
- `docs/delivery/tasks/task_v2_sales_workspace_json_store_prototype.md`
- `docs/delivery/tasks/_active.md`

---

## 3. 已验证

```bash
PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py -q
PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests -q
PYTHONPATH=$PWD OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_sales_workspace_json_store_alembic.db /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/alembic -c alembic.ini upgrade head
PYTHONPATH=$PWD OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_sales_workspace_json_store_smoke.db OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR=/tmp/openclaw_sales_workspace_store /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
curl http://127.0.0.1:8013/health
python3 scripts/seed_sales_workspace_demo.py --base-url http://127.0.0.1:8013 --workspace-id ws_demo
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/ranking-board/current
git diff --check
git status --short
```

结果：

- `16 passed`
- full backend tests：`63 passed`。
- Alembic upgrade head：通过；未修改 migration。
- backend startup + `/health` smoke：通过。
- seed script：成功写入 `ws_demo`，`cand_d` 排名第一，score=`230`。
- backend 重启后 ranking curl 仍返回 `cand_d` / `D Company` / `230`。
- `git diff --check`：通过。
- `git status --short`：仅包含本任务相关文件。

---

## 4. 已知边界

- JSON file store 是 prototype continuity 支撑，不是正式 persistence baseline。
- 本轮没有新增 endpoint。
- 本轮没有修改 SQLAlchemy model、database wiring 或 Alembic migration。
- 本轮没有开放 Android 写入 UI。
- 本轮没有接 Runtime / LangGraph、真实 LLM、search、CRM 或 ContactPoint。

---

## 5. 推荐下一步

当前仍无自动排定下一项任务。

后续规划层应在以下方向中选择一个单独建 task：

- 正式 persistence-backed API / DB schema。
- Runtime / LangGraph WorkspacePatchDraft integration。
- Android workspace 交互体验增强。
