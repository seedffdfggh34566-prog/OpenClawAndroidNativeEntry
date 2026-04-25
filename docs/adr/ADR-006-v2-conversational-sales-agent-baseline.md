# 决策记录：V2 Conversational Sales Agent Baseline

- 文档路径建议：`docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`
- 文档状态：Approved planning baseline v0.1
- 决策日期：2026-04-25
- 关联文档：
  - `docs/product/overview.md`
  - `docs/product/prd/ai_sales_assistant_v2_prd.md`
  - `docs/architecture/data/v2-sales-agent-data-model.md`
  - `docs/architecture/data/v2-lead-research-data-model.md`
  - `docs/adr/ADR-005-v2-lead-research-scope-and-search-boundary.md`
  - `docs/delivery/tasks/task_v2_conversational_sales_agent_definition_update.md`

---

## 1. 决策目的

本文档用于冻结 V2 planning baseline 的方向调整：V2 从“轻量线索研究工具”调整为“对话式专属销售 agent prototype”。

本文档只冻结规划边界，不冻结数据库 schema、API contract、runtime implementation 或 Android UI。

---

## 2. 最终决策

### 2.1 V2 产品形态

V2 当前产品形态调整为：

> **对话式专属销售 agent prototype。**

轻量线索研究不再是 V2.1 的唯一核心，而是 V2.2 阶段的 agent 能力。

### 2.2 阶段拆分

V2 规划拆分为：

```text
V2.1 Conversational Sales Agent Prototype
    对话式产品理解 + 获客方向分析 + 用户实时调整方向

V2.2 Evidence-based Lead Research
    确认方向后联网搜索，生成有来源证据的候选公司

V2.3 Persistent Sales Agent Workspace
    长期记忆、历史研究复用、候选状态管理，再讨论 MVP
```

### 2.3 V2.1 数据沉淀

V2.1 首批应持久化：

- `SalesAgentSession`
- `ConversationMessage`
- `ProductProfileRevision`
- `LeadDirectionVersion` 或等价结构化方向版本
- `AgentRun(run_type = sales_agent_turn)`

`ConversationMessage` 不再后置。对话消息是专属销售 agent 的输入轨迹和复盘依据，但不是正式业务主真相。

### 2.4 Prototype 存储路线

V2.1 先做 prototype。

当前继续采用：

- 本地后端沉淀正式对象。
- SQLite 可作为 prototype 存储基线。
- schema 设计必须按未来可迁云设计。

当前不切换到正式云端部署，不引入多用户、租户隔离或权限系统。

### 2.5 Runtime 方向

V2 继续沿用 LangGraph 作为当前默认 runtime 编排方向。

V2.1 建议新增：

```text
sales_agent_turn_graph
```

LangGraph 的职责：

- 读取会话上下文。
- 判断用户意图。
- 生成追问、回答、产品画像更新草稿或方向调整草稿。
- 返回 typed draft payload。

LangGraph 不得：

- 直接写正式数据库对象。
- 把 checkpoint 当成业务记忆主存。
- 绕过 backend services 决定正式对象状态。

### 2.6 Lead research 后置

联网搜索、具体公司候选、来源证据和联系方式进入 V2.2。

ADR-005 仍然有效，但作为 V2.2 的搜索 / 来源证据 / 联系方式边界。

---

## 3. 原因

用户目标已经从“生成一次获客分析结果”升级为“拥有一个专属销售 agent”。

若继续以 lead research 为第一实现项，会过早进入搜索 provider、联系方式和来源质量问题，而没有先验证核心交互：

- 用户是否愿意通过对话补充销售上下文。
- agent 是否能主动追问。
- 用户是否能实时调整获客方向。
- 系统是否能把这些调整结构化沉淀。

因此 V2.1 应先验证对话式销售分析 agent，再进入 V2.2 lead research。

---

## 4. 后果

### 正向后果

- V2 与通用 LLM 客户端的区别更清晰：持续会话、结构化记忆、方向版本和业务对象沉淀。
- 后端数据模型能优先支持专属 agent，而不是一次性报告。
- 搜索和联系方式风险被后置，不阻塞 V2.1 prototype。

### 代价

- V2 首批对象从 lead research 对象转向 session/message/direction。
- Android 后续需要最小 chat-first 入口。
- Backend contract 需要支持 `sales_agent_turn`。
- V2.2 lead research 实现顺序后移。

---

## 5. 后续必须单独冻结

进入实现前，还需要单独冻结：

- `SalesAgentSession` API contract。
- `ConversationMessage` schema。
- `LeadDirectionVersion` 是否独立建表。
- `sales_agent_turn_graph` draft payload schema。
- 是否首批持久化 `AgentContextPack`。
- V2.1 backend-only prototype task。
