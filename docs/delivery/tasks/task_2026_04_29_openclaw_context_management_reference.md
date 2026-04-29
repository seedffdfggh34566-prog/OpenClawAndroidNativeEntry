# Task: OpenClaw Context Management Reference

更新时间：2026-04-29

## 1. Task Positioning

- 任务名称：OpenClaw Context Management Reference
- 当前状态：`done`
- 任务类型：`docs`
- Authorization source：human instruction on 2026-04-29，要求下载并分析 upstream OpenClaw 上下文管理系统，并形成项目 docs 文档。
- 完成后是否允许自动进入下游任务：`no`

## 2. Objective

形成一份项目内架构参考文档，说明：

- upstream OpenClaw context management 的核心模块和机制。
- 本项目 V2 Sales Workspace / Product Sales Agent 可借鉴的上下文管理方案。
- 本项目不能照搬或自动实现的边界。
- 后续如需实现，应拆成什么样的独立任务。

## 3. Scope

In scope：

- 只读分析 `/tmp/openclaw-reference`。
- 新增 runtime 架构参考文档。
- 更新 runtime / architecture navigation。
- 记录 handoff。
- 运行轻量文档验证。

Out of scope：

- 修改 backend / Android 源码。
- 新增 DB schema、migration、API contract 或 runtime lifecycle。
- 引入 LangGraph durable checkpoint、MCP、ContextEngine plugin registry。
- 实现 V2.2 evidence/search/contact、CRM 或自动触达。
- 读取或输出 backend secrets。
- 修改 `_active.md` 自动执行队列。

## 4. Files

- `docs/architecture/runtime/openclaw-context-management-reference.md`
- `docs/architecture/runtime/README.md`
- `docs/architecture/README.md`
- `docs/delivery/tasks/task_2026_04_29_openclaw_context_management_reference.md`
- `docs/delivery/handoffs/handoff_2026_04_29_openclaw_context_management_reference.md`

## 5. Execution Outcome

状态：`done`。

完成内容：

- 新增 OpenClaw context management reference and borrowing plan。
- 将 upstream context、system prompt、session transcript、context engine、pruning、compaction 拆解为本项目可借鉴方案。
- 提出 `SalesWorkspaceContextPipeline`、`context_budget_report`、deterministic recent message fitting 和 future summary artifact 的分阶段路线。
- 明确不改变 backend/runtime truth-layer 边界，不自动引入 LangGraph、MCP、V2.2 search/contact。
- 更新 runtime / architecture navigation。
- 新增 handoff。

## 6. Validation

- `git diff --check` passed。
- `rg -n "[ \\t]$" ...` found no trailing whitespace in touched docs。

## 7. Known Limits

- 本任务只形成方案文档，不实现 ContextPack budget diagnostics。
- `/tmp/openclaw-reference` 在本仓库 Git 工作树外，不会被当前项目提交。
- 后续实现必须另建 dedicated task，建议任务名为 `V2.1 Sales Workspace ContextPack Budget Diagnostics`。

## 8. Handoff

Detailed handoff：`docs/delivery/handoffs/handoff_2026_04_29_openclaw_context_management_reference.md`。
