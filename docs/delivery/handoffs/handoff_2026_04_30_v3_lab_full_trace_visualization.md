# Handoff：V3 `/lab` Full Trace Visualization

日期：2026-04-30

## 1. 变更摘要

本次完善 `/lab` 为 V3 LangGraph workflow trace inspection tool。

核心结果：

- Backend turn API 新增 per-turn `debug_trace` options。
- V3 trace event 新增可选 `debug_trace` payload。
- Runtime 记录 LangGraph 节点 timeline、LLM prompt/raw output、repair attempts、parse/action apply/state diff。
- `/lab` Send 区域新增 Trace controls。
- Trace / Actions 面板新增 graph line、node details 和 JSON/code viewer。
- Debug trace 默认关闭；只有本轮 Send turn 显式打开时保存 prompt/raw output。

## 2. 文件或区域

- `backend/api/v3_sandbox.py`
- `backend/runtime/v3_sandbox/graph.py`
- `backend/runtime/v3_sandbox/schemas.py`
- `backend/tests/test_v3_sandbox_runtime.py`
- `web/src/api.ts`
- `web/src/App.tsx`
- `web/src/styles.css`
- `web/tests/lab.spec.ts`

## 3. 验证

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -q`
- `backend/.venv/bin/python -m pytest backend/tests -q`
- `cd web && npm run build`
- `cd web && npm run test:e2e`
- Real Web lab smoke：DB store + 本地 TokenHub 配置，开启 verbose trace 后发送一轮，确认 prompt/raw output/action results/state diff 均可见。
- `git diff --check`

## 4. 已知边界

- `/lab` full trace 是内部调试能力，不是 production observability。
- 未接 LangSmith / LangGraph Studio。
- 未新增 DB migration；DB store 通过 session snapshot 保存 debug trace。
- Normalized action / memory transition tables 不反向重建 debug trace。
- 未实现 `/workspace`、Android、cross-session memory、archival retrieval、compaction 或 Letta server。
- 未启用 CRM 生产写入、真实外部触达、不可逆导出、auth/tenant 或 production SaaS。

## 5. 推荐下一步

建议下一步单独开放：

- `V3 LangGraph Studio adapter spike`：如需评估官方 Studio。
- 或 `V3 /lab trace replay playback`：如需逐步回放 action/state diff。
- 或 `V3 workspace user prototype planning`：把已验证的 memory/state 能力转为用户可理解体验。
