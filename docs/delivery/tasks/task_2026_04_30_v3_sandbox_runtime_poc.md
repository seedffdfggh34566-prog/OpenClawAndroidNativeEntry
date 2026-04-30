# Task：V3 Sandbox Runtime POC

更新时间：2026-04-30

## 1. 任务定位

- 任务名称：V3 Sandbox Runtime POC
- 当前状态：`done`
- 优先级：P0
- 任务类型：`backend implementation`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 2 task / handoff / delivery index`

---

## 2. 授权来源

用户在当前线程明确要求：

> PLEASE IMPLEMENT THIS PLAN: V3 Sandbox Runtime POC Plan

本任务是 V3 accepted direction 后的第一个 backend-only sandbox runtime POC。该授权只开放本 POC，不开放 Web scaffold、Android UI、DB migration、CRM/outreach 或 production SaaS。

---

## 3. 任务目标

实现一个最小 backend-only V3 sandbox runtime POC，用于验证：

- Product Sales Agent 通过最小 LangGraph loop 运行。
- Agent 可以维护开放认知 memory。
- Agent 可以维护 sandbox working state。
- Agent 可以维护 customer intelligence draft。
- 用户纠错可以 supersede/reject 旧 memory，并影响后续回答。

---

## 4. 范围

In Scope：

- 新增独立 `/v3/sandbox` API。
- 新增 V3 sandbox Pydantic state/action 模型。
- 新增默认 in-memory、可选 JSON file store。
- 新增最小 LangGraph runtime loop。
- 复用现有 TokenHub client 作为真实 LLM 主路径。
- 添加 mock LLM 自动化测试，覆盖 memory 写入、假设、纠错、customer intelligence draft 和错误路径。
- 更新当前 task、handoff、`_active.md` 和 delivery README。

Out of Scope：

- DB schema / Alembic migration。
- Android UI 或 client adapter。
- Web `/lab` 或 `/workspace` scaffold。
- V2 `WorkspacePatchDraft`、Draft Review、Sales Workspace Kernel 作为 V3 默认路径。
- Letta server 接入。
- CRM 生产写入、外部触达、联系人导出、批量 outreach。
- production auth / tenant / deployment。

---

## 5. 实际结果说明

已完成 backend-only V3 sandbox runtime POC。

当前 POC 提供：

- `POST /v3/sandbox/sessions`
- `POST /v3/sandbox/sessions/{session_id}/turns`
- `GET /v3/sandbox/sessions/{session_id}`
- `GET /v3/sandbox/sessions/{session_id}/trace`

该 POC 不冻结正式 API/schema，也不代表 V3 product implementation、MVP 或 production-ready 完成。

---

## 6. 已做验证

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -q`
- `backend/.venv/bin/python -m pytest backend/tests -q`
- `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_sandbox_smoke.db backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
- `curl -sS http://127.0.0.1:8013/health`
- 真实 LLM 配置 smoke：`/v3/sandbox` 三轮 turn 均返回 200，trace 连续写入。
- `git diff --check`

环境门控说明：

- Postgres 专项测试因未设置 `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` 跳过。
- 既有 V2.1 live LLM 测试因未设置 `OPENCLAW_BACKEND_RUN_LIVE_LLM_SMOKE=1` 跳过。
