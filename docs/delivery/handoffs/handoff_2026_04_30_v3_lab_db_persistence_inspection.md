# Handoff：V3 `/lab` DB Persistence Inspection

日期：2026-04-30

## 1. 变更摘要

本次完善 `/lab` 为 V3 runtime / persistence inspection tool。

核心结果：

- Backend 新增安全的 store inspection API。
- Backend 新增 memory transition inspection API。
- `/lab` 顶部显示当前 store backend。
- `/lab` 新增 Memory Transitions panel。
- Replay report 显示 replay session id。
- Playwright 覆盖 DB-mode transition inspection。
- 真实 DB store + TokenHub LLM Web lab smoke 成功。

## 2. 文件或区域

- `backend/api/v3_sandbox.py`
- `backend/runtime/v3_sandbox/store.py`
- `backend/tests/test_v3_sandbox_runtime.py`
- `web/src/api.ts`
- `web/src/App.tsx`
- `web/src/styles.css`
- `web/tests/lab.spec.ts`
- `docs/delivery/tasks/task_2026_04_30_v3_lab_db_persistence_inspection.md`

## 3. 验证

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -q`
- `cd web && npm run build`
- DB-mode Playwright：`cd web && npm run test:e2e`
- Real LLM Web lab smoke：DB store + 本地 TokenHub 配置，真实 Send turn 成功返回 assistant message。
- `git diff --check`

## 4. 已知边界

- `/lab` 只展示 transition inspection，不做 step-by-step playback。
- Non-database store 下 transition panel 只显示不可用状态。
- 未新增 DB migration，复用现有 V3 sandbox persistence tables。
- 未实现 `/workspace`、Android、cross-session memory、archival retrieval、compaction 或 Letta server。
- 未启用 CRM 生产写入、真实外部触达、不可逆导出、auth/tenant 或 production SaaS。

## 5. 推荐下一步

建议下一步单独开放：

- `V3 workspace user prototype planning`：把内部 memory/state 观察结果转为用户可理解体验。
- 或 `V3 archival memory design`：设计跨 session / retrieval 边界。
- 或 `V3 /lab trace playback`：如调试需要，再做 action/transition 时间线播放。
