# Handoff: V2 Sales Workspace Draft Review Persistence v0

日期：2026-04-27

## Summary

本次完成 Draft Review persistence v0。显式 `postgres` store backend 下，backend-managed Draft Review object 和 lifecycle event 会落入 Postgres；Android review-id flow 的 API 语义保持不变。

## Changed

- 扩展 `backend/sales_workspace/repository.py`：
  - `PostgresDraftReviewStore`
  - `sales_workspace_draft_reviews`
  - `sales_workspace_draft_review_events`
- 更新 `backend/api/sales_workspace.py`，postgres store backend 下 Draft Review routes 使用 persisted review store。
- 新增 `backend/tests/test_sales_workspace_draft_reviews_postgres_store.py`。
- 更新 task：`task_v2_sales_workspace_draft_review_persistence_v0.md`。
- 更新 `_active.md`、`docs/README.md`、`docs/delivery/README.md`。

## Behavior

- Create review：写入 current review row，并追加 `created` event。
- Accept review：更新状态为 `reviewed`，追加 `reviewed` event。
- Reject review：更新状态为 `rejected`，追加 `rejected` event。
- Apply reviewed draft：由 Sales Workspace Kernel apply 后更新状态为 `applied`，追加 `applied` event。
- Stale apply / stale accept：workspace 不发生第二次写入，review 标记 `expired`，追加 `expired` / `apply_failed` event。
- memory / JSON store path 未改变。

## Validation

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_draft_reviews_api.py -q`
- `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_draft_reviews_postgres_store.py -q`
- `git diff --check`

## Known Limitations

- Draft Review history read API / Android history view 未实现。
- 多用户 / 权限 / tenant isolation 仍只是 metadata 预留。
- 未接正式 Runtime / LangGraph、真实 LLM、search、CRM 或 contact。

## Recommended Next Step

先做一次 post-persistence chain review，再决定是否进入 Runtime / LangGraph design、Android review history view，或 DB hardening。
