# Task: V2.1 Chat-first Runtime Contract Examples

状态：planned / blocked until explicitly opened

更新时间：2026-04-27

## Objective

补齐 V2.1 chat-first Runtime contract examples，用固定 JSON examples 验证产品理解、获客方向、Draft Review 和 WorkspaceCommit 的引用链。

本任务是 docs / examples only，不实现 backend route、LangGraph graph、真实 LLM 或 Android UI。

## Scope

- 新增 `docs/reference/api/sales-workspace-chat-first-runtime-examples.md`。
- 新增 JSON examples 目录。
- 覆盖：
  - user `ConversationMessage`
  - `AgentRun(run_type = sales_agent_turn)`
  - `ContextPack(task_type = sales_agent_turn)`
  - product profile update `WorkspacePatchDraft`
  - lead direction update `WorkspacePatchDraft`
  - mixed update `WorkspacePatchDraft`
  - Draft Review accept/apply trace
  - rejected draft trace
  - V2.2 out-of-scope assistant response

## Out Of Scope

- 不新增 backend endpoint。
- 不改 Android。
- 不写 DB migration。
- 不接 LangGraph implementation。
- 不接真实 LLM。
- 不接 search / ContactPoint / CRM。

## Blocker

必须先完成 `task_v2_1_chat_first_runtime_design.md`，并由 `_active.md` 明确开放。
