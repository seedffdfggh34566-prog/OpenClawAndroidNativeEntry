# Task：V2 Sales Workspace Kernel backend API contract v0

更新时间：2026-04-27

## 1. 任务定位

- 任务名称：V2 Sales Workspace Kernel backend API contract v0
- 建议路径：`docs/delivery/tasks/task_v2_sales_workspace_api_contract_v0.md`
- 当前状态：`done`
- 优先级：P0

---

## 2. 任务目标

定义 Sales Workspace Kernel backend API contract v0，为后续 FastAPI implementation 提供稳定边界。

本任务只定义 contract，不实现 route。

---

## 3. In Scope

- 定义 workspace read API。
- 定义 WorkspacePatch apply API。
- 定义 ranking board、Markdown projection、ContextPack 的读取边界。
- 定义 `base_workspace_version` 冲突语义。
- 定义错误响应、最小 request / response shape、validation expectations。
- 明确 API 与 `backend/sales_workspace` Pydantic objects 的关系。

---

## 4. Out of Scope

- FastAPI route implementation。
- SQLAlchemy ORM / Alembic migration / SQLite schema change。
- Android UI。
- Runtime / LangGraph integration。
- LLM / search provider。
- CRM / ContactPoint / 自动触达。

---

## 5. 产出要求

至少产出：

1. 一份 API contract 文档，建议放在 `docs/reference/api/`。
2. 当前 task 状态更新。
3. handoff，记录 contract 决策和未实现范围。

---

## 6. 验收标准

- contract 能覆盖 backend-only v0 已实现闭环。
- contract 明确 read / patch / projection / context pack 边界。
- contract 明确 version conflict、validation error、not found 的语义。
- contract 不要求 DB、Android、Runtime 或 LLM/search。
- `git diff --check` 通过。

---

## 7. 下一步衔接

本任务完成后，继续：

1. `task_v2_sales_workspace_persistence_decision.md`
2. 完成 persistence decision 后，才允许开放 `task_v2_sales_workspace_backend_api_v0.md`

---

## 8. 实际产出

- 新增 `docs/reference/api/sales-workspace-kernel-v0-contract.md`。
- 更新 `docs/reference/README.md`。
- 更新 `_active.md`，将 current task 切到 `task_v2_sales_workspace_persistence_decision.md`。
- 新增 handoff：`docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_api_contract_v0.md`。

---

## 9. 已做验证

已执行：

```bash
rg "sales-workspace-kernel-v0-contract.md" docs/reference docs/delivery docs/README.md
rg "POST /sales-workspaces|WorkspacePatch|workspace_version_conflict|ContextPack" docs/reference/api/sales-workspace-kernel-v0-contract.md
rg "FastAPI route implementation|Alembic migration|Android UI|Runtime / LangGraph integration" docs/delivery/tasks/task_v2_sales_workspace_api_contract_v0.md docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_api_contract_v0.md
git diff --check
git status --short
```

结果：

- contract 文档已被 reference / delivery / docs 入口引用。
- contract 文档包含最小 endpoint、`WorkspacePatch`、`workspace_version_conflict`、`ContextPack`。
- task / handoff 明确 FastAPI route、Alembic migration、Android UI、Runtime / LangGraph integration 不在本任务范围。
- `git diff --check` passed。
- `git status --short` 仅包含本次 Markdown 文档变更。

---

## 10. 实际结果说明

本任务只冻结 API contract，不实现 FastAPI route，不改变 backend code，不引入 DB migration，不接 Android / Runtime / LLM / search。
