# Task: V2.1 Chat-first Runtime Backend Prototype

状态：planned / blocked by contract examples

更新时间：2026-04-27

## Objective

实现 V2.1 chat-first Runtime backend prototype，让用户消息可以形成 `ConversationMessage`、`AgentRun(run_type = sales_agent_turn)`、`ContextPack(task_type = sales_agent_turn)` 与可审阅的 `WorkspacePatchDraft`。

## Required Precondition

必须先完成：

- `task_v2_1_chat_first_runtime_design.md`
- `task_v2_1_chat_first_runtime_contract_examples.md`

## Initial Scope Placeholder

- backend-only prototype。
- deterministic runtime stub only。
- support product profile and lead direction patch drafts。
- use existing Draft Review routes for review/apply。
- keep Sales Workspace Kernel as formal writeback owner。

## Out Of Scope Until Unblocked

- 不接真实 LLM。
- 不实现正式 LangGraph graph。
- 不接 search provider。
- 不做 ContactPoint / CRM。
- 不改 Android UI。
- 不新增 production hardening。
