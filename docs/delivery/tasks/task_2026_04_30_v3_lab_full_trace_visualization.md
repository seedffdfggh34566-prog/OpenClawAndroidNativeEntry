# Task：V3 `/lab` Full Trace Visualization

更新时间：2026-04-30

## 1. 任务定位

- 任务名称：V3 `/lab` Full Trace Visualization
- 当前状态：`done`
- 优先级：P0
- 任务类型：`backend + web implementation`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 2 API / runtime trace / Web lab / task / handoff / status`

## 2. 授权来源

用户在当前线程明确要求：

> PLEASE IMPLEMENT THIS PLAN: V3 `/lab` 原生完整 Trace 可视化计划

本任务只开放 `/lab` 内部 LangGraph workflow trace inspection，不开放 LangSmith Studio 接入、`/workspace`、Android、CRM/outreach、auth/tenant 或 production SaaS。

## 3. 任务目标

完善 `/lab` 为 V3 runtime trace inspection tool：

- 按 Send turn 单轮开启 verbose debug trace。
- 展示 LangGraph 节点链路。
- 展示提交给 LLM 的 prompt/messages。
- 展示 LLM raw output 和 repair attempts。
- 展示 parsed output、action apply results 和 state diff。

## 4. 范围

In Scope：

- 扩展 `/v3/sandbox/sessions/{session_id}/turns` request，新增可选 `debug_trace`。
- `V3SandboxTraceEvent` 新增可选 `debug_trace` payload。
- V3 LangGraph runtime 记录 `load_state -> call_llm -> parse_actions -> apply_actions -> return_turn` structured debug events。
- `/lab` 新增 Trace controls 和 workflow timeline。
- Playwright 覆盖 verbose trace UI。
- 后端测试覆盖 opt-in、prompt/raw output、repair、parse failure、DB round-trip。

Out of Scope：

- LangSmith / LangGraph Studio adapter。
- 新 DB migration。
- 修改 normalized DB event tables。
- `/workspace`。
- Android。
- cross-session / archival memory。
- CRM 生产写入、真实外部触达、联系人导出、auth/tenant、production SaaS。

## 5. 实际结果说明

已完成 `/lab` 原生完整 trace 可视化。

当前 `/lab` 可按单轮 Send turn 打开：

- verbose trace。
- include prompt。
- include raw LLM output。
- include state diff。

Trace / Actions 面板可观察：

- graph diagram。
- node status / duration。
- LLM prompt / raw output。
- repair attempts。
- validated parsed output。
- action apply results。
- state diff。

默认未开启时不保存 prompt/raw output。

## 6. 已做验证

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -q`
- `backend/.venv/bin/python -m pytest backend/tests -q`
- `cd web && npm run build`
- `cd web && npm run test:e2e`
- Real Web lab smoke：DB store + 本地 TokenHub 配置，开启 verbose trace 后发送一轮，确认 prompt/raw output/action results/state diff 均可见。
- `git diff --check`

安全说明：

- 未读取或打印 `backend/.env` 内容。
- prompt/raw output 仅在 per-turn debug option 打开时记录。
