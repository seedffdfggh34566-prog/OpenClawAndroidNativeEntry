# V2.1 Chat-first Runtime Design

更新时间：2026-04-27

## 1. 文档定位

本文档补齐 V2.1 product experience 的 Runtime 设计。

当前状态必须明确区分：

- **V2.1 engineering baseline completed**：Sales Workspace Kernel、Draft Review ID flow、Postgres / Alembic persistence chain、Sales Workspace Postgres store、Draft Review audit persistence 已完成。
- **V2.1 product experience not completed yet**：chat-first 产品理解、获客方向迭代、ConversationMessage / AgentRun trace、Runtime 基于 ContextPack 生成 `WorkspacePatchDraft` 的体验闭环尚未完成。

本文档只定义设计，不实现 backend route、LangGraph graph、真实 LLM、Android UI、search、ContactPoint 或 CRM。

## 2. 目标

V2.1 chat-first Runtime 的目标是让用户可以通过自然语言完成两类最小产品体验：

1. 让 Product Sales Agent 理解产品，并形成可审阅的 `ProductProfileRevision` draft。
2. 让 Product Sales Agent 维护获客方向，并形成可审阅的 `LeadDirectionVersion` draft。

这两类变化都必须通过：

```text
ConversationMessage
-> AgentRun(run_type = sales_agent_turn)
-> ContextPack
-> Runtime output WorkspacePatchDraft
-> DraftReview
-> WorkspacePatch
-> Sales Workspace Kernel apply
-> WorkspaceCommit
```

Runtime 不直接写正式 workspace object。

## 3. 非目标

- 不实现 LangGraph graph。
- 不接真实 LLM。
- 不新增 backend route。
- 不改 SQLAlchemy model 或 Alembic migration。
- 不改 Android。
- 不接 search provider。
- 不处理 ContactPoint。
- 不实现 CRM。
- 不改变现有 Draft Review apply 语义。
- 不把 LangGraph checkpoint、prompt、SDK session 或 Markdown projection 当成业务主存。

## 4. 核心边界

### 4.1 Backend 是正式写回裁决层

Backend / Sales Workspace Kernel 负责：

- 持久化 user / assistant `ConversationMessage`。
- 创建和更新 `AgentRun`。
- 编译 `ContextPack`。
- 接收 Runtime 返回的 `WorkspacePatchDraft`。
- 创建 `WorkspacePatchDraftReview`。
- 将 reviewed draft materialize 为 `WorkspacePatch`。
- 调用 Sales Workspace Kernel apply。
- 生成 `WorkspaceCommit`。

### 4.2 Runtime 是执行层

Runtime / Product Sales Agent execution layer 负责：

- 读取 typed runtime input。
- 根据用户消息和 ContextPack 判断意图。
- 生成 assistant draft message。
- 生成 `WorkspacePatchDraft`。
- 返回 runtime metadata。

Runtime 不负责：

- 直接写 DB。
- 直接更新 `SalesWorkspace`。
- 直接生成正式 `WorkspaceCommit`。
- 直接写 ranking board、Markdown projection 或 ContextPack。

### 4.3 Android 是人工审阅入口

Android 后续可以承接 chat-first 输入和 Draft Review 审阅，但仍不构造正式 `WorkspacePatch`，也不成为 formal truth layer。

## 5. 最小对象关系

```text
SalesWorkspace 1 --- N ConversationMessage
SalesWorkspace 1 --- N AgentRun
SalesWorkspace 1 --- N WorkspacePatchDraftReview
SalesWorkspace 1 --- N WorkspaceCommit

ConversationMessage 1 --- 0..N AgentRun input_refs
AgentRun 1 --- 1 ContextPack
AgentRun 1 --- 0..1 WorkspacePatchDraft
WorkspacePatchDraft 1 --- 1 WorkspacePatchDraftReview
WorkspacePatchDraftReview 1 --- 0..1 WorkspacePatch
WorkspacePatch 1 --- 0..1 WorkspaceCommit
WorkspaceCommit 1 --- N changed formal object refs
```

`ConversationMessage` 是输入轨迹，不是业务主真相。正式产品理解和获客方向必须落到 `ProductProfileRevision` 与 `LeadDirectionVersion`。

## 6. Chat-first Turn Flow

### 6.1 User message intake

用户在 workspace 中发送自然语言输入。

Backend 应创建 user message：

```text
ConversationMessage(
  role = user,
  message_type = product_profile_update | lead_direction_update | correction | question | mixed,
  content = raw user text,
  linked_object_refs = optional current object refs
)
```

`message_type` 可以先由 backend 使用轻量规则标记，也可以由 Runtime 在 draft metadata 中返回建议分类。无论哪种方式，分类都不是正式业务对象写回。

### 6.2 AgentRun creation

Backend 创建：

```text
AgentRun(
  run_type = sales_agent_turn,
  status = queued,
  input_refs = [
    ConversationMessage:<message_id>,
    SalesWorkspace:<workspace_id>,
    ProductProfileRevision:<current_revision_id>,
    LeadDirectionVersion:<current_direction_id>
  ]
)
```

V2.1 不引入 `waiting_for_user`、`paused`、`resumed`。人工审阅仍由 Draft Review lifecycle 表达。

### 6.3 ContextPack compilation

Backend 编译 `ContextPack(task_type = sales_agent_turn)`。

最小内容：

- workspace summary。
- current product profile revision summary。
- current lead direction version summary。
- recent user messages。
- open questions。
- latest draft review status。
- kernel boundary reminder。

ContextPack 从结构化 workspace state 编译，不从 Markdown projection、LangGraph checkpoint 或 SDK session 读取主真相。

### 6.4 Runtime execution

Runtime 输入：

```text
workspace_id
base_workspace_version
agent_run_id
user_message
context_pack
active_draft_review_context
instruction
```

Runtime 输出：

```text
assistant_message_draft
workspace_patch_draft?
runtime_metadata
open_questions
```

如果用户只问解释性问题，Runtime 可以只返回 assistant message draft，不返回 `WorkspacePatchDraft`。

如果用户提供了产品信息、获客方向或纠正意见，Runtime 应返回 `WorkspacePatchDraft`。

### 6.5 Draft Review

当 Runtime 返回 `WorkspacePatchDraft` 时，Backend 创建 `WorkspacePatchDraftReview(status = previewed)`。

用户可以：

- accept -> `reviewed`
- reject -> `rejected`
- 重新补充消息 -> 新建下一轮 `ConversationMessage` 和 `AgentRun`

只有 `reviewed` draft review 可以 apply。

### 6.6 Kernel apply

Apply 成功后：

- Workspace version 递增。
- Kernel 生成 `WorkspaceCommit`。
- Markdown projection 和 ContextPack 仍作为 derived outputs 读取。
- AgentRun output refs 记录 draft review、patch、commit 和变更对象。

Apply 失败时：

- workspace 不得部分 mutate。
- version conflict 应将 review 标记为 expired 或 failed apply result。
- 用户应重新刷新 workspace 并发起新一轮 chat-first turn。

## 7. Intent Classification

V2.1 最小 intent：

| intent | meaning | patch draft |
|---|---|---|
| `product_profile_update` | 用户补充或纠正产品信息 | yes |
| `lead_direction_update` | 用户补充或纠正获客方向 | yes |
| `mixed_product_and_direction_update` | 同时涉及产品和方向 | yes |
| `clarifying_question` | 用户回答不足，需要追问 | optional |
| `workspace_question` | 用户询问当前理解或方向解释 | no |
| `out_of_scope_v2_2` | 用户要求搜索、联系方式、CRM 或自动触达 | no |

对于 `out_of_scope_v2_2`，assistant message 应解释当前 V2.1 不做 evidence/search/contact，并建议先补齐产品理解或获客方向。

## 8. ProductProfileRevision Flow

### 8.1 Trigger

用户输入示例：

```text
我们做一个给中小制造企业用的排产和库存协同工具，主要解决订单变更后车间和仓库信息不同步的问题。
```

### 8.2 Runtime draft

Runtime 应生成 `WorkspacePatchDraft`，包含：

```text
operation.type = upsert_product_profile_revision
payload:
  id
  version
  product_name
  one_liner
  target_customers
  target_industries
  pain_points
  value_props
  constraints
```

assistant message draft 应说明：

- 当前理解到了什么。
- 哪些字段仍不确定。
- 下一步建议补充什么。

### 8.3 Review and apply

用户审阅后 accept，Backend materialize 为 `WorkspacePatch`，Kernel apply 后：

- `current_product_profile_revision_id` 指向新 revision。
- `WorkspaceCommit.changed_object_refs` 包含 `ProductProfileRevision:<id>`。
- 后续 ContextPack 使用新 revision。

## 9. LeadDirectionVersion Flow

### 9.1 Trigger

用户输入示例：

```text
先找华东地区 100 到 500 人的制造企业，最好已经有 ERP，但排产和库存还很割裂。先排除大型集团和教育行业。
```

### 9.2 Runtime draft

Runtime 应生成 `WorkspacePatchDraft`，包含：

```text
operation.type = upsert_lead_direction_version
payload:
  id
  version
  priority_industries
  target_customer_types
  regions
  company_sizes
  priority_constraints
  excluded_industries
  excluded_customer_types
  change_reason
```

如需显式切换 active direction，可附加：

```text
operation.type = set_active_lead_direction
payload:
  lead_direction_version_id
```

### 9.3 Review and apply

Apply 成功后：

- `current_lead_direction_version_id` 指向新 direction。
- 下一轮 ContextPack 读取新方向。
- V2.2 research 仍不自动启动。

## 10. Mixed Turn Flow

用户可能一次性同时提供产品理解和获客方向。

允许一个 `WorkspacePatchDraft` 同时包含：

1. `upsert_product_profile_revision`
2. `upsert_lead_direction_version`
3. optional `set_active_lead_direction`

Backend 必须按一个 `WorkspacePatch` 事务应用，成功则一个 `WorkspaceCommit` 记录全部变更，失败则 workspace 不变。

## 11. Assistant Message Semantics

assistant message 分三类：

| type | persisted when | notes |
|---|---|---|
| `clarification_question` | Runtime 需要用户补充信息时 | 不一定有 patch draft |
| `draft_summary` | Runtime 生成 patch draft 时 | 指向 `draft_review_id` |
| `explanation` | 用户询问当前 workspace 状态时 | 不产生 patch draft |

assistant message 可以引用 draft review，但不是正式对象写回裁决层。

## 12. Traceability

每轮 sales agent turn 至少应能追踪：

```text
user ConversationMessage
-> AgentRun(input_refs)
-> ContextPack(id, source_versions)
-> Runtime output WorkspacePatchDraft
-> WorkspacePatchDraftReview
-> WorkspacePatch
-> WorkspaceCommit
-> changed ProductProfileRevision / LeadDirectionVersion
-> assistant ConversationMessage
```

建议引用策略：

- `AgentRun.input_refs`：user message、workspace、current product revision、current direction、ContextPack。
- `AgentRun.output_refs`：assistant message、draft review、materialized patch、commit、changed objects。
- `WorkspacePatchDraft.runtime_metadata`：provider、mode、prompt_version、intent、source_message_ids、context_pack_id。
- `WorkspaceCommit.changed_object_refs`：正式对象引用，不引用 prompt 或 checkpoint 作为 truth。

## 13. Error Semantics

| case | expected behavior |
|---|---|
| invalid user message | reject before AgentRun or create failed AgentRun |
| missing workspace | `404 not_found` in future API |
| stale base version | draft review apply returns `409 workspace_version_conflict`; workspace unchanged |
| invalid draft | `422 patchdraft_validation_error`; no workspace mutation |
| unsupported operation | `400 unsupported_workspace_operation`; no workspace mutation |
| user rejects draft | draft review becomes `rejected`; no workspace mutation |
| out-of-scope V2.2 request | assistant message explains boundary; no patch draft |

## 14. ContextPack Update

Current `ContextPack` implementation only supports `task_type = research_round` in code. V2.1 product experience requires a future `sales_agent_turn` task type.

Design-only target:

```text
ContextPack.task_type = sales_agent_turn
```

Additional sections:

- `recent_messages`
- `current_product_profile_revision`
- `current_lead_direction_version`
- `active_draft_review_summary`
- `open_questions`
- `blocked_capabilities`

This is a future contract/design requirement, not a code change in this task.

## 15. V2.2 Boundary

The following requests stay blocked in V2.1:

- "帮我搜索真实客户"
- "给我找联系方式"
- "自动联系这些公司"
- "批量导出联系人"
- "接 CRM pipeline"

Runtime may reply with a boundary explanation, but must not generate formal `ResearchSource`、`CompanyCandidate`、`ContactPoint` 或 CRM payload for these requests until V2.2 tasks are explicitly opened.

## 16. Recommended Follow-up

Recommended next docs-only task:

- `task_v2_1_chat_first_runtime_contract_examples.md`

Purpose:

- 用 JSON examples 固定 chat-first 产品理解和获客方向的 state transition。
- 验证 `ConversationMessage`、`AgentRun`、`ContextPack`、`WorkspacePatchDraft`、`DraftReview`、`WorkspaceCommit` 的引用关系。
- 在进入 backend implementation 前发现 contract drift。

Implementation tasks remain blocked until examples are reviewed.
