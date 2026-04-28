# Task: V2.1 LLM Sales Agent Turn Backend Prototype

状态：done

更新时间：2026-04-28

## Objective

在现有 chat-first endpoint 中增加显式 LLM runtime mode，使 V2.1 Product Sales Agent 可以调用 Tencent TokenHub 生成追问、解释型回答或可审阅的 `WorkspacePatchDraft`。

## Scope

- 新增 `backend/runtime/sales_workspace_chat_turn_llm.py`。
- `OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=llm` 时调用 TokenHub。
- 默认 deterministic mode 行为不变。
- LLM 输出必须经过 structured validation。
- formal writeback 仍走 Draft Review 和 Sales Workspace Kernel。

## Out Of Scope

- 不接正式 LangGraph。
- 不接 search / ContactPoint / CRM。
- 不改 Android。
- 不改 DB schema。

## Outcome

LLM mode 已可通过现有 `POST /sales-workspaces/{workspace_id}/agent-runs/sales-agent-turns` 使用。

## Validation

```bash
PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_runtime.py backend/tests/test_sales_workspace_chat_first_api.py -q
git diff --check
```
