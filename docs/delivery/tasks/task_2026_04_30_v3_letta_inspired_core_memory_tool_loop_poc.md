# Task：V3 Letta-inspired Core Memory Tool Loop POC

更新时间：2026-04-30

## 1. 任务定位

- 任务名称：V3 Letta-inspired Core Memory Tool Loop POC
- 当前状态：`done`
- 优先级：P1
- 任务类型：`backend runtime / memory tools / persistence / web lab`
- 是否属于 delivery package：`no`

## 2. 授权来源

用户在当前线程明确要求执行 `V3 Letta-inspired Core Memory Tool Loop POC`。

## 3. 范围

In scope:

- 将 `/v3/sandbox` 默认 turn runtime 改为 native tool/function calling memory loop。
- 新增 session-scoped core memory blocks：`persona`、`human`、`product`、`sales_strategy`、`customer_intelligence`。
- 新增 core memory tools：`core_memory_append`、`memory_insert`、`memory_replace`、`send_message`。
- 新增 trace `tool_events` 和 DB normalized core memory block transition events。
- `/lab` 展示 core memory blocks、native tool events 和 core memory transitions。
- 更新测试覆盖 backend runtime、DB persistence、Web UI 和 real TokenHub smoke。

Out of scope:

- 不接 Letta server。
- 不做 archival memory、embedding、pgvector、cross-session memory 或 compaction。
- 不做 CRM、outreach、contact export、auth/tenant 或 production SaaS。
- 不改 Android 或 `/workspace`。

## 4. 实际结果

- `V3SandboxSession` 新增 `core_memory_blocks` snapshot。
- `V3SandboxTraceEvent` 新增 `tool_events`。
- 默认 `/v3/sandbox/sessions/{session_id}/turns` 使用 `TokenHubClient.complete_with_tools(...)`。
- LangGraph 节点更新为 `load_state -> compose_context -> call_agent_with_tools -> execute_tool_calls -> return_turn`。
- `send_message` 成为最终用户可见回复出口。
- 新增 Alembic revision `20260430_0006`，保存 core memory block transition events。
- 新增 `GET /v3/sandbox/sessions/{session_id}/core-memory-transitions`。
- `/lab Settings` 显示 `memory_runtime: native_tool_loop` 和 native function calling 状态。
- `/lab` 新增 Core Memory Blocks / Core Memory Transitions，并在 Trace Inspector 展示 native tool events。

## 5. 验证

- `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_core_memory_tool_loop.db backend/.venv/bin/alembic upgrade head`
- `backend/.venv/bin/python -m pytest backend/tests/test_tokenhub_client.py backend/tests/test_v3_sandbox_runtime.py -q`
- `backend/.venv/bin/python -m pytest backend/tests -q`
- `cd web && npm run build`
- `cd web && npm run test:e2e`

Real TokenHub smoke：

- `.env` presence checked without reading content.
- `backend/.env` confirmed git-ignored.
- DB-mode backend + `minimax-m2.7` completed one `/v3/sandbox` turn.
- Native tool events included `core_memory_append` and `send_message`.

## 6. 后续建议

下一步建议单独开放：

- core memory block compaction / summarization。
- archival memory design。
- `/lab` tool-loop replay comparison。
- `/workspace` 用户体验规划。
