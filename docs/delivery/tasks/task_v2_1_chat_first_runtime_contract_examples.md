# Task: V2.1 Chat-first Runtime Contract Examples

状态：done

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

必须先完成并合并 `task_v2_1_chat_first_runtime_design.md`。

## Recommended Next

完成后进入：

- `task_v2_1_chat_first_runtime_trace_persistence_schema_design.md`

## Outcome

- 新增 `docs/reference/api/sales-workspace-chat-first-runtime-examples.md`。
- 新增 `docs/reference/api/examples/sales_workspace_chat_first_runtime_v2_1/` JSON examples。
- examples 覆盖产品理解、获客方向、mixed update、Draft Review accept/apply、rejected draft 和 V2.2 out-of-scope response。
- 本任务未实现 backend route、DB migration、Android UI、LangGraph、真实 LLM、search、ContactPoint 或 CRM。

## Validation

```bash
find docs/reference/api/examples/sales_workspace_chat_first_runtime_v2_1 -name "*.json" -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
rg "sales-workspace-chat-first-runtime-examples.md|sales_workspace_chat_first_runtime_v2_1" docs/reference docs/delivery docs/README.md
rg "ConversationMessage|AgentRun|ContextPack|WorkspacePatchDraft|draft_review_sales_turn" docs/reference/api/sales-workspace-chat-first-runtime-examples.md docs/reference/api/examples/sales_workspace_chat_first_runtime_v2_1
git diff --check
```
