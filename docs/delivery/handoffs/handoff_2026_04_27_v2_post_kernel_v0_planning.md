# Handoff：V2 post-kernel-v0 planning sync

- 日期：2026-04-27
- 状态：done
- 对应任务：`docs/delivery/tasks/task_v2_sales_workspace_post_v0_entry_sync.md`

---

## 1. 本次变更

同步了 post-kernel-v0 文档入口和后续任务队列：

- 入口层明确 `Sales Workspace Kernel backend-only v0 已完成`。
- V2.1 后续顺序冻结为 API contract -> persistence decision -> backend API -> Android read-only -> Runtime integration。
- `_active.md` current task 更新为 `task_v2_sales_workspace_api_contract_v0.md`。
- `_active.md` next queued task 只列 `task_v2_sales_workspace_persistence_decision.md`。
- 新增 planned-only implementation tasks，避免 Dev Agent 自动跳入 API、Android 或 Runtime 实现。

---

## 2. 未开放范围

本次没有开放以下实现：

- FastAPI endpoint。
- SQLAlchemy ORM / Alembic migration / SQLite schema change。
- Android UI。
- Runtime / LangGraph integration。
- LLM / search provider。
- CRM / ContactPoint / 自动触达。

---

## 3. 后续队列

当前允许自动推进：

1. `task_v2_sales_workspace_api_contract_v0.md`
2. `task_v2_sales_workspace_persistence_decision.md`

以下任务只是 planned，不可自动执行：

- `task_v2_sales_workspace_backend_api_v0.md`
- `task_v2_android_workspace_readonly_view.md`
- `task_v2_sales_workspace_runtime_patchdraft_integration.md`

---

## 4. 验证

已执行：

```bash
rg "Sales Workspace Kernel backend-only v0 已完成" README.md docs/README.md docs/delivery/README.md docs/product/overview.md docs/product/roadmap.md
rg "task_v2_sales_workspace_api_contract_v0.md|task_v2_sales_workspace_persistence_decision.md" README.md docs/README.md docs/delivery/README.md docs/delivery/tasks/_active.md
git diff --check
git status --short
```

结果：

- 入口层包含 `Sales Workspace Kernel backend-only v0 已完成`。
- 入口层包含 `task_v2_sales_workspace_api_contract_v0.md` 与 `task_v2_sales_workspace_persistence_decision.md`。
- `git diff --check` passed。
- `git status --short` 仅包含本次 Markdown 文档变更。

---

## 5. 建议下一步

执行 `task_v2_sales_workspace_api_contract_v0.md`，先定义 contract，不实现 route。
