# Task：V2 Sales Workspace persistence decision

更新时间：2026-04-27

## 1. 任务定位

- 任务名称：V2 Sales Workspace persistence decision
- 建议路径：`docs/delivery/tasks/task_v2_sales_workspace_persistence_decision.md`
- 当前状态：`queued`
- 优先级：P0

---

## 2. 任务目标

决策 Sales Workspace Kernel v0.1 是否继续使用 in-memory / JSON fixture，还是进入 SQLite / Alembic，或延后 DB persistence。

本任务是 docs / ADR-level decision，不写 migration。

---

## 3. In Scope

- 比较 in-memory / JSON fixture、SQLite / Alembic、延后 DB 三种路线。
- 明确当前阶段推荐 persistence baseline。
- 明确对 backend API、Android read-only view、Runtime integration 的影响。
- 如需要，新增 ADR 或 architecture note。

---

## 4. Out of Scope

- SQLAlchemy model implementation。
- Alembic migration。
- SQLite schema change。
- Postgres / pgvector。
- 生产部署或云存储承诺。

---

## 5. 验收标准

- 明确选择一条 persistence 路线或明确延后。
- 明确为什么该路线适合 post-kernel-v0 阶段。
- 明确 backend API v0 是否可以在无 DB 状态下推进。
- `_active.md` 根据决策更新后续队列。
- `git diff --check` 通过。

---

## 6. 下一步衔接

本任务完成后，规划层再决定是否开放：

- `task_v2_sales_workspace_backend_api_v0.md`
- 或新增 DB schema / migration 专项任务。
