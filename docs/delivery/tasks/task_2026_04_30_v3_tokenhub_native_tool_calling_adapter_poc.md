# Task：V3 TokenHub Native Tool Calling Adapter POC

更新时间：2026-04-30

## 1. 任务定位

- 任务名称：V3 TokenHub Native Tool Calling Adapter POC
- 当前状态：`done`
- 优先级：P1
- 任务类型：`backend runtime / provider adapter / lab settings`
- 是否属于 delivery package：`no`

## 2. 授权来源

用户在当前线程明确要求执行 `V3 TokenHub Native Tool Calling Adapter POC`。

## 3. 范围

In scope:

- 扩展 Tencent TokenHub client，支持 OpenAI-style `tools` / `tool_choice`。
- 解析 native `message.tool_calls`，允许 tool-call 响应没有 visible content。
- 为 V3 `/lab` 增加 native FC model allowlist 和 model policy 状态。
- 提供最小 native FC smoke helper。

Out of scope:

- 不实现 session-scoped core memory blocks。
- 不改 LangGraph memory tool loop。
- 不接 Letta server。
- 不新增 DB migration 或 memory schema。
- 不启用 CRM、outreach、contact export、auth/tenant 或 production SaaS。

## 4. 实际结果

- 新增 `TokenHubClient.complete_with_tools(...)`，保留旧 `complete(messages)` 行为。
- 新增 native FC response shape：`tool_calls`、`finish_reason`、safe `raw_message`。
- 新增 V3 native FC model policy：
  - `minimax-m2.7`
  - `deepseek-v4-flash`
  - `deepseek-v3.2`
  - `kimi-k2.6`
  - `glm-5.1`
  - `deepseek-v3.1-terminus`
- V3 `/lab` effective default model 改为 `minimax-m2.7`。
- `/v3/sandbox/runtime-config` 返回 native FC policy，不显示 secret、DB URL 原文或 store dir 原文。
- `/lab Settings` 显示 Native FC Policy。

## 5. 验证

- `backend/.venv/bin/python -m pytest backend/tests/test_tokenhub_client.py backend/tests/test_v3_sandbox_runtime.py -q`
- `backend/.venv/bin/python -m pytest backend/tests -q`
- `cd web && npm run build`
- `cd web && npm run test:e2e`
- `backend/.venv/bin/python -m backend.runtime.tokenhub_native_fc_smoke --model minimax-m2.7 --tool-choice required`
- `git diff --check`

Real TokenHub native FC smoke 结果：

- provider：`tencent_tokenhub`
- model：`minimax-m2.7`
- result：`ok`
- finish_reason：`tool_calls`
- tool_calls_present：`true`
- first_tool_name：`upsert_memory`

## 6. 后续建议

下一步建议单独开放：

- `V3 Letta-inspired Core Memory Tool Loop POC`

该后续任务可基于本次 native FC adapter 实现 session-scoped core memory blocks 和 memory tools。
