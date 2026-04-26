# V2 Sales Workspace Object Model

- 文档状态：Draft v0.1
- 更新日期：2026-04-26
- 阶段定位：V2 workspace-native sales agent 的对象模型草案；尚未冻结为 ORM、Alembic migration 或 API contract
- 建议路径：`docs/architecture/workspace/workspace-object-model.md`
- 关联文档：
  - `docs/product/prd/ai_sales_assistant_v2_prd.md`
  - `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`
  - `docs/architecture/data/v2-sales-agent-data-model.md`
  - `docs/architecture/data/v2-lead-research-data-model.md`
  - `docs/delivery/tasks/task_v2_sales_workspace_direction_update.md`

---

## 1. 文档目的

本文档定义 V2 **Sales Workspace Kernel** 的核心对象模型。

V2 产品北极星已经从“对话式专属销售 agent prototype”升级为：

> **workspace-native sales agent prototype / 中小企业专属销售工作区 Agent。**

因此，V2 的对象模型不应只围绕一次产品学习、一次获客分析或一份报告设计，而应支持：

1. 用户账号 / workspace 内部的长期销售信息沉淀。
2. 产品侧信息与客户挖掘侧信息分层管理。
3. 多轮 research round 后的候选客户合并、评分、排序和解释。
4. 来源证据与候选判断绑定。
5. 用户反馈反哺下一轮客户挖掘。
6. Markdown workspace projection 与结构化主存之间的同步。
7. Context pack compiler 在 token budget 内为 agent 编译最小必要上下文。

本文档不是：

- SQLAlchemy ORM 设计
- Alembic migration
- 完整 API contract
- Android UI 信息架构
- 搜索 provider 选型
- 合规政策文件

---

## 2. 设计总原则

### 2.1 SalesWorkspace 是 V2 根对象

V2 不再以 `ProductProfile -> LeadAnalysisResult -> AnalysisReport` 作为唯一主路径。

V2 的根对象应是：

```text
SalesWorkspace
```

`SalesWorkspace` 表示一个用户围绕某个产品、业务或销售目标持续工作的销售工作区。

它连接：

- 产品理解
- 获客方向
- 多轮客户挖掘
- 候选客户
- 来源证据
- 候选评分与排序
- 用户反馈
- agent 运行记录
- 报告 / 展示视图
- Markdown projection

### 2.2 结构化对象是产品主真相

正式业务状态必须落在结构化对象中，而不是只存在于 prompt、LLM provider session、LangGraph checkpoint、SDK session、Markdown 文件、临时 JSON 或 Android 本地状态。

Markdown 可以成为 agent 的可读写工作界面，但不能成为唯一权威主存。

### 2.3 Markdown 是 workspace projection，不是单一主存

Markdown 用于 agent-readable context、人工 review、git diff / commit 风格复盘、report / card rendering、debug / eval snapshot。

但以下能力必须由结构化对象保证：候选客户去重、跨轮次排序、证据绑定、评分历史、用户反馈追踪、API 查询、Android 展示和未来云端迁移。

### 2.4 Runtime 只产出 WorkspacePatchDraft

LangGraph / agent runtime 不直接写正式业务对象。

推荐边界：

```text
Agent runtime / LangGraph
    -> WorkspacePatchDraft
    -> backend validation
    -> WorkspacePatch
    -> structured objects
    -> Markdown projection regeneration
```

### 2.5 报告是发布视图，不是主存

`AnalysisReport` 继续有价值，但在 V2 中应降级为：

> 当前 workspace 状态的一种用户可读发布视图。

报告不应吞掉候选客户、来源证据、评分历史和用户反馈。

---

## 3. 对象分层

V2 Sales Workspace 对象建议分为七层：

```text
Workspace Layer       工作区根与提交记录
Product Layer         产品侧信息
Direction Layer       获客方向与约束
Research Layer        多轮客户挖掘过程
Evidence Layer        来源证据与观察事实
Candidate Layer       候选客户、评分、排序、状态
Interaction Layer     对话、反馈、报告、运行记录
```

---

## 4. 核心对象总览

V2 workspace kernel 首批建议对象：

```text
SalesWorkspace
WorkspaceCommit
WorkspacePatch
ConversationMessage
ProductProfileRevision
LeadDirectionVersion
ResearchRound
ResearchSource
CompanyCandidate
CandidateObservation
CandidateScoreSnapshot
CandidateRankingBoard
FeedbackEvent
ContextPack
AnalysisReport
AgentRun
```

首批暂不建议做成正式对象：

```text
Full CRM Account
Full CRM Contact
Deal / Opportunity pipeline
自动触达任务
批量联系人库
团队权限矩阵
付费计划 / billing
复杂审批流
```

---

## 5. Workspace Layer

## 5.1 `SalesWorkspace`

### 职责

`SalesWorkspace` 是 V2 的根对象，表示一个用户围绕某个产品或销售目标持续工作的销售空间。

### 建议字段

```text
id
workspace_key
owner_id
name
goal
status
current_product_profile_revision_id
current_lead_direction_version_id
current_candidate_ranking_board_id
latest_research_round_id
latest_report_id
workspace_repo_path
summary
created_at
updated_at
```

### 建议状态

```text
active -> archived
```

暂不建议引入 `paused`、`waiting_for_user`、`running`。运行态应交给 `AgentRun`，用户交互态应由消息与任务提示表达。

### 边界

`SalesWorkspace` 不是 CRM workspace，也不是账号系统。

首版可以使用：

```text
owner_id = local_user
workspace_key = local_default / generated slug
```

以便未来迁移到云端 user / workspace 模型。

---

## 5.2 `WorkspaceCommit`

### 职责

记录一次正式 workspace 状态变化，类似 git commit。它服务于 diff、revert、review、debug、解释 agent 改了什么、复盘某轮研究如何影响候选排序。

### 建议字段

```text
id
workspace_id
parent_commit_id
created_by
created_by_agent_run_id
patch_id
summary
changed_object_refs
changed_markdown_paths
created_at
```

### 建议 `created_by`

```text
user
agent
system
migration
```

### 边界

`WorkspaceCommit` 不直接承载完整对象内容。它记录“这次变更是什么”，完整状态仍在结构化对象和 projection 中。

---

## 5.3 `WorkspacePatch`

### 职责

表示一次待应用或已应用的 workspace 结构化变更。Runtime 输出的是 `WorkspacePatchDraft`，后端验证后落为 `WorkspacePatch`。

### 建议字段

```text
id
workspace_id
source_agent_run_id
patch_type
status
operations
validation_errors
applied_commit_id
created_at
applied_at
```

### 建议 `patch_type`

```text
sales_agent_turn
product_profile_update
lead_direction_update
research_round_result
candidate_ranking_update
feedback_update
report_generation
markdown_sync
```

### 建议 `status`

```text
draft -> validated -> applied -> rejected
```

### `operations` 示例

```json
[
  {
    "op": "create",
    "object_type": "company_candidate",
    "object_id": "cand_001",
    "payload": {}
  },
  {
    "op": "update",
    "object_type": "candidate_ranking_board",
    "object_id": "rank_001",
    "payload": {}
  }
]
```

### 边界

`WorkspacePatch` 是后端写回裁决对象，不是 runtime 私有状态。

---

## 6. Product Layer

## 6.1 `ProductProfile`

V2 沿用 V1 资产，但在 V2 中降级为当前产品理解主档。它不再决定整个产品主流程，只是 `SalesWorkspace` 内的一个核心业务对象。

建议继续沉淀产品名称、一句话描述、类别、目标客户、典型场景、痛点、核心优势、交付方式、限制条件和当前状态。

`ProductProfile` 表示当前主档，历史变化由 `ProductProfileRevision` 承担。

---

## 6.2 `ProductProfileRevision`

### 职责

保存某一版产品理解快照。后续 research round 必须引用明确的 revision，而不是只引用当前 `ProductProfile`。

### 建议字段

```text
id
workspace_id
product_profile_id
version
snapshot
change_summary
source_message_ids
source_feedback_event_ids
created_by_agent_run_id
created_by_commit_id
created_at
```

### `snapshot` 内容建议

```text
name
one_line_description
category
target_customers
target_industries
typical_use_cases
pain_points_solved
core_advantages
delivery_model
price_range
sales_region
constraints
open_questions
confidence_score
```

### 边界

`ProductProfileRevision` 是 research 的产品侧输入版本，不是报告，也不是聊天摘要。

---

## 7. Direction Layer

## 7.1 `LeadDirectionVersion`

### 职责

保存某一版获客方向。它是客户挖掘的策略输入，而不是候选客户列表。

### 建议字段

```text
id
workspace_id
version
product_profile_revision_id
objective
target_industries
target_customer_types
regions
company_size
price_range_fit
priority_constraints
excluded_industries
excluded_customer_types
excluded_regions
excluded_company_types
assumptions
reason_for_change
source_message_ids
source_feedback_event_ids
created_by_agent_run_id
created_by_commit_id
created_at
```

### 示例

```text
目标：优先寻找华东地区制造业中型企业，避免教育行业和大型集团客户。
```

### 边界

它不是 `LeadAnalysisResult`。`LeadAnalysisResult` 可以作为对方向的分析说明，但 `LeadDirectionVersion` 是后续 research round 的正式输入。

---

## 8. Research Layer

## 8.1 `ResearchRound`

### 职责

表示一轮客户挖掘实验。每次联网搜索、手动导入、mock research、候选重排，都应落到一个 `ResearchRound`。

### 建议字段

```text
id
workspace_id
round_index
product_profile_revision_id
lead_direction_version_id
objective
research_strategy
query_plan
status
source_count
candidate_count
new_candidate_count
updated_candidate_count
rejected_candidate_count
summary
limitations
created_by_agent_run_id
created_by_commit_id
started_at
finished_at
created_at
```

### 建议状态

```text
planned -> running -> completed -> failed -> superseded
```

### 边界

`ResearchRound` 不是最终结果。它是一轮实验记录，最终影响 `CandidateRankingBoard`。

---

## 8.2 `ResearchQuery`

记录一轮研究中实际发出的搜索 query。

建议字段：

```text
id
workspace_id
research_round_id
query_text
locale
intent
search_provider
status
result_count
created_by_agent_run_id
created_at
```

首版可以不单独建正式表，而是作为 `ResearchRound.query_plan` 的结构化 JSON。若要评估 query 质量，应独立建模。

---

## 8.3 `SearchResult`

保存搜索 provider 返回的原始结果条目。

首版可以暂缓持久化全部 `SearchResult`，只保存被采纳为证据的 `ResearchSource`。如果后续需要 query 质量分析、召回评估、缓存或复跑，再正式引入。

---

## 9. Evidence Layer

## 9.1 `ResearchSource`

### 职责

保存被系统实际用于推理、引用或支撑候选判断的来源。

### 建议字段

```text
id
workspace_id
research_round_id
search_result_id
url
title
source_type
publisher
retrieved_at
published_at
content_excerpt
summary
reliability_level
usage_scope
raw_metadata
created_at
```

### 建议 `source_type`

```text
company_website
government_page
industry_association
park_directory
procurement_notice
job_posting
news_article
social_profile
public_platform
other
```

### 边界

无来源候选不得进入正式 `CompanyCandidate` 的高置信结论。来源质量必须影响候选评分。

---

## 9.2 `CandidateObservation`

### 职责

保存一个候选客户相关的观察事实或判断。

它连接：

```text
ResearchSource -> observation -> CompanyCandidate -> score
```

### 建议字段

```text
id
workspace_id
candidate_id
research_round_id
source_id
observation_type
claim
confidence
polarity
created_by_agent_run_id
created_at
```

### 建议 `observation_type`

```text
fit_signal
pain_signal
timing_signal
budget_signal
accessibility_signal
contact_signal
risk_signal
exclusion_signal
user_preference_signal
```

### 建议 `polarity`

```text
positive
negative
neutral
uncertain
```

### 示例

```text
observation_type = timing_signal
claim = 该公司近期招聘销售运营经理，可能存在销售流程建设需求。
source_id = src_001
confidence = 0.72
```

### 边界

`CandidateObservation` 不等同于事实本身。它是“系统基于来源抽取或判断出的可审查 claim”。

---

## 10. Candidate Layer

## 10.1 `CompanyCandidate`

### 职责

保存一个候选客户 / 机构。它是 V2 多轮客户挖掘和优先级排序的核心对象。

### 建议字段

```text
id
workspace_id
normalized_name
display_name
legal_name
website
industry
region
company_size
summary
source_round_ids
current_status
current_score
current_rank
current_score_snapshot_id
created_by_research_round_id
created_at
updated_at
```

### 建议状态

```text
new
promising
selected
needs_verification
user_rejected
not_fit
contacted
archived
superseded
```

### 边界

`CompanyCandidate` 不是正式 CRM account。它表示“客户挖掘候选”。如果未来进入 CRM，应单独创建 `Account` / `Contact` / `Opportunity`，不要直接把候选对象扩成 CRM。

---

## 10.2 `CandidateScoreSnapshot`

### 职责

记录某个候选在某次评分中的详细分数与原因，用于解释排名变化。

### 建议字段

```text
id
workspace_id
candidate_id
research_round_id
ranking_board_id
scoring_policy_version
score_total
score_fit
score_pain_intensity
score_timing
score_accessibility
score_region_fit
score_company_size_fit
score_source_quality
score_contactability
score_user_preference_fit
penalties
score_reason
previous_rank
new_rank
created_by_agent_run_id
created_at
```

### 建议评分维度

```text
产品匹配度
痛点强度
近期触发信号
地区 / 交付适配
公司规模适配
公开来源质量
联系入口可验证性
购买路径可行性
用户偏好匹配
```

### 边界

不要只在 `CompanyCandidate` 上覆盖 `score`。必须保留评分历史，才能解释“为什么这个候选从第 8 名升到第 2 名”。

---

## 10.3 `CandidateRankingBoard`

### 职责

维护一个 workspace 内当前候选客户优先级榜单。

它承载用户所说的：

> 后续挖掘出来的客户比之前更具可行性时，在用户账号 / workspace 内部重新排序。

### 建议字段

```text
id
workspace_id
lead_direction_version_id
current_research_round_id
ranking_policy_version
ranked_candidate_refs
ranking_summary
ranking_delta
top_candidate_ids
needs_user_validation_candidate_ids
updated_by_agent_run_id
updated_by_commit_id
created_at
updated_at
```

### `ranked_candidate_refs` 示例

```json
[
  {
    "candidate_id": "cand_004",
    "rank": 1,
    "score": 86,
    "score_snapshot_id": "score_012",
    "movement": "new_entry"
  },
  {
    "candidate_id": "cand_001",
    "rank": 2,
    "score": 78,
    "score_snapshot_id": "score_013",
    "movement": "down_1"
  }
]
```

### `ranking_delta` 示例

```text
本轮新增 D 公司并提升为第一优先级，因为它比上一轮第一名 A 公司具备更强的近期触发信号、来源质量和可联系入口。
```

### 边界

`CandidateRankingBoard` 是产品展示和报告生成的核心输入之一。它不是一次 report 的临时列表。

---

## 10.4 `ContactPoint`

### 职责

保存候选公司的公开联系入口。

### 建议字段

```text
id
workspace_id
candidate_id
type
value
label
source_id
is_personal
confidence
usage_policy
retrieved_at
notes
created_at
```

### 使用策略

```text
display_only
manual_verify_required
do_not_auto_contact
```

### 边界

联系方式不是 V2.1 核心。V2.2 可受控引入，但必须有来源，默认人工验证，不自动触达，不批量导出，个人联系方式必须显式标记。

---

## 11. Interaction Layer

## 11.1 `ConversationMessage`

保存用户与 agent 的消息轨迹。

建议字段：

```text
id
workspace_id
session_id
role
content
message_type
linked_object_refs
created_by_agent_run_id
created_at
```

消息是输入轨迹，不是业务主真相。但它可以触发 `ProductProfileRevision`、`LeadDirectionVersion`、`FeedbackEvent` 和 `WorkspacePatch`。

---

## 11.2 `FeedbackEvent`

### 职责

保存用户对候选、方向、报告或 agent 判断的反馈。它是客户挖掘能力持续提升的关键。

### 建议字段

```text
id
workspace_id
feedback_target_type
feedback_target_id
feedback_type
reason
user_note
created_from_message_id
created_at
```

### 建议 `feedback_target_type`

```text
company_candidate
candidate_ranking_board
lead_direction_version
research_round
analysis_report
agent_answer
```

### 建议 `feedback_type`

```text
accepted
rejected
not_relevant
too_large
too_small
wrong_region
wrong_industry
needs_more_research
high_priority
low_priority
```

### 边界

用户反馈不应只写入聊天记录。它必须能影响下一版 `LeadDirectionVersion`、下一轮 `ResearchRound`、候选评分和 `ContextPack`。

---

## 11.3 `ContextPack`

### 职责

保存某次 agent run 输入给模型的上下文包，是 context pack compiler 的输出快照。

### 建议字段

```text
id
workspace_id
agent_run_id
task_type
token_budget
input_object_refs
source_versions
render_format
rendered_markdown
compiled_sections
created_at
```

### 建议 `task_type`

```text
sales_agent_turn
research_round
candidate_scoring
report_generation
feedback_learning
```

### 边界

`ContextPack` 不是业务主真相。它用于复现某次 agent 判断、调试 prompt、控制上下文窗口和支持 eval。

---

## 11.4 `AnalysisReport`

V2 中 `AnalysisReport` 是 workspace 当前状态的发布视图。

它可以读取当前产品理解、当前获客方向、当前候选排名榜、本轮 ranking delta、用户验证建议和来源证据摘要。

建议新增引用：

```text
workspace_id
candidate_ranking_board_id
research_round_id
source_ids
```

报告不是候选库，也不应成为唯一结果载体。

---

## 11.5 `AgentRun`

继续记录 agent / runtime 执行过程。

建议新增 run_type：

```text
sales_agent_turn
workspace_research_round
candidate_scoring
workspace_report_generation
feedback_learning
markdown_projection_sync
```

`AgentRun` 记录执行过程，不是正式业务对象主存。

---

## 12. 关键关系模型

推荐关系：

```text
SalesWorkspace 1 --- N WorkspaceCommit
SalesWorkspace 1 --- N WorkspacePatch
SalesWorkspace 1 --- N ConversationMessage

SalesWorkspace 1 --- N ProductProfileRevision
SalesWorkspace 1 --- N LeadDirectionVersion

ProductProfileRevision 1 --- N LeadDirectionVersion
LeadDirectionVersion 1 --- N ResearchRound

ResearchRound 1 --- N ResearchSource
ResearchRound 1 --- N ResearchQuery
ResearchRound 1 --- N CandidateObservation
ResearchRound 1 --- N CandidateScoreSnapshot

SalesWorkspace 1 --- N CompanyCandidate
CompanyCandidate 1 --- N CandidateObservation
CompanyCandidate 1 --- N CandidateScoreSnapshot
CompanyCandidate 1 --- N ContactPoint

LeadDirectionVersion 1 --- N CandidateRankingBoard
CandidateRankingBoard 1 --- N CandidateScoreSnapshot
CandidateRankingBoard 1 --- N AnalysisReport

FeedbackEvent N --- 1 SalesWorkspace
FeedbackEvent 0..N --- 1 CompanyCandidate
FeedbackEvent 0..N --- 1 LeadDirectionVersion

AgentRun 1 --- N WorkspacePatch
AgentRun 1 --- N ContextPack
AgentRun 1 --- N ProductProfileRevision
AgentRun 1 --- N ResearchRound
AgentRun 1 --- N CandidateScoreSnapshot
```

---

## 13. 多轮挖掘重排流程

V2 目标流程：

```text
1. 读取 SalesWorkspace 当前状态
2. ContextPackCompiler 编译最小上下文
3. Agent runtime 执行 research round
4. Runtime 返回 WorkspacePatchDraft
5. Backend 校验 patch
6. 创建 ResearchRound / ResearchSource / CompanyCandidate / CandidateObservation
7. 对候选生成 CandidateScoreSnapshot
8. 更新 CandidateRankingBoard
9. 生成 WorkspaceCommit
10. 重新生成 Markdown projection
11. 生成 AnalysisReport 或候选卡片
12. 用户反馈进入 FeedbackEvent
13. 下一轮 ContextPack 吸收反馈
```

---

## 14. 第一批落地切片建议

### 14.1 Backend-only prototype 首批对象

首批最小实现建议只做：

```text
SalesWorkspace
ProductProfileRevision
LeadDirectionVersion
ResearchRound
ResearchSource
CompanyCandidate
CandidateObservation
CandidateScoreSnapshot
CandidateRankingBoard
FeedbackEvent
WorkspacePatch
ContextPack
```

暂缓：

```text
ContactPoint
ResearchQuery 独立表
SearchResult 独立表
WorkspaceCommit 完整 diff / revert
AnalysisReport 改造
Android UI
真实搜索 provider
```

### 14.2 首批验证目标

用 fixture 验证：

```text
Round 1 产生 A / B / C 三个候选。
Round 2 产生 D，并且 D 由于来源质量、痛点强度、地区适配和可联系入口更好，被提升为第一名。
系统生成 CandidateScoreSnapshot。
系统更新 CandidateRankingBoard。
系统生成 ranking_delta 解释 D 为什么超过 A。
系统输出 markdown projection 和 context pack。
```

### 14.3 首批不做数据库 migration

首批建议：

```text
Pydantic schema + JSON fixture store + pytest
```

对象关系稳定后，再进入：

```text
SQLAlchemy ORM + Alembic migration
```

原因：当前对象模型仍处于 kernel prototype 阶段，过早建表会增加重构成本。

---

## 15. 与现有对象的关系

### 15.1 `ProductProfile`

保留，但不作为 V2 唯一主路径根对象。

### 15.2 `LeadAnalysisResult`

保留为方向分析 / 策略说明对象，不承载候选公司库和排序历史。

### 15.3 `AnalysisReport`

保留为发布视图，不承载核心 workspace 主存。

### 15.4 `AgentRun`

保留为执行记录，新增 workspace 相关 run_type。

---

## 16. 待决问题

进入 backend prototype 前，需要继续决定：

1. `SalesWorkspace` 是否首版落数据库，还是先用 Pydantic + JSON store。
2. `WorkspaceCommit` 首版是否只保留概念，不做完整 diff / revert。
3. `CandidateRankingBoard.ranked_candidate_refs` 首版用 JSON 还是 join table。
4. `ResearchSource` 是否必须首版正式持久化。
5. `FeedbackEvent` 是否需要在 V2.1 就进入首批实现。
6. Markdown projection 是单向生成，还是允许 agent 修改后反向解析为 patch。
7. `ContextPack` 首版是否持久化完整 rendered markdown。
8. 未来云端迁移时，`workspace_repo_path` 如何映射到 object storage / git storage。

---

## 17. 当前结论

`ProductProfile`、`LeadAnalysisResult`、`AnalysisReport`、`AgentRun` 可以继续复用，但它们不足以支撑 workspace-native sales agent。

V2 必须新增 `SalesWorkspace` 作为根对象，并围绕：

```text
ResearchRound
CompanyCandidate
CandidateObservation
CandidateScoreSnapshot
CandidateRankingBoard
FeedbackEvent
WorkspacePatch
ContextPack
```

建立 Sales Workspace Kernel。

这套对象模型的目的不是做完整 CRM，而是支撑：

> **多轮客户挖掘、证据化判断、候选优先级持续重排、用户反馈反哺和 context pack 编译。**
