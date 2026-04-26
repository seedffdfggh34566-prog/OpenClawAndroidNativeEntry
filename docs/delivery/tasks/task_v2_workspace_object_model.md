# Task：V2 workspace object model

更新时间：2026-04-26

## 1. 任务定位

- 任务名称：V2 workspace object model
- 建议路径：`docs/delivery/tasks/task_v2_workspace_object_model.md`
- 当前状态：`done`
- 优先级：P0

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 上游任务：`task_v2_sales_workspace_direction_update.md`
- 建议下游任务：
  1. `task_v2_sales_workspace_kernel_architecture.md`
  2. `task_v2_markdown_projection_and_context_pack.md`
  3. `task_v2_workspace_kernel_backend_only_prototype.md`

停止条件：

- 需要进入后端 ORM / Alembic migration
- 需要实现 API
- 需要实现 Android UI
- 需要接入真实搜索 provider
- 需要实现 LangGraph runtime graph
- 需要冻结联系方式策略

---

## 2. 任务目标

完成 V2 Sales Workspace 的对象模型草案，明确 `SalesWorkspace` 作为 V2 根对象，并定义多轮客户挖掘、来源证据、候选评分、排序榜单、用户反馈、workspace patch 和 context pack 所需的核心对象。

本任务只更新架构文档、task 和 handoff，不实现后端、Android、数据库 migration、runtime graph、搜索 provider 或 API。

---

## 3. 背景

上一任务已将 V2 产品北极星升级为：

> **workspace-native sales agent prototype / 中小企业专属销售工作区 Agent。**

用户进一步明确，目标不是一次性报告，而是像软件工程 workspace 一样对信息进行分类沉淀：

- 产品侧信息
- 客户挖掘侧信息
- 来源证据
- 候选客户
- 候选评分与排序
- 用户反馈
- 多轮挖掘质量迭代

因此，需要先定义对象模型，避免继续把所有能力塞进 V1 的 `ProductProfile`、`LeadAnalysisResult`、`AnalysisReport` 和 `AgentRun`。

---

## 4. 范围

### In Scope

- 新增 `docs/architecture/workspace/workspace-object-model.md`。
- 明确 `SalesWorkspace` 是 V2 根对象。
- 明确现有 V1 对象在 V2 中的定位。
- 定义：
  - `WorkspaceCommit`
  - `WorkspacePatch`
  - `ProductProfileRevision`
  - `LeadDirectionVersion`
  - `ResearchRound`
  - `ResearchSource`
  - `CompanyCandidate`
  - `CandidateObservation`
  - `CandidateScoreSnapshot`
  - `CandidateRankingBoard`
  - `FeedbackEvent`
  - `ContextPack`
- 定义多轮挖掘后的排序更新流程。
- 定义第一批 backend-only prototype 的对象切片。
- 明确首批不做数据库 migration。

### Out of Scope

- 后端代码
- Android 代码
- 数据库 schema / migration
- runtime graph 实现
- 搜索 provider 接入
- API contract 实现
- Markdown projection 详细目录结构
- ContextPackCompiler 详细算法
- 联系方式策略细化

---

## 5. 产出要求

至少应产出：

1. `workspace-object-model.md` 明确 V2 对象分层。
2. `SalesWorkspace` 被定义为根对象。
3. `CompanyCandidate`、`CandidateObservation`、`CandidateScoreSnapshot`、`CandidateRankingBoard` 能支撑候选客户跨轮次排序。
4. `ResearchRound` 能支撑多轮客户挖掘实验。
5. `FeedbackEvent` 能支撑用户反馈反哺后续挖掘。
6. `WorkspacePatch` / `WorkspacePatchDraft` 边界明确：runtime 产出 draft，backend 校验并正式写回。
7. 明确报告是 projection / 发布视图，不是主存。
8. 明确首批 backend-only prototype 不直接建数据库 migration。

---

## 6. 验收标准

满足以下条件可认为完成：

1. 新增 `docs/architecture/workspace/workspace-object-model.md`。
2. 文档包含 V2 核心对象总览和对象分层。
3. 文档详细定义 `SalesWorkspace`。
4. 文档详细定义候选客户评分和排序对象。
5. 文档明确多轮 research round 的排序更新流程。
6. 文档明确 V1 对象在 V2 中的降级 / 复用关系。
7. 文档明确第一批 backend-only prototype 的对象集合。
8. 未修改 backend / Android 代码。

---

## 7. 实际产出

- 已新增 `docs/architecture/workspace/workspace-object-model.md`。
- 已新增本 task 文档。
- 已新增 handoff。
- 已更新 `_active.md`，记录本 task 完成并调整后续 docs task 队列。

---

## 8. 本次定稿边界

本次只冻结对象模型草案，不冻结：

- ORM
- migration
- API contract
- Android UI
- 搜索 provider
- LangGraph graph schema
- Markdown projection 反向解析规则
- ContextPackCompiler 具体实现
- 联系方式展示、保留、删除、脱敏策略

---

## 9. 推荐下一步

下一步建议创建并完成：

```text
docs/delivery/tasks/task_v2_sales_workspace_kernel_architecture.md
```

该任务应新增：

```text
docs/architecture/workspace/sales-workspace-kernel.md
```

并明确：

- Sales Workspace Kernel 的模块边界。
- structured store、Markdown projection、ContextPackCompiler、runtime adapter、backend services 的协作关系。
- `WorkspacePatchDraft -> WorkspacePatch -> WorkspaceCommit` 的写回裁决流程。
