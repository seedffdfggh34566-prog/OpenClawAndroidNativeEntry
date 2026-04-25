# V2 Lead Research Data Model

- 文档状态：Draft v0.1
- 更新日期：2026-04-25
- 阶段定位：V2.2 轻量线索研究数据架构草案，尚未冻结为数据库 schema 或 migration
- 关联文档：
  - `docs/product/prd/ai_sales_assistant_v2_prd.md`
  - `docs/architecture/data/v2-sales-agent-data-model.md`
  - `docs/reference/schemas/v1-domain-model-baseline.md`
  - `docs/architecture/system-context.md`

---

## 1. 文档目的

本文档定义 V2.2 “轻量线索研究”所需的数据对象、对象边界、关系和落地原则。

V2 当前产品形态已调整为“对话式专属销售 agent prototype”。因此本文档不再承担整个 V2 数据模型定义，而是作为 V2.2 lead research 子模型。V2.1 的会话、消息、产品画像版本和获客方向版本见：

- `docs/architecture/data/v2-sales-agent-data-model.md`

V1 的数据模型已经证明最小闭环可用：

```text
ProductProfile -> LeadAnalysisResult -> AnalysisReport
AgentRun 记录执行过程
```

V2.2 如果要支持主动联网 / 搜索、具体公司候选、来源证据和联系方式，就不能继续只把结果写成一段报告。

V2.2 数据层需要显式回答：

1. 哪一版 ProductProfile / LeadDirectionVersion 被用于搜索。
2. 搜索用了哪些 query。
3. 搜索命中了哪些来源。
4. 哪些来源支撑了哪些候选公司。
5. 哪些联系方式来自哪些来源。
6. 哪些结论是 LLM 推断，哪些有公开来源支持。
7. 用户最终看到的行动建议来自哪次研究。

本文档不是：

- ORM 设计
- Alembic migration
- 完整 API contract
- 合规政策
- 搜索 provider 选型

---

## 2. 设计原则

### 2.1 后端正式对象仍是主真相

V2 继续沿用 V1 架构边界：

- Android 是控制入口。
- 后端是正式业务系统。
- Runtime / Agent 负责 draft 和工具执行。
- 后端 services 负责正式对象写回。

任何 LLM 输出、搜索摘要、聊天消息都不能直接替代正式对象。

### 2.2 对话是输入轨迹，不是业务真相

Product learning 的对话需要保存，但它的角色是：

- 输入证据
- 用户表达轨迹
- 后续排查依据

正式业务真相仍是：

- `ProductProfile`
- `ProductProfileRevision`

### 2.3 来源是一等对象

V2 不能只保存“AI 认为某公司合适”。

每个候选公司、联系方式、关键判断都应尽量绑定：

- `ResearchSource`
- `SearchResult`
- `retrieved_at`
- `source_type`
- `confidence`

### 2.4 联系方式必须可溯源、可约束

联系方式不应混在公司候选的普通文本字段里。

必须单独建模：

- 公司联系方式和个人联系方式分开标记。
- 每个联系方式必须有来源。
- 每个联系方式必须有使用策略。
- 默认不支持自动触达。

### 2.5 借鉴仓库文档骨架

当前仓库 docs 已经形成一个清晰骨架：

```text
product/       定义方向和版本边界
architecture/  定义方案和结构
reference/     定义稳定 contract
delivery/      定义执行任务和 handoff
archive/       保存历史
```

V2 数据模型可借鉴这个思想，把销售研究也拆成几层：

```text
Direction      产品画像和研究目标
Evidence       搜索来源和网页证据
Synthesis      候选公司与匹配理由
Action         下一步销售动作
History        运行记录、版本和追溯
```

这能避免把所有信息混在一个 report JSON 里。

---

## 3. V1 对象复用

V2 不应丢弃 V1 对象。

### 3.1 `ProductProfile`

继续作为产品理解主档。

V2 中的变化：

- ProductProfile 由对话式产品学习逐步生成。
- 每次关键变化应形成 `ProductProfileRevision`。
- LeadResearch 必须引用明确的 ProductProfile 版本。

### 3.2 `LeadAnalysisResult`

继续作为“方向分析”对象。

V2 中的变化：

- 它不直接承载具体公司线索库。
- 它主要输出研究方向、优先行业、客户类型、场景假设。
- `LeadResearchResult` 基于它进一步联网研究。

### 3.3 `AnalysisReport`

继续作为用户可复看的报告对象。

V2 中的变化：

- 报告应引用 `LeadResearchResult`。
- 报告不再是唯一结果载体。
- 候选公司卡片、来源和联系入口应作为结构化对象保存。

### 3.4 `AgentRun`

继续记录执行过程。

V2 中的变化：

- 需要覆盖新的 `run_type`，例如 `lead_research`。
- `runtime_metadata` 应继续记录 provider、model、prompt_version、usage、latency、source_count 等。
- 工具调用和来源证据不应只塞进 `runtime_metadata`，应沉淀为正式或准正式研究对象。

---

## 4. V2.2 建议新增对象

### 4.1 `ProductLearningSession`

状态：

- V2.1 已不建议使用该名称作为主会话对象。
- 主会话对象改为 `SalesAgentSession`，见 `v2-sales-agent-data-model.md`。

历史职责：

- 表示一次产品学习会话。
- 连接用户对话、ProductProfile 草稿、ProductProfileRevision 和 AgentRun。

建议字段：

- `id`
- `product_profile_id`
- `status`
- `started_at`
- `ended_at`
- `created_by`
- `last_agent_run_id`
- `summary`

边界：

- 它不是 ProductProfile。
- 它是产品学习过程容器。

### 4.2 `ConversationMessage`

状态：

- V2.1 已将 `ConversationMessage` 提升为首批对象。
- 本节仅保留与 V2.2 lead research 的衔接背景。

职责：

- 保存产品学习中的用户消息、AI 追问和系统摘要。

建议字段：

- `id`
- `session_id`
- `role`
- `content`
- `message_type`
- `source`
- `created_at`
- `agent_run_id`

边界：

- 消息是输入轨迹。
- 消息不能直接作为后续研究的唯一正式输入。

### 4.3 `ProductProfileRevision`

职责：

- 保存 ProductProfile 的版本变化。
- 让后续研究可以引用具体版本。

建议字段：

- `id`
- `product_profile_id`
- `version`
- `snapshot`
- `change_summary`
- `source_session_id`
- `created_by_agent_run_id`
- `created_at`

边界：

- ProductProfile 表示当前主档。
- ProductProfileRevision 表示历史快照和可追溯输入版本。

### 4.4 `LeadResearchResult`

职责：

- 表示一次基于 ProductProfile / LeadAnalysisResult 的联网线索研究结果。

建议字段：

- `id`
- `product_profile_id`
- `product_profile_revision_id`
- `lead_analysis_result_id`
- `created_by_agent_run_id`
- `status`
- `research_scope`
- `summary`
- `candidate_count`
- `source_count`
- `confidence_summary`
- `limitations`
- `created_at`
- `updated_at`

边界：

- 它不是 CRM 线索库。
- 它是一轮研究快照。
- 候选公司、来源和联系方式应拆到独立对象。

### 4.5 `ResearchQuery`

职责：

- 保存系统实际使用过的搜索 query。

建议字段：

- `id`
- `lead_research_result_id`
- `query_text`
- `locale`
- `search_provider`
- `intent`
- `created_by_agent_run_id`
- `created_at`

边界：

- Query 是研究过程证据。
- 不直接等于最终候选。

### 4.6 `SearchResult`

职责：

- 保存搜索 provider 返回的条目级结果。

建议字段：

- `id`
- `research_query_id`
- `title`
- `url`
- `snippet`
- `rank`
- `retrieved_at`
- `raw_metadata`

边界：

- SearchResult 是搜索返回。
- ResearchSource 是系统选择进入证据集的来源。

### 4.7 `ResearchSource`

职责：

- 保存被系统实际用于推理、引用或支撑候选的来源。

建议字段：

- `id`
- `lead_research_result_id`
- `search_result_id`
- `url`
- `title`
- `source_type`
- `publisher`
- `retrieved_at`
- `published_at`
- `content_excerpt`
- `summary`
- `reliability_level`
- `usage_scope`

边界：

- 它是 V2 线索研究的关键证据对象。
- 候选公司和联系方式应引用它。

### 4.8 `CompanyCandidate`

职责：

- 保存一个具体公司 / 机构候选。

建议字段：

- `id`
- `lead_research_result_id`
- `name`
- `legal_name`
- `website`
- `industry`
- `location`
- `matched_needs`
- `match_reason`
- `evidence_source_ids`
- `confidence`
- `uncertainties`
- `priority_rank`
- `recommended_next_step`
- `status`

建议状态：

```text
draft -> selected -> dismissed -> superseded
```

边界：

- 它不是联系人。
- 它不是 CRM account。
- 它是一轮研究产出的候选公司卡片。

### 4.9 `ContactPoint`

职责：

- 保存候选公司的公开联系入口。

建议字段：

- `id`
- `company_candidate_id`
- `type`
- `value`
- `label`
- `source_id`
- `is_personal`
- `confidence`
- `retrieved_at`
- `usage_policy`
- `notes`

建议 `type`：

- `company_phone`
- `company_email`
- `website_contact_page`
- `address`
- `social_profile`
- `person_email`
- `person_phone`
- `other`

建议 `usage_policy`：

- `display_only`
- `manual_verify_required`
- `do_not_auto_contact`

边界：

- 不支持自动触达。
- 不支持批量导出。
- 个人联系方式必须显式标记 `is_personal = true`。
- 没有来源的联系方式不应进入正式对象。

### 4.10 `SalesActionCard`

职责：

- 把候选公司转化为用户下一步可执行动作。

建议字段：

- `id`
- `lead_research_result_id`
- `company_candidate_id`
- `priority`
- `action_type`
- `opening_angle`
- `validation_questions`
- `recommended_channel`
- `risk_notes`
- `created_at`

边界：

- 它是建议，不是自动执行任务。
- 不触发自动外呼、自动邮件或企微消息。

---

## 5. 对象关系

建议关系：

```text
ProductLearningSession 1 --- N ConversationMessage
ProductLearningSession 1 --- N ProductProfileRevision

ProductProfile 1 --- N ProductProfileRevision
ProductProfileRevision 1 --- N LeadResearchResult

ProductProfile 1 --- N LeadAnalysisResult
LeadAnalysisResult 1 --- N LeadResearchResult

LeadResearchResult 1 --- N ResearchQuery
ResearchQuery 1 --- N SearchResult
SearchResult 0..1 --- N ResearchSource

LeadResearchResult 1 --- N CompanyCandidate
ResearchSource N --- N CompanyCandidate
CompanyCandidate 1 --- N ContactPoint
CompanyCandidate 1 --- N SalesActionCard

AgentRun 1 --- N ProductProfileRevision
AgentRun 1 --- N LeadResearchResult
AgentRun 1 --- N ResearchQuery
AgentRun 1 --- N ResearchSource
AgentRun 1 --- N CompanyCandidate
```

说明：

- `ResearchSource N --- N CompanyCandidate` 可以先通过 `evidence_source_ids` 简化为 JSON 引用，后续再正规化为 join table。
- 首版实现可以小步落地，不必一次性建满所有表。

---

## 6. 数据流

V2 推荐数据流：

```text
用户输入
    ↓
ConversationMessage
    ↓
ProductLearningSession
    ↓
ProductProfileRevision
    ↓
ProductProfile
    ↓
LeadAnalysisResult
    ↓
AgentRun(run_type = lead_research)
    ↓
ResearchQuery / SearchResult / ResearchSource
    ↓
CompanyCandidate / ContactPoint
    ↓
LeadResearchResult
    ↓
SalesActionCard / AnalysisReport
```

关键点：

- 后续研究必须引用 ProductProfileRevision，而不是只引用当前 ProductProfile。
- 搜索来源必须独立保存。
- 联系方式必须独立保存。
- 报告只能作为表达层，不能吞掉结构化研究对象。

---

## 7. V2.2 落地建议

由于 V2.1 会先实现对话式销售 agent，不建议 V2.2 一次性落全部对象。

V2.2 建议首批实现：

1. `LeadResearchResult`
2. `ResearchSource`
3. `CompanyCandidate`
4. `ContactPoint`
5. `AgentRun.run_type = lead_research`

暂缓：

- `ResearchQuery`
- `SearchResult`
- `SalesActionCard`

暂缓原因：

- 搜索 provider 尚未确定。
- 成功标准尚未冻结。
- 联系方式展示边界尚未完全明确。

可接受的首版简化：

- Search query 可以先记录在 `LeadResearchResult.research_scope` 或 `runtime_metadata`。
- SearchResult 可以先不完整落表，只保存被采用的 `ResearchSource`。
- SalesActionCard 可以先作为 CompanyCandidate 的 `recommended_next_step` 字段。

---

## 8. 与当前 V1 后端的衔接

### 8.1 不破坏 V1 对象

V2 不应修改 V1 对象语义：

- `ProductProfile` 仍是产品主档。
- `LeadAnalysisResult` 仍是方向分析。
- `AnalysisReport` 仍是报告。
- `AgentRun` 仍是运行记录。

### 8.2 新增 run type

建议新增：

```text
lead_research
```

语义：

- 输入：ProductProfileRevision 或 ProductProfile + LeadAnalysisResult。
- 执行：搜索、来源筛选、候选生成。
- 输出：LeadResearchResult、ResearchSource、CompanyCandidate、ContactPoint。

### 8.3 Runtime 边界

Runtime 可以：

- 生成搜索 query。
- 调用搜索 provider。
- 摘要来源。
- 生成候选草稿。
- 标记置信度和不确定性。

Runtime 不应：

- 直接写正式数据库对象。
- 自行决定联系方式合规策略。
- 把无来源候选写入正式结果。
- 把聊天记录直接当成 ProductProfile。

---

## 9. 数据质量规则

### 9.1 候选公司规则

CompanyCandidate 进入正式结果前应满足：

- 有名称。
- 至少有一个 `ResearchSource`。
- 有匹配理由。
- 有置信度。
- 有不确定性说明或待验证点。

不满足来源要求时，只能作为 runtime draft，不应成为正式候选。

### 9.2 来源规则

ResearchSource 应满足：

- 有 URL。
- 有 retrieved_at。
- 有 source_type。
- 有摘要或摘录。
- 能说明被用于支撑哪个候选或判断。

### 9.3 联系方式规则

ContactPoint 应满足：

- 有 type。
- 有 value。
- 有 source_id。
- 有 retrieved_at。
- 有 usage_policy。

个人联系方式还必须：

- `is_personal = true`
- `usage_policy` 至少为 `manual_verify_required`
- 禁止自动触达

---

## 10. 保留与删除策略草案

本节尚未冻结，只作为后续设计输入。

建议：

- ProductProfileRevision 长期保留。
- LeadResearchResult 长期保留。
- ResearchSource 保留摘要、URL、retrieved_at，不默认长期保存完整网页正文。
- SearchResult 原始返回可短期保留或仅 dev trace 保留。
- ContactPoint 保留需受使用策略约束。
- 个人联系方式应支持后续删除或脱敏。

待决：

- 是否允许保存完整网页正文。
- 是否需要来源内容过期刷新。
- 是否需要用户级删除请求。
- 是否需要按 workspace 隔离。

---

## 11. 最小 API 方向草案

仅作为后续 contract 设计输入，不是冻结 API。

可能需要：

```text
POST /product-learning-sessions
POST /product-learning-sessions/{id}/messages
GET  /product-learning-sessions/{id}

POST /product-profiles/{id}/revisions
GET  /product-profiles/{id}/revisions

POST /lead-research-runs
GET  /lead-research-results/{id}
GET  /lead-research-results/{id}/sources
GET  /lead-research-results/{id}/candidates
```

首版可以更小：

```text
POST /product-profiles/{id}/lead-research
GET  /analysis-runs/{id}
GET  /lead-research-results/{id}
```

选择原则：

- 先验证研究质量和来源证据。
- 不急于公开复杂会话 API。
- 不让 API 设计先于数据边界冻结。

---

## 12. 验证指标草案

数据模型是否有效，不能只看表是否建出来。

建议验证：

- 一个 LeadResearchResult 能追溯到明确 ProductProfileRevision。
- 每个 CompanyCandidate 至少能追溯到一个 ResearchSource。
- 每个 ContactPoint 都能追溯到一个 ResearchSource。
- 删除或隐藏 ContactPoint 不影响 CompanyCandidate 本身。
- AnalysisReport 可以只引用 LeadResearchResult，不复制全部候选明细。
- Developer inspector 可以查看 LLM 输出，但正式对象不依赖 inspector trace。

---

## 13. 待决问题

进入 schema / migration 前必须明确：

1. 是否在 V2 首批实现 ConversationMessage。
2. 是否在 V2 首批实现 ProductLearningSession。
3. 是否保存 SearchResult 原始条目。
4. 是否保存完整网页正文。
5. 是否允许无联系方式的候选公司进入正式结果。
6. 是否允许个人联系方式进入正式结果。
7. ContactPoint 是否需要用户级隐藏 / 删除。
8. LeadResearchResult 是否必须绑定 LeadAnalysisResult。
9. ProductProfileRevision 是否独立建表，还是先用 JSON snapshot。
10. 是否需要 workspace / owner 字段在 V2 首批实现。

---

## 14. 推荐下一步

推荐下一步不是直接写 migration，而是：

1. 用本文档和 V2 PRD 先冻结首批对象集合。
2. 明确搜索 provider、数据保留和联系方式边界。
3. 设计 `lead_research` backend contract。
4. 做一个后端-only spike：固定 ProductProfile 输入，生成带来源的 CompanyCandidate。
5. 用 5 到 10 个中文真实业务样例验证候选质量。
