# Handoff：V2 PatchDraft review gate prototype

日期：2026-04-27

## 1. 本次完成

- 合并 PR #10 后，从最新 `origin/main` 创建 `codex/v2-patchdraft-review-gate-prototype`。
- 同步入口层，开放并完成 `task_v2_sales_workspace_patchdraft_review_gate_prototype.md`。
- 新增 PatchDraft review gate prototype endpoints：

```text
POST /sales-workspaces/{workspace_id}/runtime/patch-drafts/prototype/preview
POST /sales-workspaces/{workspace_id}/runtime/patch-drafts/prototype/apply
```

- `preview` 只生成 draft、materialized patch 和 preview ranking，不保存 workspace。
- `apply` 接收客户端回传的 reviewed `WorkspacePatchDraft`，materialize 后交给 Sales Workspace Kernel apply。
- 保留旧 auto-apply prototype endpoint，未删除。
- Runtime 不直接写 formal objects，不写 ranking board，不写 generated Markdown，不持久化 draft。

---

## 2. 主要文件

- `backend/api/sales_workspace.py`
- `backend/tests/test_sales_workspace_api.py`
- `docs/reference/api/sales-workspace-kernel-v0-contract.md`
- `docs/delivery/tasks/task_v2_sales_workspace_patchdraft_review_gate_prototype.md`
- `docs/delivery/tasks/_active.md`

---

## 3. 已验证

```bash
PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py -q
PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests -q
PYTHONPATH=$PWD OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_patchdraft_review_alembic.db /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/alembic -c alembic.ini upgrade head
PYTHONPATH=$PWD OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_patchdraft_review_smoke.db OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR=/tmp/openclaw_patchdraft_review_store /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
curl http://127.0.0.1:8013/health
python3 scripts/seed_sales_workspace_demo.py --base-url http://127.0.0.1:8013 --workspace-id ws_demo
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/runtime/patch-drafts/prototype/preview \
  -H 'Content-Type: application/json' \
  -d '{"base_workspace_version":3,"instruction":"add one deterministic runtime candidate"}'
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/ranking-board/current
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/runtime/patch-drafts/prototype/apply \
  -H 'Content-Type: application/json' \
  -d @/tmp/openclaw_patchdraft_apply_request.json
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/ranking-board/current
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/projection
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/context-packs \
  -H 'Content-Type: application/json' \
  -d '{"task_type":"research_round","token_budget_chars":6000,"top_n_candidates":5}'
```

结果：

- targeted backend/API tests：`24 passed`。
- full backend tests：`71 passed`。
- Alembic upgrade head：通过；未修改 migration。
- backend startup + `/health` smoke：通过。
- seed script：成功创建 `ws_demo` 到 version `3`。
- preview endpoint：返回 `draft_runtime_v4` / `patch_runtime_v4`、`preview_workspace_version=4`、`cand_runtime_001` preview rank #1、`would_mutate=false`。
- preview 后 workspace 仍为 version `3`，正式 ranking 仍由 `cand_d` 排第一。
- apply endpoint：成功写入 reviewed draft，workspace version 变为 `4`，`cand_runtime_001` / `Runtime Draft Co` 排名第一，`cand_d` 下移第二。
- projection 和 ContextPack 均能读取 `Runtime Draft Co` / `cand_runtime_001`。

---

## 4. 已知边界

- 本轮不持久化 draft；客户端负责把 previewed / reviewed draft 回传到 apply。
- 本轮是 deterministic prototype，不调用真实 LLM。
- 本轮不实现正式 LangGraph graph、checkpoint、resume 或 HITL lifecycle。
- 本轮不接 search、ContactPoint、CRM 或自动触达。
- 本轮不新增 Android 写入 UI。
- 本轮不修改 SQLAlchemy model、database wiring 或 Alembic migration。
- `WorkspacePatchDraft` 仍是 Runtime output schema，不是正式 workspace 主存对象。

---

## 5. 推荐下一步

当前无 next queued task。

后续规划层建议三选一：

- Android workspace review UI，让用户查看 preview 并显式 apply。
- 正式 Runtime / LangGraph integration。
- persistence-backed API / DB schema。
