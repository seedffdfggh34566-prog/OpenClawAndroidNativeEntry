# 阶段性交接：V2 workspace object model

更新时间：2026-04-26

## 1. 本次改了什么

- 新增 `docs/architecture/workspace/workspace-object-model.md`。
- 将 `SalesWorkspace` 定义为 V2 workspace-native sales agent 的根对象。
- 定义 V2 Sales Workspace 对象分层：
  - Workspace Layer
  - Product Layer
  - Direction Layer
  - Research Layer
  - Evidence Layer
  - Candidate Layer
  - Interaction Layer
- 定义多轮客户挖掘所需对象：
  - `ResearchRound`
  - `ResearchSource`
  - `CompanyCandidate`
  - `CandidateObservation`
  - `CandidateScoreSnapshot`
  - `CandidateRankingBoard`
  - `FeedbackEvent`
- 定义 `WorkspacePatch` / `WorkspacePatchDraft` 的写回边界。
- 定义 `ContextPack` 作为 context compiler 输出快照。
- 明确 `AnalysisReport` 在 V2 中是发布视图，不是 workspace 主存。
- 明确 `ProductProfile`、`LeadAnalysisResult`、`AnalysisReport`、`AgentRun` 可复用，但不足以支撑 V2 workspace-native sales agent。
- 新增本 task 文档。
- 更新 `_active.md`。

---

## 2. 为什么这么定

用户明确希望 V2 像软件工程 workspace 一样分类沉淀信息：

- 产品侧信息
- 客户挖掘侧信息
- 来源证据
- 候选客户
- 候选优先级
- 多轮研究结果
- 用户反馈

这样做的目标是避免 LLM 上下文窗口限制，并持续提升客户挖掘质量。

因此，不能继续把 V2 建在 V1 的线性对象链路上：

```text
ProductProfile -> LeadAnalysisResult -> AnalysisReport
```

V2 需要一个新的根对象和对象图：

```text
SalesWorkspace -> ResearchRound -> CompanyCandidate -> CandidateScoreSnapshot -> CandidateRankingBoard
```

---

## 3. 本次验证了什么

本次是 docs-only 更新。

已完成的人工检查：

- 对象模型是否覆盖多轮挖掘、候选评分、排序榜单、反馈闭环。
- 是否避免直接进入 ORM / migration。
- 是否明确 V1 对象复用而非继续作为产品主路径。
- 是否为后续 backend-only prototype 提供对象集合。

未运行 backend / Android 测试。

---

## 4. 已知限制

- 未定义 `sales-workspace-kernel.md` 的模块架构。
- 未定义 Markdown projection 的目录结构和反向解析规则。
- 未定义 ContextPackCompiler 的具体算法。
- 未定义 API contract。
- 未实现 backend schema / migration。
- 未实现任何 Python code。
- 未实现 LangGraph graph。
- 未接入搜索 provider。
- 未定义联系方式展示、删除、脱敏策略。

---

## 5. 推荐下一步

下一步建议创建：

```text
docs/delivery/tasks/task_v2_sales_workspace_kernel_architecture.md
```

并新增：

```text
docs/architecture/workspace/sales-workspace-kernel.md
```

重点回答：

1. Sales Workspace Kernel 放在哪一层。
2. 它如何连接 structured store、Markdown projection、ContextPackCompiler 和 runtime。
3. `WorkspacePatchDraft` 如何被 backend services 校验并写回。
4. 哪些能力属于 kernel，哪些属于 LangGraph runtime。
5. backend-only prototype 第一版应该如何落地。
