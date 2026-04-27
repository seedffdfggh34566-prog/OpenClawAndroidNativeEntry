# Handoff: V2.1 Chat-first Runtime Backend Prototype

日期：2026-04-27

## 1. Changed

- Added deterministic chat-first backend prototype routes for messages and sales-agent turn runs.
- Added persisted trace models/stores for `ConversationMessage`, `AgentRun(run_type=sales_agent_turn)`, and `ContextPack(task_type=sales_agent_turn)`.
- Product profile and lead direction chat inputs now create backend-managed Draft Review previews.
- V2.2 search/contact requests return an out-of-scope assistant response and do not mutate workspace state.

## 2. Files

- `backend/sales_workspace/chat_first.py`
- `backend/api/sales_workspace.py`
- `backend/api/main.py`
- `backend/tests/test_sales_workspace_chat_first_api.py`
- `docs/reference/api/sales-workspace-chat-first-runtime-contract.md`
- `docs/delivery/tasks/task_v2_1_chat_first_runtime_backend_prototype.md`

## 3. Validation

Passed:

```bash
backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py backend/tests/test_sales_workspace_draft_reviews_api.py backend/tests/test_sales_workspace_chat_first_api.py -q
backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_persistence_schema.py backend/tests/test_persistence.py -q
git diff --check
```

## 4. Limits

- Deterministic prototype only.
- No real LLM, formal LangGraph graph, search provider, ContactPoint, CRM, Android UI, or production hardening.
- Formal workspace writeback still happens through Draft Review apply and Sales Workspace Kernel.

## 5. Next

Proceed to `task_v2_1_android_chat_first_workspace_ui_prototype.md`.
