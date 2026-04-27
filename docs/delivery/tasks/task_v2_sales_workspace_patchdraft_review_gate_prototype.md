# Task：V2 Sales Workspace PatchDraft review gate prototype

更新时间：2026-04-27

## 1. 任务定位

- 任务名称：V2 Sales Workspace PatchDraft review gate prototype
- 当前状态：`done`
- 优先级：P0

本任务在 deterministic Runtime PatchDraft prototype 完成后，补上真实 LLM / LangGraph 接入前必须有的 review gate：Runtime 可以生成 draft preview，但正式 workspace 写入必须通过显式 apply。

本任务只做 prototype，不持久化 draft，不接真实 LLM，不实现正式 LangGraph graph，不接 search/contact/CRM，不新增 Android 写入 UI，不进入 SQLAlchemy / Alembic / SQLite schema。

---

## 2. 任务目标

实现一个最小闭环：

```text
preview Runtime WorkspacePatchDraft
-> materialize preview WorkspacePatch
-> derive preview ranking without mutating workspace
-> explicit apply reviewed WorkspacePatchDraft
-> Sales Workspace Kernel validate/apply
```

核心原则：

- `preview` 不改变 workspace state。
- `apply` 必须接收客户端回传的 `WorkspacePatchDraft`。
- Runtime 不直接写 formal workspace objects。
- Runtime 不直接写 CandidateRankingBoard、Markdown projection 或 ContextPack。
- Sales Workspace Kernel 仍是唯一正式写回裁决层。

---

## 3. In Scope

- 新增 prototype-only preview endpoint：

```text
POST /sales-workspaces/{workspace_id}/runtime/patch-drafts/prototype/preview
```

- 新增 prototype-only apply endpoint：

```text
POST /sales-workspaces/{workspace_id}/runtime/patch-drafts/prototype/apply
```

- `preview` 返回 `patch_draft`、materialized `patch`、`preview_workspace_version`、`preview_ranking_board`、`would_mutate=false`。
- `apply` 返回 `patch_draft`、materialized `patch`、`workspace`、`commit`、`ranking_board`。
- 保留旧 auto-apply prototype endpoint，不删除。
- 补充 API tests，覆盖 preview no-mutate、apply success、version conflict、path mismatch、missing workspace 与 derived outputs。
- 同步 docs entry、reference contract、task、handoff。

---

## 4. Out of Scope

- 持久化 draft。
- 真实 LLM。
- 正式 LangGraph graph。
- search provider。
- source URL fetch verification。
- ContactPoint。
- CRM pipeline。
- Android 写入 UI。
- SQLAlchemy ORM。
- Alembic migration。
- SQLite schema change。
- Postgres / pgvector。
- Runtime 直接写正式 workspace object。
- Runtime 直接编辑 generated Markdown。

---

## 5. 预期行为

Preview request:

```json
{
  "base_workspace_version": 3,
  "instruction": "add one deterministic runtime candidate"
}
```

Preview response:

```json
{
  "patch_draft": {},
  "patch": {},
  "preview_workspace_version": 4,
  "preview_ranking_board": {},
  "would_mutate": false
}
```

Apply request:

```json
{
  "patch_draft": {}
}
```

Apply response:

```json
{
  "patch_draft": {},
  "patch": {},
  "workspace": {},
  "commit": {},
  "ranking_board": {}
}
```

错误行为：

- missing workspace：`404 not_found`
- path workspace 与 draft workspace 不一致：`422 validation_error`
- version mismatch：`409 workspace_version_conflict`
- invalid draft：`422 patchdraft_validation_error`
- 任意失败不得 mutate workspace。

---

## 6. 验证标准

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
git diff --check
git status --short
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

## 7. 完成后状态

本任务完成后仍无 next queued implementation task。

后续若继续推进，应由规划层单独选择：

- Android workspace review UI。
- 正式 Runtime / LangGraph integration。
- persistence-backed API / DB schema。
