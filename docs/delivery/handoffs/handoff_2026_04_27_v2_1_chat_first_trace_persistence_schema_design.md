# Handoff: V2.1 Chat-first Trace Persistence Schema Design

日期：2026-04-27

## 1. Changed

- Added V2.1 chat-first trace persistence schema design.
- Defined `ConversationMessage`, `AgentRun(run_type=sales_agent_turn)`, and `ContextPack(task_type=sales_agent_turn)` persistence boundaries.
- Kept Draft Review lifecycle and Sales Workspace Kernel formal writeback as separate truth layers.

## 2. Files

- `docs/architecture/runtime/v2-1-chat-first-trace-persistence-schema.md`
- `docs/architecture/runtime/README.md`
- `docs/delivery/tasks/task_v2_1_chat_first_runtime_trace_persistence_schema_design.md`

## 3. Validation

Planned validation:

```bash
rg "sales_workspace_conversation_messages|sales_workspace_agent_runs|sales_workspace_context_packs" docs/architecture/runtime/v2-1-chat-first-trace-persistence-schema.md docs/delivery/tasks
rg "queued|running|succeeded|failed|Draft Review lifecycle|Runtime / LangGraph checkpoint" docs/architecture/runtime/v2-1-chat-first-trace-persistence-schema.md
git diff --check
```

## 4. Limits

- Docs / schema design only.
- No Alembic migration, backend route, Android UI, LangGraph implementation, real LLM, search, ContactPoint, or CRM work.

## 5. Next

Proceed to `task_v2_1_chat_first_runtime_trace_persistence_migration_v0.md`.
