# 项目总览（当前阶段）

更新时间：2026-04-28

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
- V2.1 workspace/kernel engineering baseline 已验证 Sales Workspace Kernel、Draft Review ID flow、Postgres / Alembic persistence chain 与 Draft Review audit persistence。
- V2.1 chat-first deterministic demo flow、backend-level 5-sample conversational acceptance 和 Tencent TokenHub LLM runtime prototype 已形成 validated prototype path：contract examples、trace persistence、backend prototype、Android chat-first UI、demo runbook、PRD Traceability、clarifying questions、workspace explanation、product extraction、lead direction adjustment、backend e2e 和 explicit-flag LLM runtime eval 均已补齐；这不等于完整 V2.1 product milestone 已关闭。
- V2.2 再进入证据化 ResearchRound、候选客户、来源证据和候选优先级榜更新。
- V2.3 作为 Persistent Sales Workspace MVP gate，验证长期记忆、历史研究复用、候选状态管理和用户反馈闭环是否值得进入 MVP。

当前 V2 草案入口：

- `docs/product/prd/ai_sales_assistant_v2_prd.md`
- `docs/architecture/data/v2-sales-agent-data-model.md`
- `docs/architecture/data/v2-lead-research-data-model.md`
- `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`
- `docs/adr/ADR-005-v2-lead-research-scope-and-search-boundary.md`

当前 V2 workspace 架构入口：

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

> **V2.1 validated prototype path completed；V2.1 product milestone remains open under planning control。**

当前阶段状态的权威入口为：

- `docs/product/project_status.md`
- `docs/product/research/v2_1_completion_semantics_correction_2026_04_28.md`

已经明确：

- V1 已冻结，不继续追加 V1 功能。
- V1 是资产库，不是 V2 产品主路径。
- V2 北极星是 Sales Workspace，而不是一次性报告生成器。
- V2.1 workspace/kernel engineering baseline 已完成 Sales Workspace Kernel、FastAPI prototype、Android Draft Review ID flow、Postgres / Alembic persistence chain、Sales Workspace Postgres store 和 Draft Review audit persistence。
- V2.1 chat-first Runtime design、contract examples、trace persistence、backend prototype、Android chat-first UI、demo runbook、backend acceptance、Android polish、真机端到端验收、PRD Acceptance final review 和 Tencent TokenHub LLM runtime prototype 已验证 prototype path；V2.1 product milestone 仍可由规划层继续开放 continuation package。
- V2.2 允许主动联网 / 中文公开网页搜索。
- V2.2 可以产出具体公司候选，但候选必须带来源证据和排序解释。
- V2 不做 Web 前端。
- V2 不做自动触达或联系人抓取产品。
- 后端仍是 formal truth layer。

尚未冻结或仍需后续规划：

- V2 是否作为 MVP。
- 是否需要正式云部署。
- 是否需要账号、多用户、租户隔离和权限。
- V2.2 evidence/search/contact 的边界与实现顺序。
- 搜索 provider。
- 数据保留策略。
- 个人联系方式展示和删除策略。
- production-grade V2 domain/schema baseline。
- production-grade V2 backend API contract。
- V2.2 research/search task queue。

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

V2 继续实现前，应先确保当前 package / task 已在 `_active.md` 中开放。V2.1 validated prototype path 已完成，但 V2.1 product milestone 仍开放于规划控制下；后续不应直接进入正式 LangGraph implementation、search 或 Android 扩展，除非规划层先开放对应 task。

---

## 10. 推荐下一步

当前推荐顺序：

1. 承认 V2.1 workspace/kernel engineering baseline completed。
2. 承认 V2.1 validated prototype path completed，但不把它升级为完整 V2.1 product milestone completed。
3. 当前项目状态以 `docs/product/project_status.md` 为准，task / handoff 只作为 evidence。
4. 后续可由规划层开放 V2.1 continuation package，例如 demo reproducibility、Android onboarding、LLM prompt quality、trace/history visibility 或 Postgres verification。
5. V2.2 implementation 前，不直接接正式 LangGraph、联网搜索、ContactPoint 或 CRM/contact。

当前不建议直接实现正式 LangGraph graph、搜索 provider、Android UI 扩展或 CRM/contact。

---

## 11. 一句话总结

当前项目已经从 V1 demo baseline 转入：

> **AI 销售助手 V2.1 validated prototype path completed；V2.1 product milestone remains open under planning control；不直接进入真实搜索、ContactPoint 或 formal LangGraph implementation。**
