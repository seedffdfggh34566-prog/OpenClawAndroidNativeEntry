# Task：V3 `/lab` Seed / Reset / Replay

更新时间：2026-04-30

## 1. 任务定位

- 任务名称：V3 `/lab` Seed / Reset / Replay
- 当前状态：`done`
- 优先级：P0
- 任务类型：`backend + web implementation`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 2 task / handoff / delivery index / status`

---

## 2. 授权来源

用户在当前线程明确要求：

> PLEASE IMPLEMENT THIS PLAN: V3 `/lab` Seed / Reset / Replay Plan

本任务只开放 V3 `/lab` 内部测试控制能力，不开放 `/workspace` 用户产品页、Android 接入、DB migration、auth/tenant、CRM/outreach 或 production Web SaaS。

---

## 3. 任务目标

为现有 V3 Web `/lab` 增加可复现测试控制：

- deterministic demo seed。
- safe reset，即创建新空 session，不删除旧 session。
- replay user turns，即从当前 session 提取 user messages 并通过真实 V3 runtime 重放。
- replay report，即使真实 LLM 不可用，也能在 UI 中观察失败状态和错误码。

目标是让开发者能稳定观察 memory、working state、customer intelligence draft、trace/actions，并用同一组用户 turns 重新跑一遍以判断 runtime 行为。

---

## 4. 范围

In Scope：

- 新增 `POST /v3/sandbox/demo-seeds`。
- 新增 `POST /v3/sandbox/sessions/{session_id}/replay`。
- 新增 replay report Pydantic 模型。
- Demo seed 第一版只支持 `sales_training_correction`。
- `/lab` 新增 `Seed demo`、`Reset session`、`Replay user turns` 控制区。
- `/lab` 展示 replay completed / failed、turn count 和 error code。
- Playwright 覆盖 seed、reset、replay report。
- 更新 task、handoff、`_active.md`、delivery README 和 V3 状态文档。

Out of Scope：

- 删除、清空或 destructive reset API。
- 前端 trace step-by-step 播放动画。
- `/workspace` 用户产品页。
- Android 接入。
- DB schema / Alembic migration。
- 正式 persistence / auth / tenant / deployment。
- CRM 生产写入、真实外部触达、联系人导出、批量 outreach。
- 将 customer intelligence draft 升级为正式 CRM 或业务建档 schema。

---

## 5. 实际结果说明

已完成 V3 `/lab` seed / reset / replay POC。

当前 `/lab` 可用于：

- 一键创建 deterministic `sales_training_correction` seeded session。
- 观察 observed、confirmed、superseded memory 状态。
- 观察 working state、customer intelligence draft、trace/actions。
- 通过 reset 创建新空 session，且不删除旧 session。
- 将当前 session 的 user messages replay 到新 session。
- 在无 LLM key 或 runtime 失败时展示 replay failure report，并保留 partial replay session。

该能力是内部开发和产品测试台能力，不代表 `/workspace`、Android、正式 persistence、MVP 或 production-ready Web SaaS 完成。

---

## 6. 已做验证

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -q`
- `cd web && npm run build`
- `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_lab_seed_replay_e2e.db OPENCLAW_BACKEND_LLM_API_KEY= backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
- `curl -sS -m 2 http://127.0.0.1:8013/health`
- `cd web && npm run test:e2e`
- `git diff --check`

环境门控说明：

- Replay 走真实 runtime；自动化 e2e 在空 LLM key 下允许 replay 失败，但要求 UI 保留可见 replay report。
- 本任务未读取或依赖 `backend/.env`。
