# Task：V2 Sales Workspace backend API v0

更新时间：2026-04-27

## 1. 任务定位

- 任务名称：V2 Sales Workspace backend API v0
- 建议路径：`docs/delivery/tasks/task_v2_sales_workspace_backend_api_v0.md`
- 当前状态：`planned`
- 优先级：P1

---

## 2. 任务目标

在 API contract 与 persistence decision 完成后，实现 Sales Workspace Kernel backend API v0。

---

## 3. Blocked By

- `task_v2_sales_workspace_api_contract_v0.md`
- `task_v2_sales_workspace_persistence_decision.md`

---

## 4. Out of Scope Until Unblocked

在上游任务完成前，不允许实现：

- FastAPI route。
- DB persistence。
- Android integration。
- Runtime / LangGraph integration。

---

## 5. 验收方向

正式开放后至少应包含：

- API route tests。
- workspace read / patch / projection / context pack smoke coverage。
- version conflict 与 validation error coverage。
- backend validation command。
