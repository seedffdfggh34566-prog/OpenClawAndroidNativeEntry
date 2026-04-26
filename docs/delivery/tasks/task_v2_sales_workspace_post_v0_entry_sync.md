# Task：V2 Sales Workspace post-v0 entry sync

更新时间：2026-04-27

## 1. 任务定位

- 任务名称：V2 Sales Workspace post-v0 entry sync
- 建议路径：`docs/delivery/tasks/task_v2_sales_workspace_post_v0_entry_sync.md`
- 当前状态：`done`
- 优先级：P0

---

## 2. 任务目标

将入口层从 “Sales Workspace Kernel backend-only v0 正在进行” 同步为 “backend-only v0 已完成，下一步先做 API contract 与 persistence decision”。

---

## 3. 范围

In Scope：

- 更新仓库根 README、docs 总入口、delivery 入口、product overview、roadmap。
- 创建 post-v0 handoff。
- 创建下一组正式 task queue。
- 更新 `_active.md`，只开放 API contract 与 persistence decision。

Out of Scope：

- 修改代码。
- 修改 PRD / ADR 正文语义。
- 实现 FastAPI route、DB migration、Android UI、Runtime / LangGraph、LLM 或 search。

---

## 4. 验收标准

- 入口层明确 `Sales Workspace Kernel backend-only v0 已完成`。
- `_active.md` current task 指向 `task_v2_sales_workspace_api_contract_v0.md`。
- `_active.md` next queued task 只列 `task_v2_sales_workspace_persistence_decision.md`。
- 后续 implementation task 只为 `planned`，不可自动执行。
- `git diff --check` 通过。

---

## 5. 实际产出

- 已同步入口层。
- 已新增 post-v0 handoff。
- 已新增 V2.1 后续 task queue。

---

## 6. 已做验证

已执行：

```bash
rg "Sales Workspace Kernel backend-only v0 已完成" README.md docs/README.md docs/delivery/README.md docs/product/overview.md docs/product/roadmap.md
rg "task_v2_sales_workspace_api_contract_v0.md|task_v2_sales_workspace_persistence_decision.md" README.md docs/README.md docs/delivery/README.md docs/delivery/tasks/_active.md
git diff --check
git status --short
```

结果：

- 入口层包含 `Sales Workspace Kernel backend-only v0 已完成`。
- 入口层包含 API contract 与 persistence decision 两个当前队列任务。
- `git diff --check` passed。
- `git status --short` 仅包含本次 Markdown 文档变更。
