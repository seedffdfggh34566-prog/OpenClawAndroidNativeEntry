# Task：V3 `/lab` Settings + Fullscreen Trace Inspector

更新时间：2026-04-30

## 1. 任务定位

- 任务名称：V3 `/lab` Settings + Fullscreen Trace Inspector
- 当前状态：`done`
- 优先级：P0
- 任务类型：`backend + web implementation`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 2 API / runtime config / Web lab / task / handoff / status`

## 2. 授权来源

用户在当前线程明确要求：

> PLEASE IMPLEMENT THIS PLAN: V3 `/lab` Settings + Fullscreen Trace Inspector Plan

本任务只开放 `/lab` 内部 runtime config inspection、有限进程级 overrides 和 fullscreen trace inspection，不开放 `.env` 编辑、LangSmith Studio、`/workspace`、Android、CRM/outreach、auth/tenant 或 production SaaS。

## 3. 任务目标

完善 `/lab` 调试体验：

- 将 backend status 和可修改 runtime config 集中到 Settings 面板。
- API key、DB URL、store dir 只显示安全状态，不显示原文。
- 支持当前 backend 进程内修改 LLM model、timeout、debug trace defaults、replay debug trace 和 trace size limit。
- Trace / Actions 卡片保留摘要，长内容通过 fullscreen Trace Inspector 查看。

## 4. 实际结果说明

已完成：

- `GET /v3/sandbox/runtime-config`
- `PATCH /v3/sandbox/runtime-config`
- `POST /v3/sandbox/runtime-config/reset`
- `/lab` 顶部 Settings 按钮和设置 drawer。
- `/lab` Trace / Actions 卡片 Open inspector。
- Fullscreen Trace Inspector overlay。

Runtime config overrides 只保存在当前 backend 进程内，重启后恢复环境配置。不写 `.env`。

## 5. 已做验证

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -q`
- `backend/.venv/bin/python -m pytest backend/tests -q`
- `cd web && npm run build`
- `cd web && npm run test:e2e`
- `git diff --check`
- Real Web lab smoke：Settings 修改 trace defaults，Send turn，确认 prompt/raw output/state diff 可见。

安全说明：

- 未读取或打印 `backend/.env` 内容。
- API key、DB URL、store dir 不在 API response 中返回原文。
