# 项目总览（当前阶段）

更新时间：2026-04-26

## 1. 文档定位

本文档用于说明本仓库的当前主线、当前阶段、当前范围、当前系统分层与当前工作方式，供人工和 AI Dev Agent 快速接手。

本文档只记录当前已经明确的共识。后续如产品方向、版本范围、系统分层、部署基线或工作方式发生变化，应优先更新本文件。

---

## 2. 当前项目是什么

当前项目已经不再以早期 OpenClaw Android Native Entry / 原生控制入口实验为主要目标。

当前项目主线为：

> **AI 销售助手 App**

V1 已正式收口为 demo-ready release candidate / learning milestone。当前阶段进入：

> **V2 planning baseline：定义 workspace-native sales agent prototype、销售工作区内核、后续证据化客户挖掘能力和 contract。**

当前不是 V1 继续开发阶段，也不是 V2 MVP 实现阶段。

---

## 3. V1 已完成基线

V1 已验证以下主闭环：

```text
产品学习 -> 产品画像确认 -> LeadAnalysis LLM -> 结构化报告 -> Android 真机复看
```

V1 可复用资产包括：

- `ProductProfile`
- `LeadAnalysisResult`
- `AnalysisReport`
- `AgentRun`
- ProductLearning LLM draft 生成经验
- LeadAnalysis LLM draft 生成经验
- TokenHub provider 接入经验
- runtime metadata 与 token usage 观测
- Developer LLM Run Inspector
- Android 控制入口和真机 demo 路径
- 真实中文业务样例库和 eval 记录

V1 不进入 MVP，原因见：

- `docs/product/research/v1_closeout_2026_04_25.md`

V1 对 V2 的定位：

- V1 是资产库和参考实现，不再决定 V2 产品主路径。
- V1 的正式对象可以复用，但不应把 V2 强行扩展成“产品学习 + 获客分析 + 报告”的线性流程。
- V2 的主路径应从 `SalesWorkspace` 和客户挖掘迭代闭环重新定义。

---

## 4. 当前 V2 北极星

V2 当前北极星为：

> **中小企业专属销售工作区 Agent：用户只管聊天和反馈，agent 负责理解产品、沉淀信息、研究候选客户、维护优先级，并持续提升获客质量。**

V2 当前规划重点：

- V2 的核心形态是 **Sales Workspace**，不是一次性报告生成器。
- chat-first 是入口，structured cards 是可视化确认方式，workspace state 是长期资产。
- 产品侧信息、获客方向、客户挖掘、来源证据、候选排序、用户反馈和报告输出应像软件工程 workspace 一样分层沉淀。
- 结构化后端对象是主真相；Markdown 是 agent-readable workspace projection，不是唯一主存。
- Product Sales Agent / Runtime 每次运行应尽量生成 `WorkspacePatchDraft`，由后端 workspace kernel 裁决正式写回。
- V2.1 先验证 Sales Workspace Kernel 和 chat-first workspace 入口。
- V2.2 再进入证据化 ResearchRound、候选客户、来源证据和候选优先级榜更新。
- V2.3 作为 Persistent Sales Workspace MVP gate，验证长期记忆、历史研究复用、候选状态管理和用户反馈闭环是否值得进入 MVP。

当前 V2 草案入口：

- `docs/product/prd/ai_sales_assistant_v2_prd.md`
- `docs/architecture/data/v2-sales-agent-data-model.md`
- `docs/architecture/data/v2-lead-research-data-model.md`
- `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`
- `docs/adr/ADR-005-v2-lead-research-scope-and-search-boundary.md`

后续应新增的 V2 workspace 架构入口：

- `docs/architecture/workspace/sales-workspace-kernel.md`
- `docs/architecture/workspace/workspace-object-model.md`
- `docs/architecture/workspace/markdown-projection.md`
- `docs/architecture/workspace/context-pack-compiler.md`

---

## 5. 当前明确不做

当前阶段不做：

- Web 前端
- 完整 CRM
- 自动邮件 / 短信 / 企微 / 电话触达
- 自动外呼
- 批量联系人抓取
- 批量联系人导出
- 大规模爬虫系统
- 企业级团队协作审批流
- 正式商业化计费系统
- 未经任务排定的后端 schema / migration / API 实现
- 未经任务排定的 Android 大改

---

## 6. 当前系统路线

当前继续沿用 V1 已验证的系统路线，但 V2 主架构应升级为 Sales Workspace Kernel：

```text
Android / client
    -> FastAPI API
    -> Sales Workspace Kernel / backend services
    -> Structured Store + Markdown Projection + ContextPack Compiler
    -> backend/runtime/ Runtime execution layer
    -> WorkspacePatchDraft
    -> backend validation / writeback
    -> formal workspace objects
```

含义：

- Android 端不是权威主存，只负责控制入口、状态查看、任务发起、结果查看和轻量编辑。
- 正式后端负责业务对象主存、任务执行编排、结果沉淀与后续协作能力预留。
- Sales Workspace Kernel 是 V2 的产品主干，负责 workspace 对象、patch、context pack、ranking board 和 Markdown projection。
- 当前默认 runtime 方向仍为 `backend/runtime/` 内的 LangGraph direct orchestration，但 LangGraph 不是产品主架构。
- Runtime / Product Sales Agent execution layer 只产出 draft payload、工具执行结果和 `WorkspacePatchDraft`，不直接写正式业务对象。
- Backend services / workspace kernel 负责正式对象写回和业务边界裁决。
- 本地部署是当前工程基线，不代表长期耦合到本地路径或单机脚本。

---

## 7. 当前阶段

当前处于：

> **V2 planning baseline 阶段，但产品北极星已从 conversational sales agent 升级为 workspace-native sales agent。**

已经明确：

- V1 已冻结，不继续追加 V1 功能。
- V1 是资产库，不是 V2 产品主路径。
- V2 北极星是 Sales Workspace，而不是一次性报告生成器。
- V2.1 先做 Sales Workspace Kernel、chat-first 入口、产品理解、获客方向、context pack 和 Markdown projection。
- V2.2 允许主动联网 / 中文公开网页搜索。
- V2.2 可以产出具体公司候选，但候选必须带来源证据和排序解释。
- V2 不做 Web 前端。
- V2 不做自动触达或联系人抓取产品。
- 后端仍是 formal truth layer。

尚未冻结：

- V2 是否作为 MVP。
- 是否需要正式云部署。
- 是否需要账号、多用户、租户隔离和权限。
- `SalesWorkspace` schema。
- `WorkspacePatchDraft` schema。
- `ContextPack` schema。
- Markdown projection 目录结构和同步规则。
- `CandidateRankingBoard` / `CandidateScoreSnapshot` 最小模型。
- 搜索 provider。
- 数据保留策略。
- 个人联系方式展示和删除策略。
- V2 domain/schema baseline。
- V2 backend API contract。
- V2 task queue。

---

## 8. 当前文档体系

当前 `docs/` 目录继续作为唯一正式文档入口：

- `product/`：产品方向、PRD、研究与路线图
- `architecture/`：系统分层、仓库结构与 backend / runtime / data / clients / workspace 方案
- `reference/`：API contract、领域模型与其他权威参考
- `how-to/`：运行、运维、协作和排障手册
- `adr/`：关键架构与部署决策
- `delivery/`：任务与交接文档
- `archive/`：历史资料归档

历史 OpenClaw 相关文档只作参考，不作为当前产品主线。V2 可以吸收 OpenClaw 的 Markdown workspace / agent memory 思想，但必须以销售场景结构化对象和 workspace kernel 作为产品主干。

---

## 9. 当前工作原则

### 原则 1：先定义，再实现

V2 方向变化、workspace 内核、搜索边界、数据模型、API contract 或运行规则变化应先进入 docs / ADR / task，再进入代码。

### 原则 2：workspace 是北极星

V2 不应退化成聊天机器人、报告生成器或一次性 lead research 工具。所有关键能力都应服务于长期 sales workspace。

### 原则 3：结构化对象是主真相

Markdown 可以作为 agent-readable projection，但正式业务对象必须沉淀为后端结构化对象。

### 原则 4：先证据，再候选

V2.2 线索研究中，无来源候选不能进入正式结果。

### 原则 5：候选排序必须可解释

候选客户优先级不能只存在于报告正文中，应由候选对象、观察事实、评分快照和 ranking board 支撑。

### 原则 6：联系方式保守处理

公司联系方式和个人联系方式必须分开建模。联系方式必须有来源，默认人工验证，不自动触达。

### 原则 7：后端是主真相

Android 是控制入口，runtime 是执行层，backend services / workspace kernel 是正式对象写回裁决层。

### 原则 8：小步任务化

V2 进入实现前，应先冻结 workspace kernel 架构、对象模型、Markdown projection、context pack compiler 和 backend-only prototype task。

---

## 10. 推荐下一步

当前推荐顺序：

1. 完成 V2 产品北极星更新。
2. 新增 Sales Workspace Kernel 架构文档。
3. 新增 workspace object model 文档。
4. 新增 Markdown projection 文档。
5. 新增 ContextPack Compiler 文档。
6. 创建 V2.1 backend-only Sales Workspace Kernel prototype task。
7. 先实现 Pydantic schema、ranking engine、Markdown projection 和 context pack compiler 的无 DB 原型。
8. 原型跑通后，再决定 SQLite migration、API 和 Android 最小接入。

当前不建议直接实现后端 schema、API、搜索 provider 或 Android UI。

---

## 11. 一句话总结

当前项目已经从 V1 demo baseline 转入：

> **AI 销售助手 V2 planning baseline：以 workspace-native sales agent 为北极星，先定义并验证 Sales Workspace Kernel，再进入证据化客户挖掘、候选排序和长期销售工作区。**
