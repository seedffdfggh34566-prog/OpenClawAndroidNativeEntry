# Handoff: V2 Draft Review Routes Prototype

日期：2026-04-27

## Summary

本次实现 backend-managed `WorkspacePatchDraftReview` prototype routes。

Runtime / Product Sales Agent execution layer 仍只产出 `WorkspacePatchDraft`。Backend 负责创建 review object、生成 non-mutating preview、记录 accept / reject、并在 reviewed apply 时由 Sales Workspace Kernel materialize `WorkspacePatch` 后正式写回 workspace。

## Changed

- 新增 draft review model / store：
  - `backend/sales_workspace/draft_reviews.py`
- 新增 draft review API prototype：
  - `POST /sales-workspaces/{workspace_id}/draft-reviews`
  - `GET /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}`
  - `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/review`
  - `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/apply`
  - `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/reject`
- 新增 API tests：
  - `backend/tests/test_sales_workspace_draft_reviews_api.py`
- 同步 task / entry docs / ADR / contract implementation status。

## Behavior Notes

- `POST /draft-reviews` 只创建 backend-managed review object，不 mutate workspace。
- `review decision=accept` 只允许 `previewed -> reviewed`，并检查 current workspace version。
- `review decision=reject` 与 `/reject` 只允许 `previewed -> rejected`。
- `apply` 只允许 `reviewed -> applied`。
- stale accept / apply 返回 `409 workspace_version_conflict`，review 标记为 `expired`，workspace 不发生额外写入。
- terminal statuses：`applied`、`rejected`、`expired`。
- JSON file store 复用 `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR`，draft reviews 存在 `draft_reviews/{workspace_id}/{draft_review_id}.json`。

## Validation

已运行：

- `PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py backend/tests/test_sales_workspace_draft_reviews_api.py -q`
- `PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests -q`
- `PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/alembic -c alembic.ini upgrade head`
- backend startup + `/health` smoke on `127.0.0.1:8013`
- `python3 scripts/seed_sales_workspace_demo.py --base-url http://127.0.0.1:8013 --workspace-id ws_demo`
- Python urllib smoke：preview -> create draft review -> accept -> apply -> ranking

结果：

- `31 passed`
- `78 passed`
- `alembic upgrade head` passed
- `/health` returned `{"status":"ok"}`
- smoke flow returned `draft_review_runtime_v4` and confirmed `cand_runtime_001` rank #1 at workspace version 4

## Known Limitations

- Draft review storage 仍是 prototype storage，不是正式 DB-backed persistence baseline。
- 没有 SQLAlchemy model、Alembic migration、SQLite schema 或 Postgres schema。
- 没有 Android UI 改动；当前 Android prototype 仍可继续用 raw patch draft apply endpoint。
- 没有接真实 LLM、正式 LangGraph graph、search、contact 或 CRM。
- 没有实现 review list / pagination / auth / tenant boundary。

## Recommended Next Step

先完成本 PR review。之后合理下一步是让 Android review UI 从 raw `patch_draft` apply 切到 `draft_review_id` flow；仍应作为单独 task 创建，不自动开放。
