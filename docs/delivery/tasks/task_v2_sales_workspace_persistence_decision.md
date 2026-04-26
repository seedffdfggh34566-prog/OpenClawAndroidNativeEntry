# Task：V2 Sales Workspace persistence decision

更新时间：2026-04-27

## 1. 任务定位

- 任务名称：V2 Sales Workspace persistence decision
- 建议路径：`docs/delivery/tasks/task_v2_sales_workspace_persistence_decision.md`
- 当前状态：`done`
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

实际结论：

- 不开放 `task_v2_sales_workspace_backend_api_v0.md`。
- 不新增 DB schema / migration 任务。
- 下一步建议新增 contract fixture examples / state transition examples task。

---

## 7. 实际产出

- 新增 `docs/adr/ADR-007-v2-sales-workspace-persistence-decision.md`。
- 更新 `docs/adr/README.md`。
- 更新 `_active.md`，清空自动排定 implementation task。
- 新增 handoff：`docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_persistence_decision.md`。

---

## 8. 已做验证

已执行：

```bash
rg "ADR-007-v2-sales-workspace-persistence-decision.md" docs/adr docs/delivery docs/README.md
rg "不进入 SQLite|不开放 backend API|in-memory / JSON fixture|backend API implementation 继续 blocked" docs/adr/ADR-007-v2-sales-workspace-persistence-decision.md
rg "FastAPI endpoint|Alembic migration|SQLite schema change|Android UI|Runtime / LangGraph" docs/delivery/tasks/_active.md docs/delivery/tasks/task_v2_sales_workspace_persistence_decision.md docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_persistence_decision.md
git diff --check
git status --short
```

结果：

- ADR-007 已被 ADR / delivery / docs 入口引用。
- ADR-007 包含延后 API、延后 SQLite / Alembic、`in-memory / JSON fixture` 非正式 baseline、backend API implementation 继续 blocked 的结论。
- task / handoff / `_active.md` 均保留 FastAPI endpoint、Alembic migration、SQLite schema change、Android UI、Runtime / LangGraph 禁止范围。
- `git diff --check` passed。
- `git status --short` 仅包含本次 Markdown 文档变更。

---

## 9. 实际结果说明

本任务是 Markdown-only decision task。未修改代码，未实现 route，未写 migration，未接 Android / Runtime / LLM / search。
