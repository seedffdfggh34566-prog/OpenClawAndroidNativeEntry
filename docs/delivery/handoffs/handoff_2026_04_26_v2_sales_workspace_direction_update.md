# 阶段性交接：V2 sales workspace direction update

更新时间：2026-04-26

## 1. 本次改了什么

- 将 V2 产品北极星从“对话式专属销售 agent prototype”升级为“workspace-native sales agent prototype / 中小企业专属销售工作区 Agent”。
- 更新 V2 PRD 到 Draft v0.3。
- 更新 overview，明确 V1 是资产库，V2 主路径应从 Sales Workspace 重新定义。
- 更新 roadmap，近期顺序调整为先定义 workspace kernel、object model、Markdown projection 和 context pack compiler。
- 更新 ADR-006，从 conversational sales agent baseline 升级为 workspace-native sales agent baseline。
- 更新 `_active.md`，设置当前 task 和后续 docs task queue。
- 新增 `task_v2_sales_workspace_direction_update.md`。

---

## 2. 为什么这么定

用户进一步明确：

- 产品应像软件工程 workspace 一样对信息进行分类沉淀。
- 目标是避免被 LLM 单次上下文窗口限制。
- 客户挖掘应能多轮迭代，并在后续候选更优时更新 workspace 内部优先级。
- 报告只是结果展示之一，核心应是销售工作区、候选排序和反馈闭环。

因此，V2 不应继续只围绕“聊天会话 + 分析报告”展开，而应升级为 Sales Workspace Kernel 主线。

---

## 3. 本次验证了什么

本次为 docs-only 变更，未运行 backend / Android 测试。

已验证：

- 修改范围只包含产品 / ADR / roadmap / active task / handoff / task 文档。
- 未修改 backend 或 Android 代码。
- 新的路线仍保留 V1 资产复用和后端 formal truth layer 原则。

---

## 4. 已知限制

- 未定义 `SalesWorkspace` 正式 schema。
- 未定义 `WorkspacePatchDraft` schema。
- 未定义 `ContextPack` schema。
- 未定义 Markdown projection 目录结构。
- 未定义 `CandidateRankingBoard` 和 `CandidateScoreSnapshot` 的正式模型。
- 未创建 backend-only prototype task。
- 未实现任何代码。

---

## 5. 推荐下一步

1. 创建 `task_v2_sales_workspace_kernel_architecture.md`。
2. 新增 `docs/architecture/workspace/sales-workspace-kernel.md`。
3. 新增 `docs/architecture/workspace/workspace-object-model.md`。
4. 新增 `docs/architecture/workspace/markdown-projection.md`。
5. 新增 `docs/architecture/workspace/context-pack-compiler.md`。
6. 再创建 backend-only Sales Workspace Kernel prototype task。
