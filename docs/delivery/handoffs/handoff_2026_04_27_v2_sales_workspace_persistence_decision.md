# Handoff：V2 Sales Workspace persistence decision

- 日期：2026-04-27
- 状态：done
- 对应任务：`docs/delivery/tasks/task_v2_sales_workspace_persistence_decision.md`

---

## 1. 本次变更

完成 Sales Workspace persistence decision：

- 新增 `docs/adr/ADR-007-v2-sales-workspace-persistence-decision.md`。
- 更新 `docs/adr/README.md`。
- 更新 `docs/README.md` 和 `_active.md`。
- 将 `task_v2_sales_workspace_persistence_decision.md` 标记为 done。

---

## 2. 决策结论

当前采用：

> **延后 backend API implementation；不进入 SQLite / Alembic；不开放 API route。**

同时明确：

- `in-memory / JSON fixture` 仅作为 prototype / contract validation 支撑。
- `in-memory / JSON fixture` 不是正式 persistence baseline。
- backend API implementation 继续 blocked。
- 下一步应先做 contract fixture examples / state transition examples。

---

## 3. Backend DB Risk Check

- DB risk category：storage baseline decision, docs-only。
- Schema files changed：no。
- Migration files changed：no。
- SQLite / Postgres / pgvector involved：no implementation involved。
- Dedicated follow-up required：yes，若未来仍需真实持久化，必须单独创建 DB schema / migration task。
- Validation：docs rg checks + `git diff --check`。

---

## 4. 未开放范围

本次没有开放：

- FastAPI endpoint。
- SQLAlchemy ORM。
- Alembic migration。
- SQLite schema change。
- Postgres / pgvector。
- Android UI。
- Runtime / LangGraph integration。
- LLM / search provider。

---

## 5. 验证

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

## 6. 建议下一步

不要自动继续实现。

建议由规划层新增：

- contract fixture examples / state transition examples task。
