# Task：V3 Sandbox Memory Persistence

更新时间：2026-04-30

## 1. 任务定位

- 任务名称：V3 Sandbox Memory Persistence
- 当前状态：`done`
- 优先级：P0
- 任务类型：`backend implementation`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 3 backend persistence / task / handoff / architecture / status`

---

## 2. 授权来源

用户在当前线程明确要求：

> PLEASE IMPLEMENT THIS PLAN: V3 Sandbox Memory Persistence Implementation Plan

本任务只开放 V3 sandbox opt-in DB persistence，不开放 `/workspace`、Android、agent-scoped memory、archival retrieval、Letta server、CRM/outreach、auth/tenant 或 production SaaS。

---

## 3. 任务目标

实现 V3 sandbox 的 opt-in DB persistence：

- 默认仍保持 in-memory 行为。
- `OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND=database` 时写入 SQLAlchemy / Alembic 管理的数据库。
- 使用 session-scoped Snapshot + Event。
- 保存 session snapshot、messages、trace/action events、current memory items 和 memory transition events。
- 保持现有 `/v3/sandbox` public API response shape 不变。

---

## 4. 范围

In Scope：

- 新增 V3 sandbox DB store。
- 新增配置 `OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND`。
- 新增 Alembic migration 和 SQLAlchemy models。
- 新增 DB store round-trip、restart persistence、action/memory transition、config precedence、DB-mode API/replay tests。
- 新增 architecture doc、task、handoff，并同步 delivery / status docs。

Out of Scope：

- 默认启用 DB store。
- 移除 JSON store。
- cross-session / agent-scoped memory。
- archival memory / retrieval / embedding / pgvector。
- compaction。
- LangGraph checkpoint 主存。
- Letta server 或完整 Letta 复现。
- formal CRM / customer intelligence schema。
- `/workspace`、Android、auth/tenant、production SaaS。

---

## 5. 实际结果说明

已完成 opt-in V3 sandbox DB persistence。

当前可通过：

```text
OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND=database
```

让 `/v3/sandbox` 使用 DB store。未配置时仍按原行为使用 in-memory；配置 `OPENCLAW_BACKEND_V3_SANDBOX_STORE_DIR` 时仍支持 JSON store。

该实现用于 V3 sandbox POC state 的持久化和调试，不代表正式产品对象、CRM、MVP 或 production-ready persistence 完成。

---

## 6. 已做验证

- `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_memory_persistence.db backend/.venv/bin/python -m alembic upgrade head`
- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -q`
- `backend/.venv/bin/python -m pytest backend/tests -q`
- `cd web && npm run build`
- `git diff --check`
