# Task: V2 Sales Workspace Persistence Baseline Design

状态：done

更新时间：2026-04-27

## Objective

为 Sales Workspace 从 prototype continuity 进入 MVP-ready persistence 做正式 baseline design。

本任务只做设计，不写 migration、不改 backend code、不改变当前 JSON file store prototype。

## Scope

- 比较并冻结 V2 Sales Workspace persistence baseline 的推荐方向。
- 优先评估 Postgres / Alembic 是否作为 MVP baseline。
- 定义需要持久化的对象边界：
  - Workspace。
  - WorkspacePatch / write commit record。
  - ProductProfileRevision。
  - LeadDirection。
  - LeadCandidate。
  - ResearchSource。
  - ResearchObservation。
  - WorkspacePatchDraftReview。
- 明确 derived outputs 的处理原则：
  - RankingBoard。
  - Markdown projection。
  - ContextPack。
- 明确 JSON file store 的后续定位。
- 明确 backend API、Runtime / LangGraph、Android review history 的前置条件。

## Out Of Scope

- 不实现 SQLAlchemy ORM。
- 不写 Alembic migration。
- 不修改 `backend/api/database.py`、`backend/api/models.py` 或 `backend/alembic/`。
- 不新增或修改 FastAPI route。
- 不改 Android。
- 不接 LangGraph / LLM / search / CRM / contact。

## Deliverables

- persistence baseline design 文档：`docs/architecture/workspace/sales-workspace-persistence-baseline.md`。
- ADR-007 addendum。
- 后续 implementation task 的清晰前置条件。
- 对 Postgres / SQLite / JSON prototype store 的取舍结论。

## Result

已完成：

- V2 MVP persistence baseline 冻结为 Postgres / Alembic。
- SQLite 不作为 V2 Sales Workspace runtime fallback。
- JSON file store 只作为 prototype / demo continuity。
- Draft Review 需要长期 audit history。
- MVP baseline 必须支持 multi-workspace。
- multi-user / permission 暂不实现，只允许后续 schema design 预留 metadata。
- 下一项唯一开放任务设为 `task_v2_postgres_dev_environment_baseline.md`。

## Validation Criteria

- 文档明确 persistence baseline 推荐方向。
- 文档明确仍不开放 DB migration。
- `_active.md` 不自动开放 implementation task。
- `git diff --check` 通过。

## Actual Validation

- `rg "Postgres / Alembic|SQLite|JSON file store|Draft Review|audit history|multi-workspace" docs/architecture docs/adr docs/delivery docs/README.md`
- `rg "不写 Alembic|不实现 SQLAlchemy|不改 Android|不接 LangGraph|不接真实 LLM" docs/delivery/tasks/_active.md docs/delivery/tasks/task_v2_sales_workspace_persistence_baseline_design.md docs/delivery/handoffs`
- `rg "task_v2_sales_workspace_persistence_baseline_design.md|sales-workspace-persistence-baseline.md" docs/README.md docs/architecture/README.md docs/delivery/README.md docs/delivery/tasks/_active.md`
- `git diff --check`
- `git status --short`

不运行 backend / Android build；本轮是 Markdown-only design。
