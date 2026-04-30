# Handoff：V3 Sandbox Memory Persistence

日期：2026-04-30

## 1. 变更摘要

本次实现 V3 sandbox opt-in DB persistence。

核心结果：

- 新增配置 `OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND`，支持 `memory | json | database`。
- 默认行为保持 in-memory；现有 JSON store 保留。
- 新增 DB-backed V3 sandbox store。
- 新增 V3 sandbox persistence migration 和 SQLAlchemy models。
- 保存完整 session snapshot，并同步 normalized messages、trace events、action events、memory items、memory transition events。
- Replay partial failure 会保存 partial replay session 和 failed trace。

## 2. 文件或区域

- `backend/api/config.py`
- `backend/api/models.py`
- `backend/api/v3_sandbox.py`
- `backend/runtime/v3_sandbox/store.py`
- `backend/runtime/v3_sandbox/__init__.py`
- `backend/alembic/versions/20260430_0005_v3_sandbox_memory_persistence.py`
- `backend/tests/test_v3_sandbox_runtime.py`
- `docs/architecture/v3/sandbox-memory-persistence.md`
- `docs/delivery/tasks/task_2026_04_30_v3_sandbox_memory_persistence.md`

## 3. 验证

- `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_memory_persistence.db backend/.venv/bin/python -m alembic upgrade head`
- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -q`
- `backend/.venv/bin/python -m pytest backend/tests -q`
- `cd web && npm run build`
- `git diff --check`

## 4. 已知边界

- DB store 是 opt-in，不是默认路径。
- 第一版只做 session-scoped persistence。
- Normalized rows 是 audit / debug / query evidence；API 仍从 session snapshot round-trip。
- 未实现 cross-session memory、agent identity、archival retrieval、embedding、pgvector 或 compaction。
- 未接 Letta server，也未完整复现 Letta。
- 未接 Android 或 `/workspace`。
- 未启用 CRM 生产写入、真实外部触达、不可逆导出、auth/tenant 或 production SaaS。

## 5. 推荐下一步

建议下一步单独开放：

- `V3 /lab DB persistence inspection`：在 `/lab` 中展示 transition events 或 store backend 状态。
- 或 `V3 workspace user prototype planning`：把稳定后的 sandbox memory/state 转为用户可理解体验。
- 或 `V3 archival memory design`：在 session-scoped persistence 基础上设计跨 session / retrieval 边界。
