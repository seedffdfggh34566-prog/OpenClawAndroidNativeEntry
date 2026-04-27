# Task: V2.1 Chat-first Runtime Backend Prototype

状态：done

更新时间：2026-04-27

## Objective

实现 V2.1 chat-first Runtime backend prototype，让用户消息可以形成 `ConversationMessage`、`AgentRun(run_type = sales_agent_turn)`、`ContextPack(task_type = sales_agent_turn)` 与可审阅的 `WorkspacePatchDraft`。

## Required Precondition

必须先完成：

- `task_v2_1_chat_first_runtime_design.md`
- `task_v2_1_chat_first_runtime_contract_examples.md`
- `task_v2_1_chat_first_runtime_trace_persistence_schema_design.md`
- `task_v2_1_chat_first_runtime_trace_persistence_migration_v0.md`

## Initial Scope Placeholder

- backend-only prototype。
- deterministic runtime stub only。
- support product profile and lead direction patch drafts。
- persist minimal `ConversationMessage` and `AgentRun(run_type = sales_agent_turn)` trace.
- compile `ContextPack(task_type = sales_agent_turn)` from structured workspace state.
- use existing Draft Review routes for review/apply。
- keep Sales Workspace Kernel as formal writeback owner。

## Out Of Scope Until Unblocked

- 不接真实 LLM。
- 不实现正式 LangGraph graph。
- 不接 search provider。
- 不做 ContactPoint / CRM。
- 不改 Android UI。
- 不新增 production hardening。

## Recommended Next

完成后进入：

- `task_v2_1_android_chat_first_workspace_ui_prototype.md`

## Outcome

- 新增 backend chat-first trace models and stores。
- 新增 prototype routes：
  - `POST /sales-workspaces/{workspace_id}/messages`
  - `GET /sales-workspaces/{workspace_id}/messages`
  - `POST /sales-workspaces/{workspace_id}/agent-runs/sales-agent-turns`
  - `GET /sales-workspaces/{workspace_id}/agent-runs/{agent_run_id}`
- deterministic runtime stub 支持 product profile、lead direction、mixed update 和 V2.2 out-of-scope response。
- product / direction draft 通过 existing Draft Review routes 进入人工审阅；正式写回仍由 Sales Workspace Kernel apply。
- Postgres mode 下 trace rows persist 到 migration v0 tables；memory/json prototype path 使用 app-local trace store。

## Validation

```bash
backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py backend/tests/test_sales_workspace_draft_reviews_api.py backend/tests/test_sales_workspace_chat_first_api.py -q
backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_persistence_schema.py backend/tests/test_persistence.py -q
git diff --check
```
