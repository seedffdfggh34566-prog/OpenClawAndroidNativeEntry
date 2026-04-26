# Handoff：V2 Sales Workspace contract fixture examples

- 日期：2026-04-27
- 状态：done
- 对应任务：`docs/delivery/tasks/task_v2_sales_workspace_contract_fixture_examples.md`

---

## 1. 本次变更

补齐 Sales Workspace Kernel API contract v0 examples：

- 新增 `docs/reference/api/sales-workspace-kernel-v0-examples.md`。
- 新增 `docs/reference/api/examples/sales_workspace_kernel_v0/`。
- 新增 create workspace、patch apply、ranking board、Markdown projection、ContextPack、version conflict、validation error examples。
- 更新 `docs/reference/README.md`、`docs/README.md`、`docs/delivery/tasks/_active.md`。

---

## 2. 范围边界

本次 examples 仅用于 contract validation。

它们不是：

- runtime fixtures。
- DB fixtures。
- FastAPI implementation。
- persistence baseline。

---

## 3. 未开放范围

本次没有开放：

- FastAPI endpoint。
- SQLAlchemy ORM。
- Alembic migration。
- SQLite schema change。
- Android UI。
- Runtime / LangGraph integration。
- LLM / search provider。

---

## 4. 验证

已执行：

```bash
find docs/reference/api/examples/sales_workspace_kernel_v0 -name "*.json" -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
rg "sales-workspace-kernel-v0-examples.md|sales_workspace_kernel_v0" docs/reference docs/delivery docs/README.md
rg "workspace_version_conflict|validation_error|cand_d|ContextPack|Markdown projection" docs/reference/api/sales-workspace-kernel-v0-examples.md docs/reference/api/examples/sales_workspace_kernel_v0
rg "FastAPI endpoint|Alembic migration|SQLite schema change|Android UI|Runtime / LangGraph" docs/delivery/tasks/_active.md docs/delivery/tasks/task_v2_sales_workspace_contract_fixture_examples.md docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_contract_fixture_examples.md
git diff --check
git status --short
```

结果：上述验证均通过；本地 `jianglab` 环境没有 `python` 别名，因此 JSON 校验使用 `python3 -m json.tool`。

---

## 5. 建议下一步

不要自动继续实现。

建议由规划层决定是否：

- 继续补更多 contract examples。
- 重新讨论 backend API implementation gate。
- 重新讨论 DB schema / migration gate。
