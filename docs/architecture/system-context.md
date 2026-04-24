# Agent Runtime 与数据架构说明

更新时间：2026-04-24

## 1. 文档定位

本文档用于说明当前 **AI 销售助手 App V1** 的系统分层、运行时边界、数据权威模型、对象模型、Agent 组织方式，以及第一阶段部署基线。

本文档回答的问题包括：

- OpenClaw 在系统中扮演什么角色
- 本地服务器、手机端、产品后端分别负责什么
- 正式业务对象存在哪里
- Agent 如何读写业务对象
- 当前为什么采用“本地服务器承载正式后端 + 手机端仅作控制入口 + 架构按未来可迁云设计”的路线
- 后续若迁移到云端，哪些部分应该保持不变

本文档不是：

- 市场研究文档
- 产品 PRD
- 任务文档
- 运行手册

它属于 `docs/architecture/`，用于把当前已经明确的方向进一步落成可指导后续 task 与实现的技术方案说明。

关联文档：

- `docs/reference/schemas/v1-domain-model-baseline.md`

---

## 2. 当前架构结论

当前项目正式采用以下路线：

> **本地服务器承载正式后端 + 手机端仅作控制入口 + 架构按未来可迁云设计**

同时明确以下系统边界：

1. **手机安卓端不是权威主存**，只承担控制入口、状态入口、结果查看与轻量编辑能力。
2. **本地服务器/电脑承载第一阶段正式后端**，负责正式业务对象、任务编排、结果沉淀与服务接口。
3. **当前默认 runtime 为 `backend/runtime/` 内的 LangGraph direct orchestration**，负责执行编排、结构化 draft 生成与运行时上下文，不直接等于产品本体。
4. **产品系统本身负责业务对象、状态管理、结果归档与后续协作扩展**，不把聊天会话直接视为业务真相。
5. **架构从第一阶段开始按未来可迁云设计**，不允许为了当前本地部署而把业务逻辑耦合到本地文件路径、手工脚本或设备特定实现。

---

## 3. 为什么当前采用这条路线

### 3.1 与当前产品阶段匹配

当前项目主线已经收口为：

- 产品学习
- 获客分析
- 结构化输出 / 报告

当前重点不是立即扩展到联系方式获取、自动触达或完整 CRM，而是先把最小可验证闭环做对。

在这个阶段，采用本地服务器承载正式后端，具备以下优势：

- 迭代快，便于围绕对象模型与 Agent 流程反复调整
- 可直接复用现有 `jianglab` 主机能力
- 成本低于立即做正式云端产品部署
- 更容易先把产品层与 runtime 层的边界分清
- 便于在不做手机端主存的前提下形成统一后端真相

### 3.2 与当前工程条件匹配

当前唯一权威工作区已明确为：

```text
jianglab:/home/yulin/projects/OpenClawAndroidNativeEntry
```

并且当前项目已经建立了：

- 唯一工作区
- 远程 Codex 工作流
- 文档骨架
- AI 销售助手 V1 主线

因此，第一阶段把正式后端部署在本地服务器/电脑上，是当前工程条件下最自然的选择。

### 3.3 与后续迁云目标兼容

当前选择本地服务器，并不意味着系统逻辑只能本地运行。

当前路线的本质是：

- **部署先本地**
- **接口先服务化**
- **对象先结构化**
- **边界先分层**
- **未来可迁云**

也就是说，当前决定的是**部署基线**，而不是把系统永久锁死在本地环境。

---

## 4. 系统总体分层

当前建议系统分为四层：

```text
手机端（控制入口）
    ↓
产品层后端（正式业务系统）
    ↓
Runtime Execution Layer（当前默认：backend/runtime + LangGraph）
    ↓
数据层（结构化主存 / 文件存储 / 向量检索 / 日志）
```

### 4.1 手机端（控制入口层）

主要职责：

- 登录与身份进入
- 发起产品学习
- 查看当前任务状态
- 查看 / 确认产品画像
- 查看分析结果与报告
- 做轻量编辑与重新触发
- 缓存最近工作集与已读结果

明确不承担：

- 权威主数据库
- 正式对象主真相
- 主 Agent 执行宿主
- 团队协作裁决点
- 正式文件主存

### 4.2 产品层后端（正式业务系统）

这是当前产品真正的核心层，负责：

- `ProductProfile` 等正式业务对象管理
- 任务状态管理
- 分析结果归档
- 报告归档与导出
- 用户/团队/权限预留
- 统一 API 提供
- 审计与运行记录预留
- 调度 runtime execution layer 执行任务

### 4.3 Runtime Execution Layer（当前默认：LangGraph）

当前默认 runtime 执行层扮演：

- graph-based execution orchestration
- 结构化 draft payload 生成
- 运行时上下文承载层
- 受控模型与工具调用入口

当前默认 runtime 不扮演：

- 产品业务数据库
- 正式权限系统
- 最终业务主档存储
- 正式对象写回裁决层
- 最终产品 UI

### 4.4 数据层

数据层用于承载：

- 正式结构化业务对象
- 原始文件与材料
- 检索索引
- 运行日志与事件

数据层属于产品系统，而不是手机端或单个 agent 的私有状态。

---

## 5. 各层职责详细说明

## 5.1 手机端职责

手机端是“控制入口”，而不是“宿主本体”。

### 手机端应负责

- 引导用户进入首页
- 发起产品学习
- 录入或上传产品材料
- 查看生成中的任务状态
- 审核 `ProductProfile` 的 draft 形态
- 发起获客分析
- 查看 `LeadAnalysisResult`
- 查看 `AnalysisReport`
- 查看最近任务与历史结果
- 发起重跑、确认、导出等轻量操作

### 手机端可负责

- 本地缓存最近项目
- 本地缓存最近报告
- 本地缓存临时草稿
- 本地缓存会话状态
- 离线查看部分已同步内容

### 手机端不应负责

- 正式业务对象主存
- 中心化对象裁决
- 正式团队同步裁决
- 长期运行 Agent 执行主进程
- 直接操作数据库主表

---

## 5.2 本地服务器/电脑职责

本地服务器/电脑是第一阶段正式后端的部署位置。

推荐由 `jianglab` 承载第一阶段正式后端。

### 本地服务器应负责

- 启动正式产品后端服务
- 承载正式数据库
- 承载对象存储或本地文件主目录
- 承载当前默认 runtime execution layer
- 接收手机端发起的请求
- 执行产品学习 / 获客分析 / 报告生成任务
- 统一归档结果对象
- 记录运行日志

### 本地服务器可负责

- 本地缓存 embedding / 向量索引
- 本地执行文档解析
- 本地执行 API 聚合与清洗
- 本地运行后台任务调度器

### 本地服务器不应负责

- 直接把 UI 逻辑与服务逻辑混在一起
- 以手工脚本取代正式 API
- 让 agent 直接改动任意本地 markdown 作为业务真相

---

## 5.3 Runtime Execution Layer 职责

### Runtime 应负责

- 统一执行 Agent 回合
- 管理模型调用或其他受控生成逻辑
- 调用工具
- 调用外部数据源
- 生成中间分析结果
- 返回结构化输出
- 提供 runtime 级运行日志

### Runtime 不应负责

- 直接定义 `ProductProfile` 的权威 schema
- 直接决定业务对象生命周期
- 直接保存客户主档为最终真相
- 直接作为产品 API 层

### 当前建议定位

> **Runtime = execution substrate，backend = formal truth layer**

不是产品本体，不是数据库，不是唯一状态系统。

---

## 5.4 产品系统职责

产品系统是当前项目真正要构建的“销售场景 AI 原生产品层”。

它负责：

- 业务对象建模
- 业务状态管理
- 结果沉淀
- 统一 API 暴露
- 与 runtime 解耦
- 后续权限、协作、审计扩展

这层应该独立于 OpenClaw runtime，哪怕当前 runtime 由 OpenClaw 承载。

---

## 6. 权威数据模型

## 6.1 核心原则

当前采用以下数据原则：

1. **权威主存不在手机端**
2. **正式业务对象以后端为准**
3. **本地缓存允许存在，但不能成为双主**
4. **聊天记录不是正式业务真相**
5. **Agent 输出必须沉淀为正式对象或正式对象草稿**

---

## 6.2 正式业务对象

V1 核心正式业务对象以 [v1_domain_model_baseline.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/reference/schemas/v1-domain-model-baseline.md) 为准。

当前冻结的 4 个正式对象为：

- `ProductProfile`
- `LeadAnalysisResult`
- `AnalysisReport`
- `AgentRun`

这些对象承担正式业务真相与正式执行记录。

此外，当前架构层允许保留少量支持性数据概念，例如 `SourceArtifact`，用于承载原始材料元数据，但它不属于本任务冻结的 V1 核心正式对象。

像 `Lead`、`LeadResearchSnapshot` 这类研究型或 CRM 延展对象，当前不在 V1 核心对象基线中冻结。如后续确有需要，应在新的 spec / task 中单独定义。

---

## 6.3 正式对象与会话的关系

当前必须明确：

- 聊天会话只是**交互通道**
- `ProductProfile` 等对象才是**正式业务真相**
- 会话中的有效信息应被提炼并写入对象
- 不能把“以后去翻会话记录”当作长期主存策略

---

## 7. 数据层分层设计

当前建议采用 **结构化主存 + 文件存储 + 检索索引 + 运行日志** 的分层方式。

## 7.1 结构化主存

作用：

- 存储正式业务对象
- 存储状态与引用关系
- 存储对象版本
- 存储任务状态

第一阶段可采用：

- PostgreSQL
- 或 MVP 期临时使用 SQLite（仅在明确不影响接口设计时）

但无论底层选型如何，接口层都应按正式服务化对象设计。

## 7.2 文件存储

作用：

- 存放上传文档
- 存放解析产物
- 存放网页快照
- 存放导出报告
- 存放大文本材料

第一阶段可先使用本地服务器文件系统中的受控目录；后续可替换为对象存储。

## 7.3 检索索引层

作用：

- 支持原始材料召回
- 支持报告与资料片段引用
- 支持产品学习阶段的语义检索

第一阶段可以采用：

- pgvector
- FAISS
- 或其他简化方案

但必须明确：

> 检索索引不是权威主存，只是辅助召回层。

## 7.4 运行日志层

作用：

- 记录 agent 执行轨迹
- 记录工具调用
- 记录错误
- 记录中间对象引用
- 支持回溯与调试

第一阶段可先用数据库表 + 文本日志文件并存。

---

## 8. Agent 组织方式

当前建议 V1 采用：

- 1 个 orchestrator
- 3 个主 agent

## 8.1 `orchestrator_agent`

职责：

- 决定当前应触发哪个 agent
- 维护流程状态
- 管理失败重试
- 保证流程不跳步
- 统一产出任务状态

不负责深度内容生成。

## 8.2 `product_learning_agent`

职责：

- 通过对话与材料抽取产品信息
- 识别缺失字段
- 生成 `ProductProfileDraft` 草稿形态
- 提示需要补充的问题

输入：

- 用户回答
- 上传资料
- 历史 profile
- 原始材料片段

输出：

- `ProductProfileDraft` 草稿形态
- 缺失字段列表
- 置信度
- 建议追问

## 8.3 `lead_analysis_agent`

职责：

- 基于 `ProductProfile` 做行业与客户方向分析
- 形成候选 lead 方向
- 输出排序与推荐理由

输入：

- 已确认 `ProductProfile`
- 外部企业数据
- 搜索结果
- 历史模板

输出：

- `LeadAnalysisResultDraft` 草稿形态
- 候选 lead 清单
- 排序理由
- 风险与限制

## 8.4 `report_generation_agent`

职责：

- 将分析结果整理为面向用户的正式报告

输入：

- `ProductProfile`
- `LeadAnalysisResult`
- `SourceEvidence`

输出：

- `AnalysisReportDraft` 草稿形态
- 摘要版
- 详细版

---

## 9. Agent 文件架构建议

当前建议在仓库中把 Agent 定义与业务数据严格分开。

## 9.1 Agent 定义文件

这些文件属于**规则层**，建议放在：

```text
docs/agents/
```

建议结构：

```text
docs/
  agents/
    README.md
    orchestrator/
      agent.md
      state_machine.md
      output_contract.md
    product_learning/
      agent.md
      interview_strategy.md
      extraction_schema.md
      memory_rules.md
    lead_analysis/
      agent.md
      analysis_framework.md
      ranking_rules.md
      tool_contracts.md
    report_generation/
      agent.md
      report_template.md
      output_schema.md
```

这些文件负责定义：

- agent 是谁
- 负责什么
- 输入是什么
- 输出是什么
- 允许调用哪些工具
- 不该做什么
- 成功标准是什么

## 9.2 Schema 文件

这些文件属于**对象模型层**，建议单独放在：

```text
schemas/
```

建议结构：

```text
schemas/
  product_profile.schema.json
  source_artifact.schema.json
  lead_analysis_result.schema.json
  analysis_report.schema.json
  agent_run.schema.json
```

如果后续要引入 `Lead` 或 `LeadResearchSnapshot`，应在新的领域对象 spec 中单独补充，而不是默认视为当前 V1 已冻结对象。

## 9.3 业务数据

业务数据不应存放在 `docs/agents/` 中，也不应让 agent 直接把 markdown 文档当主数据库。

正式业务对象应存于后端正式数据层。

---

## 10. 调用与读写边界

当前建议采用以下边界：

## 10.1 手机端 → 产品后端

手机端通过正式 API 调用：

- 创建产品学习任务
- 获取当前产品画像
- 提交确认
- 创建获客分析任务
- 获取分析结果
- 获取报告
- 获取任务状态

## 10.2 产品后端 → Runtime Execution Layer

产品后端调用 runtime：

- 发起 agent run
- 提供输入对象引用
- 获取结构化结果
- 写回正式对象

当前默认实现方向为：

- `backend/runtime/` 内直接接入 LangGraph
- 不经由额外 OpenClaw 中间执行壳
- 正式对象写回仍由 backend services 协调

## 10.3 Runtime Execution Layer → 数据与工具

runtime 只通过受控方式：

- 读取对象数据
- 读取材料
- 调用外部 API
- 调用搜索与解析工具
- 返回结构化输出

runtime 不应直接越过产品层随意写正式主对象。

---

## 11. 当前主流程

## 11.1 产品学习流程

```text
手机端发起产品学习
    ↓
产品后端创建一次 product learning agent run
    ↓
Runtime execution layer 执行 product_learning_agent
    ↓
生成 ProductProfileDraft 草稿形态
    ↓
后端校验并写回 `ProductProfile` 的 `draft` 状态
    ↓
手机端展示草稿并请求用户确认
    ↓
用户确认后升级为正式 ProductProfile

产品学习阶段当前至少区分：

- `collecting`
- `ready_for_confirmation`
- `confirmed`

当前是否独立冻结 `ProductLearningRun`，仍留给后续 follow-up task 决定。
```

## 11.2 获客分析流程

```text
手机端发起获客分析
    ↓
产品后端读取已确认 ProductProfile
    ↓
Runtime execution layer 执行 lead_analysis_agent
    ↓
生成 LeadAnalysisResultDraft 草稿形态
    ↓
后端校验并写回 `LeadAnalysisResult` 的 `draft` 状态
    ↓
手机端查看结果并可触发继续生成报告
```

## 11.3 报告生成流程

```text
手机端请求生成报告
    ↓
产品后端读取 ProductProfile + LeadAnalysisResult
    ↓
Runtime execution layer 执行 report_generation_agent
    ↓
生成 AnalysisReportDraft 草稿形态
    ↓
后端校验并写回 `AnalysisReport` 的 `draft` 状态
    ↓
手机端展示 / 导出
```

---

## 12. 本地部署与未来迁云边界

当前采用本地服务器承载正式后端，但必须从第一阶段开始遵守以下迁云前提：

## 12.1 不变的部分

未来迁云时，以下内容应尽量保持不变：

- 核心业务对象模型
- API 语义
- agent contract
- 手机端页面逻辑
- runtime execution layer 的角色定位
- 任务状态模型

## 12.2 可替换的部分

未来迁云时，以下内容允许替换：

- 数据库部署位置
- 文件存储位置
- 向量索引部署位置
- runtime 部署位置
- 网络入口与鉴权方式

## 12.3 当前必须避免的耦合

必须避免：

- 直接依赖本地绝对文件路径作为业务契约
- 把本地 markdown 当正式主数据库
- 让手机端直接依赖某台主机的内部实现
- 让 agent 直接读写任意宿主文件作为正式真相

---

## 13. 非目标与当前明确不做

当前阶段不做：

- 手机端权威主存
- 复杂双主同步
- 完整 CRM 对象体系
- 完整自动触达系统
- 大而全多租户企业后台
- 一开始就同时维护本地部署版与正式云端版两套产品逻辑

当前阶段也不要求：

- 立刻完成正式云端上线
- 立刻完成复杂权限矩阵
- 立刻完成复杂离线编辑冲突解决

---

## 14. 后续文档与任务建议

基于当前 spec，后续建议继续补齐：

### 1）Decision 文档

建议新增：

```text
docs/adr/ADR-001-backend-deployment-baseline.md
```

用于记录：

- 为什么当前采用本地服务器承载正式后端
- 为什么手机端不做主存
- 为什么 runtime 只作为 execution layer
- 为什么架构要按未来可迁云设计

### 2）Task 文档

后续正式 task 可按以下顺序展开：

1. `ProductProfile` schema 与服务定义
2. `AgentRun` 状态模型与任务接口
3. 产品学习流程接口与草稿确认机制
4. 获客分析结果对象与报告对象定义
5. 手机端首页 / 状态页 / 产品画像确认页骨架

### 3）Agent 文档

建议在 `docs/agents/` 目录中进一步定义：

- orchestrator_agent
- product_learning_agent
- lead_analysis_agent
- report_generation_agent

---

## 15. 一句话总结

当前系统的正式技术基线是：

> **手机端作为控制入口，本地服务器承载正式后端，`backend/runtime/` 内的 LangGraph 作为当前默认 runtime 执行层，业务对象以后端为权威真相，并从第一阶段开始按未来可迁云设计。**
