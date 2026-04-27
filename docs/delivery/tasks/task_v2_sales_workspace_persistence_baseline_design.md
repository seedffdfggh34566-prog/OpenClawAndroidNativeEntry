# Task: V2 Sales Workspace Persistence Baseline Design

状态：planned / current

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

- persistence baseline design 文档或 ADR addendum。
- 后续 implementation task 的清晰前置条件。
- 对 Postgres / SQLite / JSON prototype store 的取舍结论。

## Validation Criteria

- 文档明确 persistence baseline 推荐方向。
- 文档明确仍不开放 DB migration。
- `_active.md` 不自动开放 implementation task。
- `git diff --check` 通过。
