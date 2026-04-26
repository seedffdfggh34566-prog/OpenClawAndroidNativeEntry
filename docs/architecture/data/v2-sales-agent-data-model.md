# V2 Sales Agent Data Model

- 文档状态：Draft v0.1
- 更新日期：2026-04-25
- 阶段定位：V2 对话式专属销售 agent 数据模型草案，尚未冻结为数据库 schema 或 migration
- 关联文档：
  - `docs/product/prd/ai_sales_assistant_v2_prd.md`
  - `docs/architecture/data/v2-lead-research-data-model.md`
  - `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`

---

## 1. 文档目的

本文档定义 V2.1 对话式专属销售 agent prototype 所需的数据对象、对象边界和落地原则。

V2 方向已从单纯“轻量线索研究工具”调整为：

> **对话式专属销售 agent prototype。**

因此，V2 数据模型必须先支持：

1. 用户与 agent 的持续会话。
2. 每轮消息的可追溯记录。
3. 产品理解的结构化版本化。
4. 获客方向的对话式调整和版本化。
5. agent 回答、追问和正式对象变更之间的引用关系。

本文档不是：

- ORM 设计
- Alembic migration
- 完整 API contract
- 搜索 provider 选型
- CRM 数据模型

---

## 2. 设计原则

### 2.1 后端正式对象仍是主真相

V2 继续沿用 V1 架构边界：

- Android 是控制入口。
- 后端是正式业务系统。
- Runtime / agent 负责 draft、工具调用和中间推理。
- Backend services 负责正式对象写回。

### 2.2 对话必须持久化，但不是业务真相

`ConversationMessage` 是输入轨迹和交互历史。

它可以影响：

- `ProductProfileRevision`
- 获客方向版本
- `LeadAnalysisResult`
- 后续 `LeadResearchResult`

但它不能直接替代这些正式业务对象。

### 2.3 Agent memory 不能只存在 runtime 中

专属销售 agent 的长期记忆不能只存在：

- prompt
- Markdown 文件
- LangGraph checkpoint
- LLM provider session
- SDK session

可恢复、可解释、可迁移的记忆必须沉淀为结构化后端对象。

### 2.4 Markdown 是 projection，不是主存

Markdown 适合：

- agent-readable context
- report
- candidate card rendering
- debug / eval snapshot

Markdown 不适合做正式业务对象主存。

正式对象应以结构化数据库对象为主真相。

---

## 3. V2.1 首批建议对象

### 3.1 `SalesAgentSession`

职责：

- 表示用户与专属销售 agent 的一段持续会话。
- 连接消息、产品画像版本、获客方向版本和 AgentRun。

建议字段：

- `id`
- `product_profile_id`
- `current_product_profile_revision_id`
- `current_lead_direction_version_id`
- `status`
- `goal`
- `summary`
- `last_agent_run_id`
- `created_at`
- `updated_at`

建议状态：

```text
active -> archived
```

暂不建议引入复杂状态：

- `waiting_for_user`
- `paused`
- `resumed`

这些应留给后续 lifecycle task。

### 3.2 `ConversationMessage`

职责：

- 保存用户和 agent 的每轮消息。
- 支持复盘 agent 如何理解、追问、回答和更新对象。

建议字段：

- `id`
- `session_id`
- `role`
- `content`
- `message_type`
- `created_at`
- `agent_run_id`
- `linked_object_refs`

建议 `role`：

- `user`
- `assistant`
- `system`

建议 `message_type`：

- `user_input`
- `agent_question`
- `agent_answer`
- `product_update`
- `direction_update`
- `research_request`
- `research_summary`

边界：

- 消息内容可以被用于后续推理。
- 但后续正式分析必须引用结构化对象版本，而不是只引用消息文本。

### 3.3 `ProductProfileRevision`

职责：

- 保存 ProductProfile 的结构化快照。
- 让 agent 可以明确知道当前产品理解来自哪一版。

建议字段：

- `id`
- `product_profile_id`
- `version`
- `snapshot`
- `change_summary`
- `source_session_id`
- `source_message_ids`
- `created_by_agent_run_id`
- `created_at`

边界：

- `ProductProfile` 表示当前主档。
- `ProductProfileRevision` 表示可追溯历史版本。

### 3.4 `LeadDirectionVersion`

职责：

- 保存用户当前获客分析方向的结构化版本。
- 支持用户通过对话实时调整方向。

建议字段：

- `id`
- `session_id`
- `product_profile_revision_id`
- `version`
- `target_industries`
- `target_customer_types`
- `regions`
- `company_size`
- `priority_constraints`
- `excluded_industries`
- `excluded_customer_types`
- `reason_for_change`
- `source_message_ids`
- `created_by_agent_run_id`
- `created_at`

边界：

- 它不是候选公司列表。
- 它是后续 `LeadAnalysisResult` 或 `LeadResearchResult` 的方向输入。
- 如果首版不想新增独立表，可临时用 `LeadAnalysisResult.analysis_scope` 的结构化 JSON 替代，但不建议长期这么做。

### 3.5 `AgentContextPack`

职责：

- 保存某次 agent run 输入给模型的可复现上下文快照。

建议字段：

- `id`
- `agent_run_id`
- `session_id`
- `input_object_refs`
- `source_versions`
- `render_format`
- `rendered_markdown`
- `created_at`

边界：

- 它不是正式业务主真相。
- 它是运行复现、debug 和 eval 的输入快照。
- 首版可以暂缓持久化，但应在 contract 中保留概念。

### 3.6 `AgentRun`

继续作为运行记录。

V2.1 建议新增：

```text
run_type = sales_agent_turn
```

语义：

- 输入：SalesAgentSession、ConversationMessage、ProductProfileRevision、LeadDirectionVersion。
- 执行：识别意图、追问、回答、更新产品理解、调整获客方向。
- 输出：assistant message draft、ProductProfileRevision draft、LeadDirectionVersion draft。

---

## 4. V2.2 研究对象衔接

V2.2 再进入：

- `LeadResearchResult`
- `ResearchSource`
- `CompanyCandidate`
- `ContactPoint`

这些对象继续由：

- `docs/architecture/data/v2-lead-research-data-model.md`

定义。

关系：

```text
SalesAgentSession
    -> ProductProfileRevision
    -> LeadDirectionVersion
    -> LeadResearchResult
    -> ResearchSource / CompanyCandidate / ContactPoint
```

---

## 5. 数据流

V2.1 推荐数据流：

```text
User message
    ↓
ConversationMessage(role=user)
    ↓
AgentRun(run_type=sales_agent_turn)
    ↓
sales_agent_turn_graph
    ↓
typed draft payload
    ↓
services.py writeback
    ↓
ConversationMessage(role=assistant)
    ↓
ProductProfileRevision / LeadDirectionVersion
```

关键点：

- 每轮用户消息应可追溯到一次 AgentRun。
- 每次正式对象变化应能追溯到触发消息。
- agent 回答应能引用当前对象版本。

---

## 6. V2.1 最小 API 方向草案

仅作为后续 contract 设计输入，不是冻结 API。

```text
POST /sales-agent-sessions
GET  /sales-agent-sessions/{id}
POST /sales-agent-sessions/{id}/messages
GET  /sales-agent-sessions/{id}/messages
```

`POST /sales-agent-sessions/{id}/messages` 的响应建议包含：

- assistant message
- updated product profile summary
- current lead direction
- suggested next questions
- created agent run

---

## 7. Runtime 边界

Runtime 可以：

- 读取 session context。
- 判断用户意图。
- 生成追问。
- 生成回答。
- 生成 ProductProfileRevision draft。
- 生成 LeadDirectionVersion draft。

Runtime 不应：

- 直接写数据库。
- 直接修改正式对象。
- 把 LangGraph checkpoint 当成业务记忆主存。
- 自行创建云端用户、权限或计费逻辑。

---

## 8. 存储路线

V2.1 prototype 默认继续：

- 本地后端
- SQLite 可接受
- 按未来可迁云设计 schema

MVP 前必须单独冻结：

- Postgres
- User / Workspace
- 权限和数据隔离
- 数据保留 / 删除 / 脱敏
- 成本治理和监控

---

## 9. 验证指标草案

V2.1 数据模型是否有效，应验证：

- 一轮用户消息能创建对应 ConversationMessage。
- 一轮 agent 响应能创建 assistant ConversationMessage。
- 一次 AgentRun 能关联输入消息和输出对象。
- ProductProfileRevision 能追溯到 source_message_ids。
- LeadDirectionVersion 能记录用户调整方向的原因。
- 后续回答能引用当前 ProductProfileRevision 和 LeadDirectionVersion。

---

## 10. 待决问题

进入 schema / migration 前必须明确：

1. 是否将 `LeadDirectionVersion` 独立建表。
2. 是否首批持久化 `AgentContextPack`。
3. `SalesAgentSession.status` 是否只保留 `active / archived`。
4. `ConversationMessage.message_type` 枚举是否需要更细。
5. `sales_agent_turn_graph` draft schema。
6. 是否继续 SQLite 完成 V2.1 prototype。
7. 是否需要在 V2.1 引入 User / Workspace 占位字段。

---

## 11. 推荐下一步

推荐下一步不是直接写 migration，而是：

1. 冻结 V2.1 backend contract。
2. 冻结 V2.1 draft schemas。
3. 创建 backend-only prototype task。
4. 完成 V2.1 对话式销售 agent 后，再进入 V2.2 lead research 实现。
