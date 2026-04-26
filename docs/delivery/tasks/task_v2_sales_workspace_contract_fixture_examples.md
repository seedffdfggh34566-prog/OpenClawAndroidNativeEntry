# Task：V2 Sales Workspace contract fixture examples

更新时间：2026-04-27

## 1. 任务定位

- 任务名称：V2 Sales Workspace contract fixture examples
- 建议路径：`docs/delivery/tasks/task_v2_sales_workspace_contract_fixture_examples.md`
- 当前状态：`done`
- 优先级：P0

---

## 2. 任务目标

补齐 Sales Workspace Kernel API contract v0 的 fixture examples / state transition examples。

本任务只补文档和 JSON examples，不实现 API、DB、Android 或 Runtime。

---

## 3. In Scope

- 新增 `docs/reference/api/sales-workspace-kernel-v0-examples.md`。
- 新增 `docs/reference/api/examples/sales_workspace_kernel_v0/*.json`。
- 示例覆盖 workspace create、patch apply、ranking board、Markdown projection、ContextPack、version conflict、validation error。
- 更新 reference / docs / active task 入口。

---

## 4. Out of Scope

- FastAPI endpoint。
- SQLAlchemy ORM。
- Alembic migration。
- SQLite schema change。
- Android UI。
- Runtime / LangGraph integration。
- LLM / search provider。

---

## 5. 验收标准

- JSON examples 全部通过 `python3 -m json.tool`。
- examples 被 `docs/reference/README.md`、`docs/README.md`、`_active.md` 引用。
- examples 明确 `WorkspacePatch` 是唯一写入口，derived outputs 不可直接写入。
- `git diff --check` 通过。

---

## 6. 实际产出

- 新增 `docs/reference/api/sales-workspace-kernel-v0-examples.md`。
- 新增 10 个 JSON examples。
- 更新 `docs/reference/README.md`、`docs/README.md`、`docs/delivery/tasks/_active.md`。
- 新增 handoff：`docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_contract_fixture_examples.md`。

---

## 7. 已做验证

```bash
find docs/reference/api/examples/sales_workspace_kernel_v0 -name "*.json" -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
rg "sales-workspace-kernel-v0-examples.md|sales_workspace_kernel_v0" docs/reference docs/delivery docs/README.md
rg "workspace_version_conflict|validation_error|cand_d|ContextPack|Markdown projection" docs/reference/api/sales-workspace-kernel-v0-examples.md docs/reference/api/examples/sales_workspace_kernel_v0
rg "FastAPI endpoint|Alembic migration|SQLite schema change|Android UI|Runtime / LangGraph" docs/delivery/tasks/_active.md docs/delivery/tasks/task_v2_sales_workspace_contract_fixture_examples.md docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_contract_fixture_examples.md
git diff --check
git status --short
```

结果：上述验证均通过；本地 `jianglab` 环境没有 `python` 别名，因此 JSON 校验使用 `python3 -m json.tool`。
