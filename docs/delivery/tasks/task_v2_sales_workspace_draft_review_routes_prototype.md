# Task: V2 Sales Workspace Draft Review Routes Prototype

状态：done

更新时间：2026-04-27

## Objective

实现 backend-managed `WorkspacePatchDraftReview` prototype routes，让 Draft review contract 从 docs-only contract 进入可调用 backend prototype。

该任务目标是把当前 “Android 持有 raw `WorkspacePatchDraft` 并回传 apply” 的 prototype 边界，升级为：

```text
WorkspacePatchDraft
-> backend-managed WorkspacePatchDraftReview
-> explicit review / reject
-> reviewed apply
-> Sales Workspace Kernel formal writeback
```

## Scope

本任务包含：

- 新增 `WorkspacePatchDraftReview` prototype model。
- 新增 in-memory draft review store。
- 复用 `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR` 支撑 JSON file-backed draft review prototype store。
- 实现 draft review routes：
  - `POST /sales-workspaces/{workspace_id}/draft-reviews`
  - `GET /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}`
  - `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/review`
  - `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/apply`
  - `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/reject`
- 覆盖 previewed、reviewed、applied、rejected、expired lifecycle。
- 保持 Sales Workspace Kernel 作为唯一正式 workspace writeback owner。

## Out Of Scope

- 不改 Android UI。
- 不实现正式 LangGraph graph。
- 不接真实 LLM。
- 不接 search / contact / CRM。
- 不写 SQLAlchemy model。
- 不写 Alembic migration。
- 不改变 SQLite / Postgres / production persistence baseline。
- 不新增环境变量。

## Result

已完成：

- 新增 `backend/sales_workspace/draft_reviews.py`。
- 扩展 `backend/api/sales_workspace.py`，实现 draft review prototype routes。
- 扩展 `backend/api/main.py`，初始化 app-local draft review store。
- 新增 `backend/tests/test_sales_workspace_draft_reviews_api.py`。
- stale accept / apply 会返回 `409 workspace_version_conflict`，并把 review 标记为 `expired`；workspace 不发生额外写入。
- rejected / applied / expired 为 terminal state。
- JSON file store 下 draft review object 可跨 app restart 读取并继续 review / apply。

## Validation Criteria

- create draft review 不 mutate workspace。
- accept 后才能 apply。
- rejected draft 不能 apply。
- stale draft 不能 apply，且不得二次写 workspace。
- JSON store reload 后 draft review 仍可读。
- no-DB / no-migration boundary 不变。

## Actual Validation

- `PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py backend/tests/test_sales_workspace_draft_reviews_api.py -q`
- `PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests -q`
- `PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/alembic -c alembic.ini upgrade head`
- `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_draft_review_routes_smoke.db OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR=/tmp/openclaw_draft_review_routes_store PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
- `curl -sS http://127.0.0.1:8013/health`
- `python3 scripts/seed_sales_workspace_demo.py --base-url http://127.0.0.1:8013 --workspace-id ws_demo`
- Python urllib smoke：preview -> create draft review -> accept -> apply -> ranking，确认 `cand_runtime_001` 排名第一，workspace version 为 4。
