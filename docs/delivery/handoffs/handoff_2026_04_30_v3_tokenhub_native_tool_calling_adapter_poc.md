# Handoff：V3 TokenHub Native Tool Calling Adapter POC

日期：2026-04-30

## 1. 变更摘要

本次打通 V3 native Function Calling 前置能力：

- `TokenHubClient` 新增 `complete_with_tools(...)`。
- 支持发送 `tools` / `tool_choice` 和 per-model request policy。
- 支持解析 OpenAI-style `message.tool_calls`。
- V3 `/lab` runtime config 默认模型改为 `minimax-m2.7`。
- `/lab Settings` 增加 Native FC Policy 展示。
- 新增安全 native FC smoke helper。

## 2. 文件或区域

- `backend/runtime/llm_client.py`
- `backend/runtime/tokenhub_native_fc.py`
- `backend/runtime/tokenhub_native_fc_smoke.py`
- `backend/api/v3_sandbox.py`
- `web/src/api.ts`
- `web/src/App.tsx`
- `web/src/styles.css`
- `backend/tests/test_tokenhub_client.py`
- `backend/tests/test_v3_sandbox_runtime.py`
- `web/tests/lab.spec.ts`

## 3. 验证

- `backend/.venv/bin/python -m pytest backend/tests/test_tokenhub_client.py backend/tests/test_v3_sandbox_runtime.py -q`
- `backend/.venv/bin/python -m pytest backend/tests -q`
- `cd web && npm run build`
- `cd web && npm run test:e2e`
- `backend/.venv/bin/python -m backend.runtime.tokenhub_native_fc_smoke --model minimax-m2.7 --tool-choice required`
- `git diff --check`

Real TokenHub smoke 确认 `minimax-m2.7` 返回 native `tool_calls`，首个工具名为 `upsert_memory`。

## 4. 已知边界

- 未实现 memory blocks。
- 未实现 LangGraph memory tool loop。
- 未接 Letta server。
- 未新增 DB migration。
- 未测试 Token Plan `/plan/v3` endpoint。
- JSON-simulated tool calls 仅保留为后续 fallback 方向，本任务未接入主路径。
- API key、Authorization header、DB URL 原文和 store dir 原文仍不得显示或记录。

## 5. 推荐下一步

建议下一步开放：

- `V3 Letta-inspired Core Memory Tool Loop POC`

该任务应在 native FC adapter 之上实现 session-scoped core memory blocks、memory tools、tool result round-trip 和 `/lab` 可观察性。
