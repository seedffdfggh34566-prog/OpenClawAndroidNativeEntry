# 当前活跃任务

更新时间：2026-04-27

## 1. 使用说明

本文件用于告诉开发者和 Dev Agent：

- 当前优先推进哪个正式任务
- 哪个任务只是背景材料
- 当前是否允许自动继续执行下一项任务
- 哪些内容仍禁止自动实现

---

## 2. 当前状态

### Current task

暂无自动排定。

### Next queued task

暂无自动排定。

### Recently completed

- `docs/delivery/tasks/task_v2_sales_workspace_kernel_backend_only_v0.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_post_v0_entry_sync.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_api_contract_v0.md`（done）
- `docs/reference/api/sales-workspace-kernel-v0-contract.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_persistence_decision.md`（done）
- `docs/adr/ADR-007-v2-sales-workspace-persistence-decision.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_contract_fixture_examples.md`（done）
- `docs/reference/api/sales-workspace-kernel-v0-examples.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_backend_api_prototype_v0.md`（done）
- `docs/delivery/tasks/task_v2_android_workspace_readonly_view.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_json_store_prototype.md`（done）

Sales Workspace Kernel backend-only v0 已完成，API contract v0 已冻结，persistence decision 已完成，contract fixture examples / state transition examples 已补齐，no-DB FastAPI prototype v0 已完成，Android read-only workspace demo 已完成，JSON file store prototype 已完成。

---

## 3. 当前 V2.1 后续顺序

已完成：

1. Sales Workspace Kernel backend API contract。
2. Persistence decision。
3. Contract fixture examples / state transition examples。
4. Sales Workspace Backend API prototype v0。
5. Android read-only workspace demo。
6. Sales Workspace JSON file store prototype。

当前结论：

- 不进入 SQLite / Alembic。
- 不开放 persistence-backed backend API implementation。
- `in-memory / JSON fixture` 仅作为 prototype / contract validation 支撑，不是正式 persistence baseline。
- 当前已存在 no-DB FastAPI prototype：`backend/api/sales_workspace.py`。
- 当前已存在 Android read-only workspace demo：top-level `Workspace` 页面。
- 当前已存在可选 JSON file store prototype：`OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR`。
- backend API 的 DB-backed / production persistence 版本继续 blocked。
- 当前没有 next queued implementation task。

---

## 4. 当前禁止自动实现

除非后续单独创建 task 并写入本文件，否则执行 agent 不应自动实现：

- 新增或扩展 Sales Workspace FastAPI endpoint
- SQLAlchemy ORM
- Alembic migration
- SQLite schema change
- Postgres / pgvector
- 新增或扩展 Android workspace 写入 UI
- LangGraph graph
- 真实 LLM
- 联网搜索
- 搜索 provider
- CRM pipeline
- ContactPoint
- 自动触达
- 多用户 / 权限 / 租户
- 真实 Git commit / rollback / branch
- Markdown parse-back
- embedding / semantic retrieval
- source URL fetch verification
- 复杂 candidate merge
- AnalysisReport 正式对象
- ConversationMessage / AgentRun 集成

---

## 5. 当前结论

V2 已从“对话式专属销售 agent prototype”进一步收敛为：

> **workspace-native sales agent / 中小企业专属销售工作区 Agent。**

Sales Workspace Kernel 是 V2 主架构。

LangGraph 后续只作为 runtime execution layer。

backend-only v0 已证明：

```text
创建 workspace
-> 添加产品理解
-> 添加获客方向
-> 添加两轮候选客户研究结果
-> 第二轮新候选超过第一轮旧候选
-> 生成 ranking delta
-> 渲染 Markdown workspace
-> 编译 ContextPack
```

API contract v0 已冻结：

- `docs/reference/api/sales-workspace-kernel-v0-contract.md`

Persistence decision 已冻结：

- `docs/adr/ADR-007-v2-sales-workspace-persistence-decision.md`

Contract examples 已补齐：

- `docs/reference/api/sales-workspace-kernel-v0-examples.md`
- `docs/reference/api/examples/sales_workspace_kernel_v0/`

Sales Workspace Backend API prototype v0 已完成：

- `backend/api/sales_workspace.py`
- `backend/tests/test_sales_workspace_api.py`
- `docs/delivery/tasks/task_v2_sales_workspace_backend_api_prototype_v0.md`

Android read-only workspace demo 已完成：

- `scripts/seed_sales_workspace_demo.py`
- Android top-level `Workspace` 页面
- `docs/delivery/tasks/task_v2_android_workspace_readonly_view.md`

Sales Workspace JSON file store prototype 已完成：

- `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR`
- `backend/sales_workspace/store.py`
- `docs/delivery/tasks/task_v2_sales_workspace_json_store_prototype.md`

---

## 6. 当前执行入口

优先阅读：

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/product/overview.md`
4. `docs/product/prd/ai_sales_assistant_v2_prd.md`
5. `docs/architecture/workspace/workspace-object-model.md`
6. `docs/architecture/workspace/sales-workspace-kernel.md`
7. `docs/architecture/workspace/workspace-kernel-v0-scope.md`
8. `docs/architecture/workspace/markdown-projection.md`
9. `docs/architecture/workspace/context-pack-compiler.md`
10. `docs/reference/api/sales-workspace-kernel-v0-contract.md`
11. `docs/reference/api/sales-workspace-kernel-v0-examples.md`
12. `docs/adr/ADR-007-v2-sales-workspace-persistence-decision.md`
13. `docs/delivery/tasks/task_v2_sales_workspace_backend_api_prototype_v0.md`
14. `docs/delivery/tasks/task_v2_android_workspace_readonly_view.md`
15. `docs/delivery/tasks/task_v2_sales_workspace_json_store_prototype.md`
16. 本文件

---

## 7. Auto-continue allowed when

当前没有 next queued task，因此执行 agent 不应自动继续实现或规划新任务。

---

## 8. Stop conditions

命中以下任一条件时停止并交回规划层：

- 需要改变 V2 产品方向。
- 需要实现 DB migration。
- 需要新增或扩展 API route。
- 需要新增 Android write path 或复杂交互。
- 需要接 LangGraph / LLM / search。
- 需要引入新外部依赖。
- 需要开放 persistence-backed backend API implementation。
