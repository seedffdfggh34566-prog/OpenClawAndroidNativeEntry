# Task：V2 Sales Workspace Runtime PatchDraft prototype

更新时间：2026-04-27

## 1. 任务定位

- 任务名称：V2 Sales Workspace Runtime PatchDraft prototype
- 当前状态：`in_progress`
- 优先级：P0

本任务在 no-DB FastAPI prototype、Android read-only demo 和 JSON file store prototype 完成后，打通 Runtime / Product Sales Agent execution layer 到 Sales Workspace Kernel 的最小受控写回边界。

本任务只做 deterministic prototype，不接真实 LLM，不实现正式 LangGraph graph，不接 search/contact/CRM，不新增 Android 写入 UI，不进入 SQLAlchemy / Alembic / SQLite schema。

---

## 2. 任务目标

实现一个最小闭环：

```text
current workspace
-> deterministic Runtime WorkspacePatchDraft
-> backend materialize WorkspacePatch
-> Sales Workspace Kernel validate/apply
-> ranking/projection/context pack update
```

核心原则：

- `WorkspacePatchDraft` 是 Runtime output schema，不是正式主存对象。
- Runtime 不直接写 formal workspace objects。
- Runtime 不直接写 CandidateRankingBoard、Markdown projection 或 ContextPack。
- Sales Workspace Kernel 仍是唯一正式写回裁决层。

---

## 3. In Scope

- 新增 `WorkspacePatchDraft` Pydantic schema。
- 新增 deterministic draft generator。
- 新增 draft -> `WorkspacePatch` materialization helper。
- 新增 prototype-only endpoint：

```text
POST /sales-workspaces/{workspace_id}/runtime/patch-drafts/prototype
```

- response 返回 `patch_draft`、materialized `patch`、`workspace`、`commit`、`ranking_board`。
- 补充 API tests，覆盖 success、version conflict、missing workspace 与 derived outputs。
- 同步 docs entry、task、handoff。

---

## 4. Out of Scope

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

Request:

```json
{
  "base_workspace_version": 3,
  "instruction": "add one deterministic runtime candidate"
}
```

Prototype 固定生成：

- research round：`rr_runtime_001`
- source：`src_runtime_001`
- candidate：`cand_runtime_001`
- observations：fit / pain / timing / source_quality positive signals

成功 apply 后：

- workspace version 递增。
- `cand_runtime_001` 稳定排到 ranking 第一。
- projection 和 ContextPack 可读。

错误行为：

- missing workspace：`404 not_found`
- version mismatch：`409 workspace_version_conflict`
- draft validation failure：`422 patchdraft_validation_error`
- unsupported materialized operation：沿用 `400 unsupported_workspace_operation`
- 任意失败不得 mutate workspace。

---

## 6. 验证标准

```bash
backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py -q
backend/.venv/bin/python -m pytest backend/tests -q
backend/.venv/bin/alembic -c alembic.ini upgrade head
backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
curl http://127.0.0.1:8013/health
python3 scripts/seed_sales_workspace_demo.py --base-url http://127.0.0.1:8013 --workspace-id ws_demo
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/runtime/patch-drafts/prototype \
  -H 'Content-Type: application/json' \
  -d '{"base_workspace_version":3,"instruction":"add one deterministic runtime candidate"}'
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/ranking-board/current
git diff --check
git status --short
```

---

## 7. 完成后状态

本任务完成后仍无 next queued implementation task。

后续若继续推进，应由规划层单独选择：

- 正式 Runtime / LangGraph integration。
- Android workspace write / review UI。
- persistence-backed API / DB schema。
