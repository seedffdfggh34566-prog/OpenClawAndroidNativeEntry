# Task: V2 Post Review-ID Flow Persistence Decision Refresh

状态：done

更新时间：2026-04-27

## Objective

在 Android Draft Review ID flow prototype 完成后，重新评估 Sales Workspace 是否应继续停留在 JSON prototype store，还是进入正式 persistence baseline design。

本任务只做 docs / ADR-level decision refresh，不实现数据库、API、Android 或 Runtime。

## Scope

- 更新 `ADR-007-v2-sales-workspace-persistence-decision.md` addendum。
- 明确 JSON file store、SQLite / Alembic、Postgres / Alembic 三条路线的相对位置。
- 创建下一项唯一开放任务：`task_v2_sales_workspace_persistence_baseline_design.md`。
- 创建后续 planned / blocked 任务占位：
  - `task_v2_sales_workspace_draft_review_persistence_schema.md`
  - `task_v2_runtime_langgraph_design.md`
  - `task_v2_android_review_history_view.md`
- 更新 `_active.md`、`docs/README.md`、`docs/delivery/README.md`。
- 新增 handoff。

## Out Of Scope

- 不实现 DB migration。
- 不修改 SQLAlchemy model、Alembic revision、SQLite schema 或 Postgres 配置。
- 不新增或修改 backend route。
- 不改 Android UI。
- 不接正式 LangGraph graph。
- 不接真实 LLM / search / contact / CRM。
- 不改变现有 JSON file store prototype 行为。

## Decision

当前结论：

- JSON file store 继续作为 prototype continuity，不升级为正式 persistence baseline。
- SQLite / Alembic 可作为本地过渡备选，但不作为推荐默认。
- 如果 V2 继续向 MVP 推进，下一步应进入正式 persistence baseline design，优先评估 Postgres / Alembic。
- 在 persistence baseline design 完成前，不开放 DB migration、persistence-backed backend API、正式 Runtime / LangGraph integration 或 Android review history implementation。

## Result

已完成：

- ADR-007 增加 Post Review-ID Flow persistence decision refresh addendum。
- 下一项唯一开放任务设为 `task_v2_sales_workspace_persistence_baseline_design.md`。
- 后续 implementation / design 任务以 planned / blocked 登记，不进入自动执行队列。
- 入口文档已同步到 post-review-id-flow 状态。

## Actual Validation

- `rg "Android Draft Review ID flow prototype 已完成|task_v2_android_draft_review_id_flow_prototype.md" docs/README.md docs/delivery/README.md docs/delivery/tasks/_active.md`
- `rg "Postgres|SQLite|JSON file store|persistence baseline design|不实现 DB|不接 LangGraph" docs/adr docs/delivery docs/README.md`
- `git diff --check`
- `git status --short`

不运行 backend / Android build；本轮是 Markdown-only decision refresh。
