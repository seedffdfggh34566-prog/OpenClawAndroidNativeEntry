# Sales Workspace Chat-first Runtime Contract

更新时间：2026-04-27

## 1. 文档定位

本文档定义 V2.1 chat-first product experience 的 future contract。

它用于说明用户消息、AgentRun、ContextPack、Runtime output、Draft Review 和 WorkspaceCommit 的最小边界。

本文档不是：

- FastAPI route implementation
- SQLAlchemy / Alembic migration
- Android UI implementation
- LangGraph graph implementation
- real LLM contract
- V2.2 search / ContactPoint / CRM contract

## 2. Contract Goal

V2.1 chat-first Runtime contract 只覆盖：

- 产品理解更新。
- 获客方向更新。
- 当前 workspace 状态解释。
- 追问缺失信息。

Runtime 可以输出 `WorkspacePatchDraft`，但正式写回仍由 Draft Review 和 Sales Workspace Kernel 裁决。

## 3. Future Object Shapes

### 3.1 `ConversationMessage`

```json
{
  "id": "msg_user_001",
  "workspace_id": "ws_demo",
  "role": "user",
  "message_type": "product_profile_update",
  "content": "我们做一个给中小制造企业用的排产和库存协同工具。",
  "linked_object_refs": [],
  "created_by_agent_run_id": null,
  "created_at": "2026-04-27T00:00:00Z"
}
```

Allowed `role` values:

- `user`
- `assistant`
- `system`

V2.1 minimum `message_type` values:

- `product_profile_update`
- `lead_direction_update`
- `mixed_product_and_direction_update`
- `clarifying_question`
- `workspace_question`
- `out_of_scope_v2_2`
- `system_note`

### 3.2 `SalesAgentTurnRun`

`SalesAgentTurnRun` maps to future `AgentRun(run_type = sales_agent_turn)`.

```json
{
  "id": "run_sales_turn_001",
  "workspace_id": "ws_demo",
  "run_type": "sales_agent_turn",
  "status": "succeeded",
  "input_refs": [
    "ConversationMessage:msg_user_001",
    "SalesWorkspace:ws_demo",
    "ContextPack:ctx_sales_turn_001"
  ],
  "output_refs": [
    "WorkspacePatchDraftReview:draft_review_sales_turn_001",
    "ConversationMessage:msg_assistant_001"
  ],
  "runtime_metadata": {
    "provider": "future_runtime_provider",
    "mode": "chat_first_design",
    "intent": "product_profile_update"
  },
  "error": null
}
```

Allowed status values stay within the existing lightweight lifecycle:

- `queued`
- `running`
- `succeeded`
- `failed`

V2.1 does not introduce `waiting_for_user`、`paused`、`resumed`。

### 3.3 `SalesAgentTurnContextPack`

Future `ContextPack(task_type = sales_agent_turn)` shape:

```json
{
  "id": "ctx_sales_turn_001",
  "workspace_id": "ws_demo",
  "task_type": "sales_agent_turn",
  "token_budget_chars": 6000,
  "workspace_summary": "FactoryOps AI workspace",
  "current_product_profile_revision": {
    "id": "ppr_v1",
    "summary": "FactoryOps AI helps manufacturing teams coordinate scheduling and inventory."
  },
  "current_lead_direction_version": {
    "id": "dir_v1",
    "summary": "Target mid-market manufacturing companies in East China."
  },
  "recent_messages": [
    {
      "id": "msg_user_001",
      "role": "user",
      "content_excerpt": "先找华东地区 100 到 500 人的制造企业。"
    }
  ],
  "active_draft_review_summary": null,
  "open_questions": [],
  "blocked_capabilities": [
    "V2.2 evidence/search/contact"
  ],
  "kernel_boundary": "Runtime returns WorkspacePatchDraft; Sales Workspace Kernel validates and writes formal objects."
}
```

### 3.4 `SalesAgentTurnRuntimeOutput`

```json
{
  "assistant_message_draft": {
    "role": "assistant",
    "message_type": "draft_summary",
    "content": "我已整理出一版产品理解草稿，请审阅后应用。"
  },
  "patch_draft": {
    "id": "draft_sales_turn_001",
    "workspace_id": "ws_demo",
    "base_workspace_version": 3,
    "author": "sales_agent_turn_runtime",
    "instruction": "update product profile from chat-first input",
    "runtime_metadata": {
      "agent_run_id": "run_sales_turn_001",
      "context_pack_id": "ctx_sales_turn_001",
      "intent": "product_profile_update",
      "source_message_ids": ["msg_user_001"]
    },
    "operations": []
  },
  "open_questions": [
    "是否主要面向离散制造还是流程制造？"
  ],
  "runtime_metadata": {
    "provider": "future_runtime_provider",
    "mode": "chat_first_design"
  }
}
```

`patch_draft` may be null when the turn is only a question or explanation.

## 4. Product Profile Update Patch

Runtime output for product understanding should use existing kernel operation:

```json
{
  "type": "upsert_product_profile_revision",
  "payload": {
    "id": "ppr_chat_001",
    "version": 2,
    "product_name": "FactoryOps AI",
    "one_liner": "Manufacturing scheduling and inventory coordination assistant.",
    "target_customers": ["mid-market manufacturing companies"],
    "target_industries": ["manufacturing"],
    "pain_points": ["scheduling changes do not sync with inventory"],
    "value_props": ["reduce operational data fragmentation"],
    "constraints": ["needs ERP-adjacent workflow data"]
  }
}
```

Rules:

- Runtime may suggest fields but does not assign formal truth by itself.
- Backend validates payload using kernel schema.
- Draft Review captures preview before apply.
- Kernel apply updates `current_product_profile_revision_id`.

## 5. Lead Direction Update Patch

Runtime output for lead direction should use existing kernel operation:

```json
{
  "type": "upsert_lead_direction_version",
  "payload": {
    "id": "dir_chat_001",
    "version": 2,
    "priority_industries": ["manufacturing"],
    "target_customer_types": ["mid-market manufacturers with ERP"],
    "regions": ["East China"],
    "company_sizes": ["100-500 employees"],
    "priority_constraints": ["has ERP but weak scheduling/inventory coordination"],
    "excluded_industries": ["education"],
    "excluded_customer_types": ["large conglomerates"],
    "change_reason": "User clarified target segment in chat."
  }
}
```

Optional active direction operation:

```json
{
  "type": "set_active_lead_direction",
  "payload": {
    "lead_direction_version_id": "dir_chat_001"
  }
}
```

## 6. Future API Surface

The following endpoints are future contract placeholders, not implemented by this PR:

- `POST /sales-workspaces/{workspace_id}/messages`
- `POST /sales-workspaces/{workspace_id}/agent-runs/sales-agent-turns`
- `GET /sales-workspaces/{workspace_id}/agent-runs/{agent_run_id}`

Current prototype endpoints remain valid:

- `POST /sales-workspaces/{workspace_id}/draft-reviews`
- `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/review`
- `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/apply`
- `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/reject`

## 7. Trace Rules

Minimum trace relationship:

```text
ConversationMessage:user
-> AgentRun.input_refs
-> ContextPack
-> WorkspacePatchDraft.runtime_metadata
-> WorkspacePatchDraftReview
-> WorkspacePatch
-> WorkspaceCommit
-> AgentRun.output_refs
-> ConversationMessage:assistant
```

Failure cases must still preserve enough trace:

- failed AgentRun records error and input refs.
- invalid draft records validation error.
- rejected draft review records reviewer decision.
- expired draft review records version conflict.

## 8. Error Semantics

| error | meaning | mutation |
|---|---|---|
| `404 not_found` | workspace, message, run, or review not found | none |
| `409 workspace_version_conflict` | draft base version stale | none |
| `409 draft_review_state_conflict` | illegal review/apply transition | none |
| `422 validation_error` | request shape invalid | none |
| `422 patchdraft_validation_error` | Runtime output invalid | none |
| `400 unsupported_workspace_operation` | patch contains unsupported operation | none |

## 9. V2.2 Blocked Capabilities

This contract intentionally does not support:

- real search provider calls
- source fetch verification
- ContactPoint
- CRM
- automated outreach
- candidate research beyond existing prototype fixtures

If the user asks for those capabilities, the Product Sales Agent should explain the boundary and ask for product / direction refinement instead of generating unsupported formal objects.
