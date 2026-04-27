# V2.1 Chat-first Trace Persistence Schema

更新时间：2026-04-27

## 1. Purpose

本文档定义 V2.1 chat-first product experience 所需的最小 trace persistence schema。

它只覆盖：

- `ConversationMessage`
- `AgentRun(run_type = sales_agent_turn)`
- `ContextPack(task_type = sales_agent_turn)`
- Draft Review / WorkspaceCommit / formal workspace object 的引用关系

本文档不实现 Alembic migration、SQLAlchemy ORM、backend route、Android UI、LangGraph graph、真实 LLM、search、ContactPoint 或 CRM。

---

## 2. Design Summary

V2.1 chat-first trace persistence 采用：

> **relational trace index + JSONB payload snapshots**

含义：

- relational fields 保存 identity、workspace ownership、role、run status、时间和常用查询字段。
- JSONB snapshots 保存完整 contract payload，避免早期 trace object 频繁 schema churn。
- Runtime trace 只记录执行过程，不成为 Sales Workspace formal truth layer。
- Draft Review lifecycle 继续由 `sales_workspace_draft_reviews` 与 `sales_workspace_draft_review_events` 表达。
- Workspace formal writeback 继续由 Sales Workspace Kernel 通过 `WorkspacePatch` / `WorkspaceCommit` 完成。

---

## 3. Persisted Objects

### 3.1 `sales_workspace_conversation_messages`

保存用户、assistant、system 消息。

Core columns:

```text
workspace_id text not null references sales_workspaces(workspace_id)
message_id text not null
role text not null
message_type text not null
content text not null
linked_object_refs_json jsonb not null default []
created_by_agent_run_id text null
payload_json jsonb not null
created_at timestamptz not null
primary key (workspace_id, message_id)
```

Allowed `role` values:

- `user`
- `assistant`
- `system`

Minimum V2.1 `message_type` values:

- `product_profile_update`
- `lead_direction_update`
- `mixed_product_and_direction_update`
- `clarifying_question`
- `workspace_question`
- `draft_summary`
- `out_of_scope_v2_2`
- `system_note`

Recommended indexes:

```text
(workspace_id, created_at)
(workspace_id, role, created_at)
(workspace_id, created_by_agent_run_id)
```

### 3.2 `sales_workspace_agent_runs`

保存 Product Sales Agent / Runtime 的一次 chat-first turn trace。

Core columns:

```text
workspace_id text not null references sales_workspaces(workspace_id)
agent_run_id text not null
run_type text not null
status text not null
input_refs_json jsonb not null default []
output_refs_json jsonb not null default []
runtime_metadata_json jsonb not null default {}
error_json jsonb null
payload_json jsonb not null
created_at timestamptz not null
started_at timestamptz null
finished_at timestamptz null
primary key (workspace_id, agent_run_id)
```

V2.1 only defines:

```text
run_type = sales_agent_turn
```

Allowed `status` values remain the lightweight lifecycle:

- `queued`
- `running`
- `succeeded`
- `failed`

Do not introduce `waiting_for_user`、`paused`、`resumed` in V2.1.

Recommended indexes:

```text
(workspace_id, created_at)
(workspace_id, status, created_at)
(workspace_id, run_type, created_at)
```

### 3.3 `sales_workspace_context_packs`

保存 Runtime 输入快照。

Core columns:

```text
workspace_id text not null references sales_workspaces(workspace_id)
context_pack_id text not null
agent_run_id text not null
task_type text not null
token_budget_chars integer not null
input_refs_json jsonb not null default []
source_versions_json jsonb not null default {}
payload_json jsonb not null
created_at timestamptz not null
primary key (workspace_id, context_pack_id)
```

Rules:

- `task_type` v2.1 value: `sales_agent_turn`。
- `payload_json` stores the complete ContextPack snapshot that Runtime saw.
- ContextPack is audit evidence, not formal workspace state.
- If ContextPack is later rebuilt, the rebuilt value must not overwrite old audit snapshots.

Recommended indexes:

```text
(workspace_id, agent_run_id)
(workspace_id, created_at)
(workspace_id, task_type, created_at)
```

---

## 4. Reference Strategy

`input_refs_json` 和 `output_refs_json` 使用 stable string refs。

Examples:

```text
ConversationMessage:msg_user_product_001
SalesWorkspace:ws_demo
ContextPack:ctx_sales_turn_product_001
WorkspacePatchDraftReview:draft_review_sales_turn_product_001
WorkspacePatch:patch_sales_turn_product_001
WorkspaceCommit:commit_v1
ProductProfileRevision:ppr_chat_001
LeadDirectionVersion:dir_chat_001
```

Rules:

- refs are audit links, not strict DB foreign keys for every target object.
- DB constraints should enforce workspace ownership for trace rows.
- cross-object existence and business validity remain backend service / kernel responsibilities.
- Runtime / LangGraph checkpoints may reference these ids later, but checkpoints do not replace these persisted trace rows.

---

## 5. Lifecycle Relationship

Minimum successful product-profile turn:

```text
ConversationMessage:user
-> AgentRun(status=running)
-> ContextPack snapshot
-> WorkspacePatchDraft
-> WorkspacePatchDraftReview(status=previewed)
-> ConversationMessage:assistant
-> AgentRun(status=succeeded)
```

After human review and apply:

```text
WorkspacePatchDraftReview(status=reviewed)
-> Sales Workspace Kernel apply
-> WorkspaceCommit
-> WorkspacePatchDraftReview(status=applied)
```

Rejected draft:

```text
WorkspacePatchDraftReview(status=rejected)
-> no WorkspaceCommit
-> workspace not mutated
```

AgentRun status does not replace Draft Review status. An `AgentRun` can be `succeeded` after producing a draft that is later rejected.

---

## 6. JSONB Boundaries

Use relational columns for:

- ids
- workspace ownership
- role / message type
- run type / run status
- timestamps
- query and ordering fields

Use JSONB snapshots for:

- full `ConversationMessage` payload
- full `AgentRun` payload
- full `ContextPack` payload
- `input_refs`
- `output_refs`
- runtime metadata
- error details
- source version summaries

Do not put formal `ProductProfileRevision` or `LeadDirectionVersion` truth only in trace JSON. Formal object truth remains in Sales Workspace tables and patch commits.

---

## 7. Migration Input

The next migration task should create:

- `sales_workspace_conversation_messages`
- `sales_workspace_agent_runs`
- `sales_workspace_context_packs`

Implementation notes:

- Postgres JSON fields should use JSONB.
- SQLite migration path may use generic JSON fallback for existing test compatibility.
- The migration must not change Draft Review tables except for optional non-breaking indexes if needed.
- The migration must not introduce LangGraph checkpoint tables.
- The migration must not implement search/contact/CRM schema.
