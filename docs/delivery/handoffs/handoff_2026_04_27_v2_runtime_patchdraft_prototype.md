# Handoff：V2 Runtime PatchDraft prototype

日期：2026-04-27

## 1. 本次完成

- 合并 PR #9 后，从最新 `origin/main` 创建 `codex/v2-runtime-patchdraft-prototype`。
- 同步 post-JSON-store 入口层，开放并完成 `task_v2_sales_workspace_runtime_patchdraft_prototype.md`。
- 新增 deterministic `WorkspacePatchDraft` runtime schema / generator。
- 新增 draft -> `WorkspacePatch` materialization helper。
- 新增 prototype-only endpoint：

```text
POST /sales-workspaces/{workspace_id}/runtime/patch-drafts/prototype
```

- endpoint 读取当前 workspace，生成 Runtime draft，materialize 为正式 patch，再交给 Sales Workspace Kernel apply。
- Runtime 不直接写 formal objects，不写 ranking board，不写 generated Markdown。

---

## 2. 主要文件

- `backend/runtime/sales_workspace_patchdraft.py`
- `backend/api/sales_workspace.py`
- `backend/tests/test_sales_workspace_api.py`
- `docs/reference/api/sales-workspace-kernel-v0-contract.md`
- `docs/delivery/tasks/task_v2_sales_workspace_runtime_patchdraft_prototype.md`
- `docs/delivery/tasks/_active.md`

---

## 3. 已验证

```bash
PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py -q
PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests -q
PYTHONPATH=$PWD OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_runtime_patchdraft_alembic.db /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/alembic -c alembic.ini upgrade head
PYTHONPATH=$PWD OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_runtime_patchdraft_smoke.db OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR=/tmp/openclaw_runtime_patchdraft_store /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
curl http://127.0.0.1:8013/health
python3 scripts/seed_sales_workspace_demo.py --base-url http://127.0.0.1:8013 --workspace-id ws_demo
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/runtime/patch-drafts/prototype \
  -H 'Content-Type: application/json' \
  -d '{"base_workspace_version":3,"instruction":"add one deterministic runtime candidate"}'
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/ranking-board/current
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/projection
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/context-packs \
  -H 'Content-Type: application/json' \
  -d '{"task_type":"research_round","token_budget_chars":6000,"top_n_candidates":5}'
```

结果：

- targeted backend/API tests：`19 passed`。
- full backend tests：`66 passed`。
- Alembic upgrade head：通过；未修改 migration。
- backend startup + `/health` smoke：通过。
- seed script：成功创建 `ws_demo` 到 version `3`。
- runtime patchdraft prototype：成功生成 `draft_runtime_v4` / `patch_runtime_v4`，workspace version 变为 `4`。
- ranking：`cand_runtime_001` / `Runtime Draft Co` 排名第一，score=`365`；`cand_d` 下移第二。
- projection 和 ContextPack 均能读取 `Runtime Draft Co` / `cand_runtime_001`。

---

## 4. 已知边界

- 本轮是 deterministic prototype，不调用真实 LLM。
- 本轮不实现正式 LangGraph graph、checkpoint、resume 或 HITL lifecycle。
- 本轮不接 search、ContactPoint、CRM 或自动触达。
- 本轮不新增 Android 写入 UI。
- 本轮不修改 SQLAlchemy model、database wiring 或 Alembic migration。
- `WorkspacePatchDraft` 是 Runtime output schema，不是正式 workspace 主存对象。

---

## 5. 推荐下一步

当前无 next queued task。

后续规划层建议三选一：

- 正式 Runtime / LangGraph integration。
- Android workspace review / write UI，用于人工审阅并接受 Runtime draft。
- persistence-backed API / DB schema。
