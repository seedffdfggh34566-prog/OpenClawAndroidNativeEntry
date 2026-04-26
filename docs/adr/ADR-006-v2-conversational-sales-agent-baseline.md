# 决策记录：V2 Workspace-native Sales Agent Baseline

- 文档路径建议：`docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`
- 文档状态：Approved planning baseline v0.2
- 决策日期：2026-04-26
- 关联文档：
  - `docs/product/overview.md`
  - `docs/product/prd/ai_sales_assistant_v2_prd.md`
  - `docs/architecture/data/v2-sales-agent-data-model.md`
  - `docs/architecture/data/v2-lead-research-data-model.md`
  - `docs/adr/ADR-005-v2-lead-research-scope-and-search-boundary.md`
  - `docs/delivery/tasks/task_v2_sales_workspace_direction_update.md`

---

## 1. 决策目的

本文档用于更新 V2 planning baseline 的产品北极星：V2 从“对话式专属销售 agent prototype”进一步升级为“workspace-native sales agent prototype”。

本文档只冻结规划边界，不冻结数据库 schema、API contract、runtime implementation 或 Android UI。

---

## 2. 最终决策

### 2.1 V2 产品形态

V2 当前产品形态调整为：

> **中小企业专属销售工作区 Agent：用户只管聊天和反馈，agent 负责理解产品、沉淀信息、研究候选客户、维护优先级，并持续提升获客质量。**

这意味着：

- chat-first 是入口，不是全部产品。
- Sales Workspace 是长期资产容器。
- structured cards 是用户确认和管理 workspace state 的方式。
- evidence-based lead research 是 V2.2 的 agent 能力。
- candidate ranking board 是客户挖掘结果的核心承载之一。
- report 是发布 / 复盘 / 导出视图，不是唯一结果载体。

### 2.2 阶段拆分

V2 规划拆分为：

```text
V2.1 Sales Workspace Kernel Prototype
    chat-first 入口 + 产品理解 + 获客方向 + workspace patch + context pack + Markdown projection

V2.2 Evidence-based Research Round
    确认方向后联网搜索，生成来源证据、候选客户、观察事实、评分快照和 ranking delta

V2.3 Persistent Sales Workspace MVP Gate
    长期记忆、历史研究复用、候选状态管理、用户反馈闭环，再讨论 MVP
```

### 2.3 V2.1 数据沉淀

V2.1 首批应围绕 Sales Workspace Kernel，而不是单纯围绕聊天会话。

首批建议持久化或定义原型对象：

- `SalesWorkspace`
- `ConversationMessage`
- `ProductProfileRevision`
- `LeadDirectionVersion`
- `CandidateRankingBoard` 的最小雏形
- `WorkspacePatch` / `WorkspacePatchDraft`
- `ContextPack`
- `AgentRun(run_type = sales_agent_turn)`

`ConversationMessage` 不再后置。对话消息是专属销售 agent 的输入轨迹和复盘依据，但不是正式业务主真相。

Markdown 可以作为 agent-readable workspace projection，但不能成为唯一主存。正式对象必须以后端结构化对象为主真相。

### 2.4 V1 资产定位

V1 不再决定 V2 产品主路径。

V1 对象在 V2 中的定位：

- `ProductProfile`：可继续作为产品主档或 current projection，但不代表完整 sales workspace。
- `LeadAnalysisResult`：可继续作为方向分析结果，但不承载客户候选库和排序历史。
- `AnalysisReport`：作为发布 / 复盘 / 导出视图，不作为客户挖掘主存。
- `AgentRun`：继续记录执行过程、输入输出谱系和 runtime metadata。

### 2.5 Prototype 存储路线

V2.1 先做 prototype。

当前建议：

- 第一阶段优先做 backend-only Sales Workspace Kernel prototype。
- 可以先用 Pydantic schema + JSON fixture / file-backed store + Markdown projection 验证对象关系。
- 对象关系稳定后再进入 SQLite / Alembic migration。
- schema 设计必须按未来可迁云设计。

当前不切换到正式云端部署，不引入多用户、租户隔离或权限系统。

### 2.6 Runtime 方向

V2 可以继续沿用 LangGraph 作为当前默认 runtime 编排方向，但 LangGraph 不是产品主架构。

V2 主架构应是：

```text
Sales Workspace Kernel
    -> ContextPack Compiler
    -> Agent Runtime / LangGraph
    -> WorkspacePatchDraft
    -> Backend validation / writeback
    -> Structured objects + Markdown projection
```

V2.1 建议新增或调整：

```text
sales_agent_turn_graph
```

LangGraph 的职责：

- 读取 workspace context pack，而不是直接读取全部历史聊天。
- 判断用户意图。
- 生成追问、回答、产品画像更新草稿、方向调整草稿或 workspace patch draft。
- 返回 typed draft payload。

LangGraph 不得：

- 直接写正式数据库对象。
- 把 checkpoint 当成业务记忆主存。
- 绕过 backend services / workspace kernel 决定正式对象状态。

### 2.7 Lead research 后置但升级为 research round

联网搜索、具体公司候选、来源证据和联系方式进入 V2.2。

ADR-005 仍然有效，但作为 V2.2 的搜索 / 来源证据 / 联系方式边界。

V2.2 不应只生成一次性 `LeadResearchResult`，而应形成可追踪的 `ResearchRound`，并更新候选观察、候选评分和 `CandidateRankingBoard`。

---

## 3. 原因

用户目标已经从“生成一次获客分析结果”升级为“拥有一个专属销售工作区 agent”。

若继续以 conversational sales agent 为唯一北极星，系统容易退化成：

- 聊天机器人
- 获客方向分析器
- 一次性报告生成器
- lead research 工具

这些都不足以支撑用户真正想要的长期价值：

- 产品侧信息持续沉淀。
- 客户挖掘侧信息持续沉淀。
- 多轮研究后候选客户优先级可更新。
- 用户反馈能反哺下一轮研究。
- agent 不依赖单次 LLM 上下文，而是通过 workspace state 和 context pack 工作。

因此，V2 的北极星应升级为 workspace-native sales agent。

---

## 4. 后果

### 正向后果

- V2 与通用 LLM 客户端的区别更清晰：长期 workspace、结构化记忆、方向版本、证据账本、候选排序和反馈闭环。
- V2 与传统 CRM 的区别更清晰：不先做复杂客户管理，而是先做客户挖掘和销售思考的 agent workspace。
- 后端数据模型能优先支持 sales workspace，而不是一次性报告。
- 搜索和联系方式风险继续后置，不阻塞 V2.1 workspace kernel prototype。
- 后续如果切换 runtime framework，Sales Workspace Kernel 仍可保持稳定。

### 代价

- V2 首批对象从 session/message/direction 进一步升级为 workspace/kernel/patch/context/ranking。
- 原有 V2 sales agent data model 需要升级。
- Android 后续需要展示 workspace state，而不只是聊天消息。
- Backend contract 需要围绕 workspace endpoints 和 workspace patch 重新设计。
- V2.2 lead research 实现顺序后移，但会更清楚地服务于 research round 和 ranking board。

---

## 5. 后续必须单独冻结

进入实现前，还需要单独冻结：

- `SalesWorkspace` 对象模型。
- `WorkspacePatchDraft` schema。
- `ContextPack` schema 和 token budget 策略。
- Markdown projection 的目录结构、frontmatter 和同步规则。
- `CandidateRankingBoard` / `CandidateScoreSnapshot` 最小模型。
- `SalesAgentSession` 是否继续作为独立对象，还是并入 `SalesWorkspace` 关系。
- `sales_agent_turn_graph` draft payload schema。
- V2.1 backend-only Sales Workspace Kernel prototype task。
