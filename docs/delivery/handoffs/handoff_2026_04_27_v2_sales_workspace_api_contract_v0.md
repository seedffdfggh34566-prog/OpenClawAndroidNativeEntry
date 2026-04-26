# Handoff：V2 Sales Workspace API contract v0

- 日期：2026-04-27
- 状态：done
- 对应任务：`docs/delivery/tasks/task_v2_sales_workspace_api_contract_v0.md`

---

## 1. 本次变更

完成 Sales Workspace Kernel backend API contract v0：

- 新增 `docs/reference/api/sales-workspace-kernel-v0-contract.md`。
- 定义最小 V2.1 backend API surface：
  - `POST /sales-workspaces`
  - `GET /sales-workspaces/{workspace_id}`
  - `POST /sales-workspaces/{workspace_id}/patches`
  - `GET /sales-workspaces/{workspace_id}/ranking-board/current`
  - `GET /sales-workspaces/{workspace_id}/projection`
  - `POST /sales-workspaces/{workspace_id}/context-packs`
- 明确 `WorkspacePatch` 是唯一写入口。
- 明确 version conflict、validation error、not found、unsupported operation 的错误语义。
- 更新 reference / delivery / docs 入口，将 current task 切到 persistence decision。

---

## 2. 未开放范围

本次是 Markdown-only contract task，没有实现：

- FastAPI route implementation。
- SQLAlchemy ORM / Alembic migration / SQLite schema change。
- Android UI。
- Runtime / LangGraph integration。
- LLM / search provider。
- CRM / ContactPoint / 自动触达。

---

## 3. Backend API Change Check

- Formal contract affected：yes，新增 V2 Sales Workspace API contract。
- Existing V1 API contract affected：no。
- Change type：additive docs-only contract。
- Request / response models affected：
  - `SalesWorkspace`
  - `WorkspacePatch`
  - `WorkspaceOperation`
  - `WorkspaceCommit`
  - `CandidateRankingBoard`
  - Markdown projection response
  - `ContextPack`
- Implementation required now：no。
- Minimum verification：docs rg checks + `git diff --check`。

---

## 4. 验证

已执行：

```bash
rg "sales-workspace-kernel-v0-contract.md" docs/reference docs/delivery docs/README.md
rg "POST /sales-workspaces|WorkspacePatch|workspace_version_conflict|ContextPack" docs/reference/api/sales-workspace-kernel-v0-contract.md
rg "FastAPI route implementation|Alembic migration|Android UI|Runtime / LangGraph integration" docs/delivery/tasks/task_v2_sales_workspace_api_contract_v0.md docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_api_contract_v0.md
git diff --check
git status --short
```

结果：

- contract 文档已被 reference / delivery / docs 入口引用。
- contract 文档包含最小 endpoint、`WorkspacePatch`、`workspace_version_conflict`、`ContextPack`。
- task / handoff 明确 FastAPI route、Alembic migration、Android UI、Runtime / LangGraph integration 不在本任务范围。
- `git diff --check` passed。
- `git status --short` 仅包含本次 Markdown 文档变更。

---

## 5. 建议下一步

执行 `docs/delivery/tasks/task_v2_sales_workspace_persistence_decision.md`。

在 persistence decision 完成前，不开放 backend API implementation。
