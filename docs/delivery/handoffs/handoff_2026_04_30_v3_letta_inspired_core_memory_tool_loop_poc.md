# Handoff：V3 Letta-inspired Core Memory Tool Loop POC

日期：2026-04-30

## 1. 变更摘要

本次把 V3 sandbox 默认 runtime 推进为 Letta-inspired native tool loop：

- session snapshot 新增 core memory blocks。
- LangGraph 默认 turn path 改为 native `tools/tool_calls` round-trip。
- memory tools 支持 append、insert、replace 和 `send_message`。
- trace 新增 `tool_events`，DB store 新增 normalized core memory block transition events。
- `/lab` 可观察 core memory blocks、tool events、core transitions 和 native tool-loop trace。

## 2. 文件或区域

- `backend/runtime/v3_sandbox/`
- `backend/runtime/llm_client.py`
- `backend/api/v3_sandbox.py`
- `backend/api/models.py`
- `backend/alembic/versions/20260430_0006_v3_sandbox_core_memory_block_events.py`
- `web/src/api.ts`
- `web/src/App.tsx`
- `web/src/styles.css`
- `backend/tests/test_v3_sandbox_runtime.py`
- `web/tests/lab.spec.ts`

## 3. 验证

- `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_core_memory_tool_loop.db backend/.venv/bin/alembic upgrade head`
- `backend/.venv/bin/python -m pytest backend/tests/test_tokenhub_client.py backend/tests/test_v3_sandbox_runtime.py -q`
- `backend/.venv/bin/python -m pytest backend/tests -q`
- `cd web && npm run build`
- `cd web && npm run test:e2e`

Real TokenHub smoke 成功：

- provider：`tencent_tokenhub`
- model：`minimax-m2.7`
- tool events：`core_memory_append:applied`、`send_message:applied`
- core product memory 写入成功。

## 4. 已知边界

- Core memory 仍是 session-scoped，不是跨 session 长期记忆。
- 没有 Letta server、archival memory、embedding、pgvector 或 compaction。
- `MemoryItem` legacy 面板保留，但默认 runtime 主写入面已转向 `core_memory_blocks`。
- Customer intelligence 仍是 draft/sandbox，不是正式 CRM schema。
- 未开放外部触达、联系人导出、auth/tenant 或 production SaaS。
- API key、Authorization header、DB URL 原文和 store dir 原文仍不得显示或记录。

## 5. 推荐下一步

建议下一步从以下方向择一单独开 task：

- core memory compaction / block limit 管理。
- archival memory design。
- `/lab` tool-loop replay diff。
- `/workspace` 用户 prototype planning。
