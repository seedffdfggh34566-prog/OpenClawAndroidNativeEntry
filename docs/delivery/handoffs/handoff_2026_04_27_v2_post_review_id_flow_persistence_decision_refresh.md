# Handoff: V2 Post Review-ID Flow Persistence Decision Refresh

日期：2026-04-27

## Summary

PR #19 合入后，Android Draft Review ID flow prototype 已进入 `main`。本次对 persistence direction 做了 docs-only refresh：V2 如果继续向 MVP 推进，下一步应先设计正式 persistence baseline，优先评估 Postgres / Alembic，而不是直接进入 LangGraph / LLM 或继续扩 Android UI。

## Changed

- 更新 ADR-007 addendum，记录 post-review-id-flow persistence 判断。
- 新增 completed task：`task_v2_post_review_id_flow_persistence_decision_refresh.md`。
- 新增下一项唯一开放任务：`task_v2_sales_workspace_persistence_baseline_design.md`。
- 新增 planned / blocked 占位任务：
  - `task_v2_sales_workspace_draft_review_persistence_schema.md`
  - `task_v2_runtime_langgraph_design.md`
  - `task_v2_android_review_history_view.md`
- 更新 `docs/README.md`、`docs/delivery/README.md`、`docs/delivery/tasks/_active.md`。

## Decision Notes

- JSON file store 继续作为 prototype continuity，不是正式 persistence baseline。
- SQLite / Alembic 是备选本地过渡方案，不作为默认推荐。
- Postgres / Alembic 是下一阶段 persistence baseline design 的优先评估方向。
- 当前不开放 DB migration、SQLAlchemy model、backend route change、Android UI expansion、LangGraph、LLM/search/contact/CRM。

## DB Risk Classification

- Risk category：storage baseline decision refresh only。
- Schema / migration files changed：no。
- SQLAlchemy / Alembic / SQLite / Postgres implementation changed：no。
- Dedicated follow-up required：yes，`task_v2_sales_workspace_persistence_baseline_design.md`。

## Validation

- `rg "Android Draft Review ID flow prototype 已完成|task_v2_android_draft_review_id_flow_prototype.md" docs/README.md docs/delivery/README.md docs/delivery/tasks/_active.md`
- `rg "Postgres|SQLite|JSON file store|persistence baseline design|不实现 DB|不接 LangGraph" docs/adr docs/delivery docs/README.md`
- `git diff --check`
- `git status --short`

## Known Limitations

- 本次没有实现 DB schema 或 migration。
- 本次没有重新运行 backend / Android build，因为没有代码变更。
- Postgres 是否成为最终 baseline 仍需下一项 design task 冻结。

## Recommended Next Step

执行 `task_v2_sales_workspace_persistence_baseline_design.md`，只做 persistence baseline design，不写 migration。
