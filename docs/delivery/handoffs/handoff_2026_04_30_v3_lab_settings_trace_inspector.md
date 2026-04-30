# Handoff：V3 `/lab` Settings + Fullscreen Trace Inspector

日期：2026-04-30

## 1. 变更摘要

本次完善 `/lab` 调试体验：

- Backend 新增 V3 sandbox runtime config inspection / override API。
- Runtime config overrides 只保存在当前 backend 进程内。
- `/lab` 顶部新增 Settings 按钮和设置 drawer。
- Settings 显示 backend status、runtime config、danger/read-only 状态。
- `/lab` Trace / Actions 卡片新增 Open inspector。
- 新增 fullscreen Trace Inspector overlay，用于查看 LangGraph workflow、prompt/raw output、repair attempts、actions 和 state diff。

## 2. 文件或区域

- `backend/api/v3_sandbox.py`
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
- `git diff --check`
- Real Web lab smoke：Settings 修改 trace defaults，Send turn，确认 prompt/raw output/state diff 可见。

## 4. 已知边界

- Settings 不是 production admin console。
- 不显示或编辑 API key。
- 不显示 DB URL 或 store dir 原文。
- 不写 `.env`，不自动重启 backend。
- 不热切 store backend / DB URL / JSON store dir。
- 未接 LangSmith / LangGraph Studio。
- 未实现 `/workspace`、Android、cross-session memory、archival retrieval、compaction 或 Letta server。
- 未启用 CRM 生产写入、真实外部触达、不可逆导出、auth/tenant 或 production SaaS。

## 5. 推荐下一步

建议下一步单独开放：

- `V3 /lab trace replay playback`：如需逐步回放 action/state diff。
- 或 `V3 LangGraph Studio adapter spike`：如需评估官方 Studio。
- 或 `V3 workspace user prototype planning`：把已验证的 memory/state 能力转为用户可理解体验。
