# Task：V3 `/lab` DB Persistence Inspection

更新时间：2026-04-30

## 1. 任务定位

- 任务名称：V3 `/lab` DB Persistence Inspection
- 当前状态：`done`
- 优先级：P0
- 任务类型：`backend + web implementation`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 2 API / Web lab / task / handoff / status`

---

## 2. 授权来源

用户在当前线程明确要求：

> PLEASE IMPLEMENT THIS PLAN: V3 `/lab` DB Persistence Inspection + Real LLM Lab Test Plan

本任务只开放 `/lab` 内部 inspection 能力和真实 Web lab 测试，不开放 `/workspace`、Android、cross-session memory、archival retrieval、Letta server、CRM/outreach、auth/tenant 或 production SaaS。

---

## 3. 任务目标

完善 Web `/lab` 为 V3 runtime / persistence inspection tool：

- 显示当前 V3 sandbox store backend。
- database store 下展示 memory transition events。
- non-database store 下明确显示 DB inspection 不可用。
- replay report 显示 replay session id。
- 真实 Web lab 测试使用 DB store + 本地真实 TokenHub LLM 配置。

---

## 4. 范围

In Scope：

- 新增只读 `GET /v3/sandbox/store`。
- 新增只读 `GET /v3/sandbox/sessions/{session_id}/memory-transitions`。
- `/lab` 新增 Store 状态和 Memory Transitions panel。
- Playwright 覆盖 DB-mode transition inspection。
- 执行 DB store + real TokenHub LLM smoke。
- 更新 task、handoff、delivery/status docs。

Out of Scope：

- 新 DB migration。
- 改变现有 session/turn/replay API response shape。
- `/workspace`。
- Android。
- cross-session / agent-scoped memory。
- archival retrieval / embedding / pgvector / compaction。
- Letta server 或完整 Letta 复现。
- CRM 生产写入、真实外部触达、联系人导出、auth/tenant、production SaaS。

---

## 5. 实际结果说明

已完成 `/lab` DB persistence inspection。

当前 `/lab` 可观察：

- 当前 store backend：`memory | json | database`。
- database store 下的 memory transition events。
- transition type、memory id、before/after status、trace id、turn id、action index。
- replay session id。

该能力用于内部 runtime / persistence 调试，不代表用户产品页、正式 CRM 或 production-ready Web SaaS 完成。

---

## 6. 已做验证

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -q`
- `cd web && npm run build`
- DB-mode Playwright：`cd web && npm run test:e2e`
- Real LLM Web lab smoke：DB store + 本地 TokenHub 配置，真实 Send turn 成功返回 assistant message，并写入 memory transition。
- `git diff --check`

安全说明：

- 未读取或打印 `backend/.env` 内容。
- 仅检查 `backend/.env` 存在且被 git ignore。
