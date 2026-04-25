# V1 领域对象与状态基线

更新时间：2026-04-24

## 1. 文档定位

本文档用于冻结 **AI 销售助手 V1** 的正式领域对象与最小状态基线。

它服务于以下后续工作：

- 信息架构定义
- Android 控制壳层重构
- 后端 API contract 拆分
- Agent runtime 输出收口

本文档不是：

- 数据库 schema 文档
- ORM 设计文档
- 完整 API 设计文档
- CRM 扩展规划

关联文档：

- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/architecture/system-context.md`
- `docs/adr/ADR-001-backend-deployment-baseline.md`
- `docs/delivery/tasks/task_v1_domain_model_baseline.md`

---

## 2. 当前结论

V1 当前只冻结 4 个正式业务对象：

1. `ProductProfile`
2. `LeadAnalysisResult`
3. `AnalysisReport`
4. `AgentRun`

这些对象共同覆盖 V1 的最小闭环：

```text
产品学习
    ↓
ProductProfile
    ↓
LeadAnalysisResult
    ↓
AnalysisReport
```

同时由 `AgentRun` 记录正式执行过程。

以下内容当前不是 V1 正式业务对象：

- 聊天会话
- 会话消息
- 临时追问列表
- tool 原始调用日志
- `Lead`
- `LeadResearchSnapshot`
- 完整 CRM 类对象
- 独立 product learning run 正式对象

如需在 V1 中出现上述信息，应将其视为交互通道、运行态上下文或未来扩展，而不是当前必须冻结的正式对象。

---

## 3. 正式对象、运行态与交互通道边界

### 3.1 正式对象

正式对象由产品后端负责校验、归档、赋予状态与版本，并作为后续页面、接口和历史记录的权威来源。

V1 正式对象只有：

- `ProductProfile`
- `LeadAnalysisResult`
- `AnalysisReport`
- `AgentRun`

### 3.2 Runtime 中间输出

Runtime 可以输出结构化草稿形态与中间结果，例如：

- `ProductProfileDraft`
- `LeadAnalysisResultDraft`
- `AnalysisReportDraft`
- 缺失字段列表
- 置信度
- 证据引用

这里的 `Draft` 表示“正式对象在写回前或待确认阶段的草稿形态”，不是新的正式业务对象类型。

### 3.3 交互通道

聊天会话、消息、上传材料、临时追问和状态提示属于交互或输入通道。

它们可以影响正式对象，但不能直接替代正式对象成为长期业务真相。

---

## 4. 最小关系模型

### 4.1 对象关系

- 一个 `ProductProfile` 可以关联多份 `LeadAnalysisResult`
- 一份 `LeadAnalysisResult` 可以关联多份 `AnalysisReport`
- 一个 `AgentRun` 通过 `input_refs` 和 `output_refs` 关联上述正式对象

关系可用下面的最小模型理解：

```text
ProductProfile 1 --- N LeadAnalysisResult 1 --- N AnalysisReport
       ^
       |
       +---------------- AgentRun (by input_refs / output_refs)
```

### 4.2 版本原则

V1 默认允许保留历史版本，但只需要明确：

- 可以存在历史版本
- 同类对象在同一工作上下文下应有一个“当前有效版本”
- 不在本任务中设计完整版本控制系统

---

## 5. 最小状态流转

### 5.1 `ProductProfile`

```text
draft → confirmed → superseded
```

- `draft`：系统已形成结构化草稿，但仍允许补充、确认或修订
- `confirmed`：已被用户确认，可作为正式分析输入
- `superseded`：已被更新版本替代，但仍保留历史引用价值

约束：

- 只有 `confirmed` 状态可作为正式分析输入
- `ready_for_confirmation` 通过 `learning_stage` 表达，而不是进入 `status`

### 5.2 `LeadAnalysisResult`

```text
draft → published → superseded
```

- `draft`：runtime 已输出分析草稿，后端尚未完成最终发布
- `published`：已成为用户可查看、可复用的正式分析结果
- `superseded`：已被更新结果替代

约束：

- 失败、重试、取消不写入该对象状态，统一由 `AgentRun` 承担

### 5.3 `AnalysisReport`

```text
draft → published → superseded
```

- `draft`：报告草稿已生成，但尚未作为正式输出发布
- `published`：可被查看、导出、复用
- `superseded`：已被更新报告替代

### 5.4 `AgentRun`

```text
queued → running → succeeded | failed | cancelled
```

- `queued`：任务已被创建，等待 runtime 执行
- `running`：任务执行中
- `succeeded`：本次执行成功产出结构化结果
- `failed`：本次执行失败，需查看错误或重试
- `cancelled`：任务被主动取消或中止

约束：

- `AgentRun` 负责记录执行过程，不承担正式业务真相
- product learning 执行继续复用 `AgentRun`
- create 阶段与 iteration 阶段的 product learning 都继续复用 `AgentRun`

---

## 6. 正式对象定义

## 6.1 `ProductProfile`

### 职责与权威边界

`ProductProfile` 是产品理解与后续分析的权威主档。

它负责沉淀：

- 产品是什么
- 卖给谁
- 在什么场景下使用
- 用户为什么购买
- 当前已知的销售线索和限制

它不能退化为聊天记录摘要，也不能被手机端本地草稿替代。

### 建议字段分组

- 标识与归属：`id`、`workspace_id`、`owner_id`
- 产品概述：`name`、`one_line_description`、`source_notes`、`category`
- 客户与场景：`target_customers`、`target_industries`、`typical_use_cases`
- 销售线索：`pain_points_solved`、`core_advantages`、`delivery_model`、`price_range`、`sales_region`、`constraints`
- 质量与版本：`status`、`learning_stage`、`confidence_score`、`version`
- 时间信息：`created_at`、`updated_at`

说明：

- `status` 表示正式对象生命周期
- `learning_stage` 表示 backend 派生的产品学习阶段表达

### 读取与产出

- 由产品学习流程产出
- 由用户确认与修订
- 由获客分析流程读取
- 可被报告生成流程引用

### 对象关系

- 被 `LeadAnalysisResult.product_profile_id` 引用
- 可被 `AgentRun.output_refs` 产出
- 可被后续 `AgentRun.input_refs` 再次读取

## 6.2 `LeadAnalysisResult`

### 职责与权威边界

`LeadAnalysisResult` 是基于已确认 `ProductProfile` 生成的结构化获客分析结果。

它负责沉淀：

- 推荐方向
- 优先级
- 排序理由
- 风险限制
- 下一步建议

它不是 CRM 线索库，也不是联系人主档。

### 建议字段分组

- 标识与输入引用：`id`、`product_profile_id`、`created_by_agent_run_id`
- 分析摘要：`analysis_scope`、`summary`
- 推荐方向：`priority_industries`、`priority_customer_types`、`scenario_opportunities`
- 排序理由：`ranking_explanations`、`recommendations`
- 风险限制：`risks`、`limitations`
- 版本与时间：`status`、`version`、`created_at`、`updated_at`

### 读取与产出

- 由获客分析流程产出
- 由报告生成流程读取
- 可被用户复看、替换或基于新版本重跑

### 对象关系

- 必须引用一个已确认的 `ProductProfile`
- 可被 `AnalysisReport.lead_analysis_result_id` 引用
- 可被 `AgentRun.output_refs` 产出

## 6.3 `AnalysisReport`

### 职责与权威边界

`AnalysisReport` 是面向用户复看、复用和导出的正式报告对象。

它负责把前序对象整理成更适合阅读和传播的结果交付，而不是简单拼接聊天内容。

### 建议字段分组

- 标识与谱系：`id`、`product_profile_id`、`lead_analysis_result_id`
- 报告摘要：`title`、`summary`
- 正文结构：`body_markdown`、`sections`
- 导出/展示信息：`export_status`、`export_refs`
- 版本与时间：`status`、`version`、`created_at`、`updated_at`

### 读取与产出

- 由报告生成流程产出
- 读取 `ProductProfile` 与 `LeadAnalysisResult`
- 供手机端查看、复制、导出和后续迭代

### 对象关系

- 必须引用一个 `ProductProfile`
- 必须引用一个 `LeadAnalysisResult`
- 可被 `AgentRun.output_refs` 产出

## 6.4 `AgentRun`

### 职责与权威边界

`AgentRun` 是一次正式执行过程的记录对象。

它负责沉淀：

- 是谁触发了运行
- 运行读取了哪些输入
- 运行产出了哪些对象
- 当前执行状态
- 错误摘要与时间信息

它不是业务主真相对象，也不替代正式分析结果。

### 建议字段分组

- 执行标识：`id`、`run_type`
- 触发来源：`triggered_by`、`trigger_source`
- 输入引用：`input_refs`
- 输出引用：`output_refs`
- 运行状态：`status`
- 错误与时序：`started_at`、`ended_at`、`error_message`
- runtime 元信息：`runtime_provider`、`runtime_metadata`

`runtime_metadata` 可包含 provider、graph、trace、prompt version、round index，以及 product learning / lead analysis LLM 成功路径的非敏感 token usage 统计。

### 读取与产出

- 由产品后端创建
- 由 runtime 更新执行进展
- 供状态页、审计、排障和历史回看使用

### 对象关系

- 通过 `input_refs` / `output_refs` 引用正式对象
- 不反向拥有正式对象生命周期

---

## 7. Runtime 写回边界

### 7.1 Runtime 负责什么

Runtime 负责：

- 基于输入对象和材料执行分析
- 生成结构化草稿形态
- 返回缺失字段、置信度、证据引用和错误信息

### 7.2 产品后端负责什么

产品后端负责：

- 校验 runtime 输出
- 将输出写回正式对象
- 赋予对象状态与版本
- 决定对象是否发布为用户可见结果

### 7.3 不允许发生的事情

当前不允许：

- 把聊天会话直接当成正式业务对象
- 让 runtime 越过产品后端直接写正式主对象
- 把 `AgentRun` 状态机混进 `ProductProfile`、`LeadAnalysisResult`、`AnalysisReport`
- 为了“未来 CRM”提前引入过重对象体系

---

## 8. 本次基线的范围外说明

以下内容明确不在本次基线中冻结：

- `Lead`
- `LeadResearchSnapshot`
- 联系方式抓取对象
- 联系人库
- 外呼或自动触达对象
- 完整数据库表结构
- API 字段类型与序列化细节

如后续确实需要上述对象，应在新的 spec 或 task 中单独定义，并显式说明与本基线的关系。

---

## 9. 后续引用建议

后续任务如涉及以下主题，应优先引用本文档：

- 首页、流程页、结果页、报告页的信息架构
- Android 端查看/确认/重跑的对象入口
- 后端 API 的对象读写边界
- Agent runtime 输出 contract 的收口方式

后续实现默认基于本文档的对象边界与最小状态流转推进，除非新的 decision 或 task 显式覆盖。
