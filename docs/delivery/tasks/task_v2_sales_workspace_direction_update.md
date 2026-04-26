# Task：V2 sales workspace direction update

更新时间：2026-04-26

## 1. 任务定位

- 任务名称：V2 sales workspace direction update
- 建议路径：`docs/delivery/tasks/task_v2_sales_workspace_direction_update.md`
- 当前状态：`done`
- 优先级：P0

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：
  1. `task_v2_sales_workspace_kernel_architecture.md`
  2. `task_v2_workspace_object_model.md`
  3. `task_v2_markdown_projection_and_context_pack.md`
  4. `task_v2_workspace_kernel_backend_only_prototype.md`
- 停止条件：
  - 需要进入后端 / Android / 数据库实现
  - 需要冻结 V2 API contract
  - 需要选择搜索 provider
  - 需要决定个人联系方式保留、删除、脱敏或合规策略
  - 需要实现 runtime graph

---

## 2. 任务目标

将 V2 产品北极星从：

> **对话式专属销售 agent prototype**

升级为：

> **workspace-native sales agent prototype / 中小企业专属销售工作区 Agent**

本任务只更新产品方向、路线图、ADR、当前执行入口和 handoff，不实现后端、Android、数据库 migration、runtime graph、搜索 provider 或 API。

---

## 3. 背景

用户进一步明确：

- 产品不应只是聊天、分析报告或 lead research 工具。
- 产品应像软件工程 workspace 一样，对产品侧信息、客户挖掘侧信息、来源证据、候选排序和用户反馈进行分类沉淀。
- 这样做的目标是避免被 LLM 上下文窗口限制，并持续迭代客户挖掘能力和质量。
- 多轮挖掘后，如果后续候选客户比之前更具可行性，系统应能在用户账号 / workspace 内部更新候选优先级排序。
- 最终结果可以通过获客报告、候选卡片或人工验证建议展示，但报告不是唯一结果载体。

因此，V2 应从“对话式销售 agent”进一步升级为“workspace-native sales agent”。

---

## 4. 范围

### In Scope

- 更新 V2 PRD 到 Draft v0.3。
- 更新 product overview，明确 Sales Workspace 是 V2 北极星。
- 更新 roadmap，调整近期推荐顺序。
- 更新 ADR-006，从 conversational sales agent baseline 升级为 workspace-native sales agent baseline。
- 更新 `_active.md`，设置当前 task 和后续 docs task queue。
- 新增本 task 文档。
- 新增 handoff。

### Out of Scope

- 后端代码
- Android 代码
- 数据库 schema / migration
- runtime graph 实现
- 搜索 provider 接入
- API contract 实现
- MVP 定义
- 联系方式策略细化

---

## 5. 产出要求

至少应产出：

1. V2 PRD 明确 V2 北极星是 Sales Workspace，而不是一次性报告生成器。
2. V2 PRD 明确 V1 是资产库，不再决定 V2 产品主路径。
3. V2 PRD 明确 `SalesWorkspace`、`WorkspacePatch`、`ContextPack`、`CandidateRankingBoard` 是后续核心方向。
4. ADR-006 明确 LangGraph 可以继续作为 runtime 编排层，但不是产品主架构。
5. roadmap 明确后续优先做 workspace kernel architecture、object model、Markdown projection、context pack compiler。
6. `_active.md` 明确当前仍不允许直接实现后端 schema / migration / API / Android UI。

---

## 6. 验收标准

满足以下条件可认为完成：

1. `ai_sales_assistant_v2_prd.md` 更新为 Draft v0.3，并出现 workspace-native sales agent 北极星。
2. `overview.md` 的当前 V2 方向更新为 Sales Workspace。
3. `roadmap.md` 的近期推荐顺序从 backend contract 优先调整为 workspace kernel docs 优先。
4. ADR-006 更新为 workspace-native sales agent baseline。
5. `_active.md` 设置当前 task，并列出后续 docs task queue。
6. 不修改 backend / Android 代码。
7. 文档能直接指导下一步创建 workspace kernel architecture task。

---

## 7. 实际产出

- 已更新 `docs/product/prd/ai_sales_assistant_v2_prd.md` 到 Draft v0.3。
- 已更新 `docs/product/overview.md`。
- 已更新 `docs/product/roadmap.md`。
- 已更新 `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`。
- 已更新 `docs/delivery/tasks/_active.md`。
- 已新增本 task 文档。
- 已新增 handoff。

---

## 8. 本次定稿边界

本次只冻结 V2 产品北极星，不冻结：

- `SalesWorkspace` 正式 schema
- `WorkspacePatchDraft` schema
- `ContextPack` schema
- Markdown projection 目录结构
- `CandidateRankingBoard` 数据模型
- V2 API contract
- V2 implementation queue
- 搜索 provider
- 联系方式策略

---

## 9. 推荐下一步

下一步应创建：

```text
docs/delivery/tasks/task_v2_sales_workspace_kernel_architecture.md
```

该任务应新增：

```text
docs/architecture/workspace/sales-workspace-kernel.md
docs/architecture/workspace/workspace-object-model.md
docs/architecture/workspace/markdown-projection.md
docs/architecture/workspace/context-pack-compiler.md
```

并明确：

- Sales Workspace Kernel 分层。
- 结构化对象与 Markdown projection 的同步边界。
- `WorkspacePatchDraft` 如何从 runtime draft 进入后端写回裁决。
- `ContextPackCompiler` 如何避免每轮 agent 读取全部历史。
- `CandidateRankingBoard` 如何承载多轮客户挖掘后的优先级变化。
