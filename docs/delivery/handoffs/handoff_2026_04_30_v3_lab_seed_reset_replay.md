# Handoff：V3 `/lab` Seed / Reset / Replay

日期：2026-04-30

## 1. 变更摘要

本次实现 V3 `/lab` seed / reset / replay POC，用于稳定观察 V3 sandbox runtime 行为。

核心结果：

- Backend 新增 deterministic demo seed API。
- Backend 新增 replay API，从 source session 提取 user messages 并通过真实 runtime 生成 replay session。
- Replay 失败时返回 HTTP 200 replay report，保留 partial replay session，并暴露错误码。
- `/lab` 新增 `Seed demo`、`Reset session`、`Replay user turns` 控制区。
- Reset 仅创建新空 session，不删除、不清空旧 session。
- Playwright 覆盖 seed、reset、replay report。

## 2. 文件或区域

- `backend/api/v3_sandbox.py`
- `backend/runtime/v3_sandbox/schemas.py`
- `backend/runtime/v3_sandbox/__init__.py`
- `backend/tests/test_v3_sandbox_runtime.py`
- `web/src/api.ts`
- `web/src/App.tsx`
- `web/src/styles.css`
- `web/tests/lab.spec.ts`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`
- `docs/delivery/tasks/task_2026_04_30_v3_lab_seed_reset_replay.md`
- `docs/product/project_status.md`
- `docs/architecture/v3/web-dual-entry-prototype.md`

## 3. 验证

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -q`
- `cd web && npm run build`
- `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_lab_seed_replay_e2e.db OPENCLAW_BACKEND_LLM_API_KEY= backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
- `curl -sS -m 2 http://127.0.0.1:8013/health`
- `cd web && npm run test:e2e`
- `git diff --check`

## 4. 已知边界

- Seed 第一版只支持 `sales_training_correction`。
- Replay 是真实 runtime replay，会调用 LLM；无 LLM key 时失败是预期且可观察的结果。
- Reset 不删除 backend session。
- 未新增 DB schema / migration。
- 未接 Android。
- `/workspace` 未实现。
- 未加入 auth / tenant / production deployment。
- 未启用 CRM 生产写入、真实外部触达、不可逆导出或 production SaaS。

## 5. 推荐下一步

建议下一步单独开放：

- `V3 sandbox memory persistence design`：基于 `/lab` 可复现观察结果决定正式 persistence 边界。
- 或 `V3 /workspace prototype planning`：把 lab 中验证有效的 memory / working state 信息转为用户可理解体验。
- 或 `V3 /lab trace playback`：如需要更细粒度调试，再补 trace step-by-step 播放。
