# Task：V2 Sales Workspace Runtime WorkspacePatchDraft integration

更新时间：2026-04-27

## 1. 任务定位

- 任务名称：V2 Sales Workspace Runtime WorkspacePatchDraft integration
- 建议路径：`docs/delivery/tasks/task_v2_sales_workspace_runtime_patchdraft_integration.md`
- 当前状态：`planned`
- 优先级：P1

---

## 2. 任务目标

在 API、写回边界和 persistence 决策稳定后，让 Runtime / LangGraph 只产出 `WorkspacePatchDraft`，并由 Sales Workspace Kernel 校验后写入正式对象。

---

## 3. Blocked By

- `task_v2_sales_workspace_api_contract_v0.md`
- `task_v2_sales_workspace_persistence_decision.md`
- `task_v2_sales_workspace_backend_api_v0.md`

---

## 4. Out of Scope Until Unblocked

- LangGraph graph implementation。
- 真实 LLM。
- 联网搜索。
- Runtime 直接写正式 workspace 对象。
- Runtime 直接编辑 generated Markdown。

---

## 5. 验收方向

正式开放后至少应包含：

- `WorkspacePatchDraft` schema / boundary。
- Runtime draft -> backend validation -> WorkspacePatch 的测试。
- 明确 failure handling 和 human review boundary。
