# Task：V3 Web `/lab` Scaffold

更新时间：2026-04-30

## 1. 任务定位

- 任务名称：V3 Web `/lab` Scaffold
- 当前状态：`done`
- 优先级：P0
- 任务类型：`web implementation`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 2 task / handoff / delivery index / status`

---

## 2. 授权来源

用户在当前线程明确要求：

> PLEASE IMPLEMENT THIS PLAN: V3 Web `/lab` Scaffold Plan

本任务只开放 V3 `/lab` scaffold，不开放 `/workspace` 用户产品页、Android 接入、DB migration、auth/tenant、CRM/outreach 或 production Web SaaS。

---

## 3. 任务目标

建立独立 `web/` 工程，实现 V3 Sales Agent Lab 第一版，用于观察和验证 backend `/v3/sandbox` runtime：

- session 创建和当前 session 状态。
- turn 输入。
- messages。
- memory。
- sandbox working state。
- customer intelligence draft。
- trace / actions。
- backend / LLM 错误码。

---

## 4. 范围

In Scope：

- 新增 Vite + React + TypeScript `web/` 工程。
- 新增 `/lab` 页面。
- 新增 typed `/v3/sandbox` API client。
- 新增 Vite dev proxy：`/api/* -> http://127.0.0.1:8013/*`。
- 新增 Playwright e2e。
- 更新 task、handoff、`_active.md`、delivery README 和 V3 Web 状态文档。

Out of Scope：

- `/workspace` 用户产品页。
- 前端 mock mode。
- Web auth / tenant / production deployment。
- Android 接入。
- DB schema / migration。
- CRM/outreach/contact/export。
- 正式设计系统或 UI component library。

---

## 5. 实际结果说明

已完成 V3 `/lab` scaffold。当前页面连接真实 backend `/v3/sandbox`，没有 mock mode。

当前 `/lab` 可用于：

- 创建 sandbox session。
- 提交一轮 turn。
- 查看 message timeline。
- 查看 memory 状态。
- 查看 working state。
- 查看 customer intelligence draft。
- 查看 trace/action/runtime metadata。
- 查看 `llm_runtime_unavailable`、`llm_structured_output_invalid` 等真实错误码。

该 scaffold 不代表 `/workspace`、production Web SaaS、MVP 或完整 V3 product implementation 完成。

---

## 6. 已做验证

- `cd web && npm install`
- `cd web && npm run build`
- `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_lab_e2e.db OPENCLAW_BACKEND_LLM_API_KEY= backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
- `cd web && npx playwright install chromium`
- `cd web && npm run test:e2e`
- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -q`
- `git diff --check`
