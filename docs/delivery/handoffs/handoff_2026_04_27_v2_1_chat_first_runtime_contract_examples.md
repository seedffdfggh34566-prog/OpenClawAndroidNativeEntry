# Handoff: V2.1 Chat-first Runtime Contract Examples

日期：2026-04-27

## 1. Changed

- Added V2.1 chat-first Runtime contract examples.
- Added fixed JSON examples for user messages, AgentRun, ContextPack, WorkspacePatchDraft, Draft Review accept/apply, rejected draft, and V2.2 out-of-scope response.
- Updated the reference docs entry and task status.

## 2. Files

- `docs/reference/api/sales-workspace-chat-first-runtime-examples.md`
- `docs/reference/api/examples/sales_workspace_chat_first_runtime_v2_1/*.json`
- `docs/reference/README.md`
- `docs/delivery/tasks/task_v2_1_chat_first_runtime_contract_examples.md`

## 3. Validation

Planned validation:

```bash
find docs/reference/api/examples/sales_workspace_chat_first_runtime_v2_1 -name "*.json" -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
rg "sales-workspace-chat-first-runtime-examples.md|sales_workspace_chat_first_runtime_v2_1" docs/reference docs/delivery docs/README.md
rg "ConversationMessage|AgentRun|ContextPack|WorkspacePatchDraft|draft_review_sales_turn" docs/reference/api/sales-workspace-chat-first-runtime-examples.md docs/reference/api/examples/sales_workspace_chat_first_runtime_v2_1
git diff --check
```

## 4. Limits

- Docs / examples only.
- No backend route, DB migration, Android UI, LangGraph, real LLM, search, ContactPoint, or CRM implementation.

## 5. Next

Proceed to `task_v2_1_chat_first_runtime_trace_persistence_schema_design.md`.
