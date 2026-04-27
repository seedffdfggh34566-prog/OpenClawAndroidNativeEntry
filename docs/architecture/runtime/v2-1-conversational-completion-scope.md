# V2.1 Conversational Completion Scope

日期：2026-04-27

## 1. Purpose

本文定义完整 V2.1 conversational product experience 的剩余最小范围。

它基于 `docs/product/research/v2_1_prd_acceptance_gap_review_2026_04_27.md`，目标是把 PRD gap 转成可执行 task queue，而不是启动 V2.2。

## 2. Completion Definition

V2.1 conversational product experience 完成意味着：

```text
user chat input
-> ConversationMessage
-> SalesAgentTurnRun
-> ContextPack
-> deterministic Product Sales Agent behavior
-> assistant message and/or WorkspacePatchDraft
-> Draft Review
-> WorkspacePatch
-> ProductProfileRevision / LeadDirectionVersion
-> traceable workspace state visible from backend and Android
```

其中 deterministic Product Sales Agent behavior 必须覆盖：

- 主动追问 3 到 5 个关键问题。
- 从中文自然语言中形成第一版产品理解。
- 根据用户自然语言调整获客方向。
- 基于当前 workspace objects 给出解释型回答。
- 在不进入 V2.2 时明确拒绝联网搜索、联系人、CRM 或自动触达请求。

## 3. Required Behaviors

### 3.1 Clarifying questions

当用户输入不足以形成产品理解或获客方向时，Product Sales Agent 必须返回 3 到 5 个中文追问。

追问应覆盖：

- 产品做什么。
- 目标客户是谁。
- 主要痛点是什么。
- 区域或行业优先级。
- 不想优先覆盖的客户或行业。

本行为可以先 deterministic 实现，不要求真实 LLM。

### 3.2 Product profile extraction

对于包含产品信息的用户输入，Runtime 应生成可审阅的 `WorkspacePatchDraft`，写入 `ProductProfileRevision`。

最小字段：

- product name / category
- one-liner
- target customers
- target industries
- pain points
- value props
- constraints / uncertainty
- source message refs

### 3.3 Lead direction adjustment

对于获客方向或纠正类输入，Runtime 应生成新的 `LeadDirectionVersion`。

最小字段：

- priority industries
- target customer types
- regions
- company sizes
- priority constraints
- excluded industries / customer types
- change reason
- source message refs

### 3.4 Workspace explanation

当用户询问“为什么推荐这个方向”“风险是什么”“先做哪个方向”时，Product Sales Agent 应返回 assistant message，不一定生成 patch draft。

回答必须引用当前：

- `ProductProfileRevision`
- `LeadDirectionVersion`
- ContextPack source versions
- 已有 ranking / observations，如果存在

### 3.5 Traceability and recovery

每轮 turn 必须保留：

- user / assistant `ConversationMessage`
- `SalesAgentTurnRun.input_refs`
- `SalesAgentTurnRun.output_refs`
- `ContextPack`
- `WorkspacePatchDraftReview`
- `WorkspaceCommit`
- changed object refs

Postgres 模式下，重启 backend 后应可读取 workspace、messages、AgentRun、ContextPack、Draft Review 和 formal objects。

## 4. Explicit Non-goals

V2.1 conversational completion 不包含：

- V2.2 evidence/search/contact。
- 真实 LLM provider。
- 正式 LangGraph graph。
- CRM。
- 自动触达。
- ContactPoint。
- 大规模 Android 聊天 UI 重写。
- 多用户权限。

## 5. Recommended Implementation Order

1. Clarifying questions backend prototype。
2. Workspace explanation backend prototype。
3. Product profile extraction deterministic runtime。
4. Lead direction adjustment deterministic runtime。
5. Conversation acceptance e2e tests over 5 Chinese business samples。
6. Minimal Android polish only if backend acceptance is green。

Only the first implementation task should be opened automatically.
