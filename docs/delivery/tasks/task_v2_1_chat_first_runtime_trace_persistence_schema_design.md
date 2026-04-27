# Task: V2.1 Chat-first Runtime Trace Persistence Schema Design

状态：done

更新时间：2026-04-27

## Objective

设计 V2.1 chat-first product experience 所需的最小 trace persistence schema，支撑 `ConversationMessage`、`AgentRun(run_type = sales_agent_turn)`、`ContextPack(task_type = sales_agent_turn)` 与 Draft Review / WorkspaceCommit 的可追踪关系。

本任务是 docs / schema design only，不写 Alembic migration，不改 backend code，不改 Android。

## Required Precondition

- `task_v2_1_chat_first_runtime_contract_examples.md`

## Scope

- 更新或新增架构文档，定义最小表或等价 persisted objects：
  - `sales_workspace_conversation_messages`
  - `sales_workspace_agent_runs`
  - optional `sales_workspace_context_packs` 或 `context_pack_json` snapshot strategy
- 明确 `input_refs` / `output_refs` 如何引用：
  - user message
  - assistant message
  - ContextPack
  - WorkspacePatchDraftReview
  - WorkspacePatch
  - WorkspaceCommit
  - changed `ProductProfileRevision` / `LeadDirectionVersion`
- 明确 JSONB payload snapshots 与 relational fields 的边界。
- 明确 lifecycle 仍只使用 `queued`、`running`、`succeeded`、`failed`。
- 明确 Draft Review lifecycle 不被 AgentRun status 替代。

## Out Of Scope

- 不写 Alembic migration。
- 不改 SQLAlchemy model。
- 不新增 backend route。
- 不实现 runtime。
- 不改 Android。
- 不接真实 LLM / LangGraph / search / ContactPoint / CRM。

## Acceptance Criteria

- Schema design 明确 chat-first trace 可以长期 audit。
- 不把 Runtime / LangGraph checkpoint 当成业务主存。
- 不改变 Sales Workspace Kernel formal writeback owner。
- 为下一项 migration task 提供明确表、字段、索引和 JSONB 策略。

## Recommended Next

- `task_v2_1_chat_first_runtime_trace_persistence_migration_v0.md`

## Outcome

- 新增 `docs/architecture/runtime/v2-1-chat-first-trace-persistence-schema.md`。
- 明确最小 persisted objects：
  - `sales_workspace_conversation_messages`
  - `sales_workspace_agent_runs`
  - `sales_workspace_context_packs`
- 明确 `input_refs` / `output_refs` 的 audit ref 策略。
- 明确 AgentRun lifecycle 不替代 Draft Review lifecycle。
- 明确 Runtime / LangGraph checkpoint 不作为业务主存。

## Validation

```bash
rg "sales_workspace_conversation_messages|sales_workspace_agent_runs|sales_workspace_context_packs" docs/architecture/runtime/v2-1-chat-first-trace-persistence-schema.md docs/delivery/tasks
rg "queued|running|succeeded|failed|Draft Review lifecycle|Runtime / LangGraph checkpoint" docs/architecture/runtime/v2-1-chat-first-trace-persistence-schema.md
git diff --check
```
