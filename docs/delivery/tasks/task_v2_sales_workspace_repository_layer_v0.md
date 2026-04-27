# Task: V2 Sales Workspace Repository Layer v0

状态：done

更新时间：2026-04-27

## Objective

在 Sales Workspace persistence migration v0 完成后，实现 Pydantic object 与 Postgres schema 之间的 repository layer。

## Blocker

已由长线程执行计划开放，且 persistence migration v0 已完成。

## Scope Placeholder

- 读写 `SalesWorkspace` 及其正式子对象。
- 维护 `workspace_version` optimistic concurrency。
- 写入 append-only patch commit record。
- 保持现有 API contract 语义。

## Result

已完成：

- 新增 repository module：`backend/sales_workspace/repository.py`。
- 新增 `PostgresWorkspaceStore`，接口兼容现有 workspace store。
- 支持 create / get / save / apply_patch。
- `apply_patch` 在事务内执行 workspace row lock、version 校验、kernel apply、object row sync、append-only patch commit insert。
- `get` 从 root `payload_json` 还原 `SalesWorkspace`。
- 新增 Postgres repository tests：`backend/tests/test_sales_workspace_repository.py`。
- 未切换 API 默认 store，未改 Android，未接 Runtime / LangGraph。

## Actual Validation

- `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_repository.py -q`
- `backend/.venv/bin/python -m pytest backend/tests/sales_workspace -q`
- `git diff --check`

## Out Of Scope Until Unblocked

- 不新增 API route。
- 不改 Android。
- 不接 Runtime / LangGraph。
- 不接 LLM / search / CRM / contact。
