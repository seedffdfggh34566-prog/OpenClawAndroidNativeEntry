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

- `docs/delivery/tasks/task_v2_sales_workspace_api_contract_v0.md`

### Next queued task

- `docs/delivery/tasks/task_v2_sales_workspace_persistence_decision.md`

### Recently completed

- `docs/delivery/tasks/task_v2_sales_workspace_kernel_backend_only_v0.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_post_v0_entry_sync.md`（done）

Sales Workspace Kernel backend-only v0 已完成，包含：

- Pydantic schema
- in-memory / JSON fixture store
- WorkspacePatch apply
- deterministic candidate ranking
- Markdown projection
- ContextPack compiler
- pytest

---

## 3. 当前 V2.1 后续顺序

后续任务顺序冻结为：

1. Sales Workspace Kernel backend API contract。
2. Persistence decision。
3. Backend API implementation。
4. Android read-only workspace view。
5. Runtime / LangGraph WorkspacePatchDraft integration。

当前只允许自动推进前两项 docs / decision 任务：

- `task_v2_sales_workspace_api_contract_v0.md`
- `task_v2_sales_workspace_persistence_decision.md`

---

## 4. 当前禁止自动实现

除非后续单独完成 contract / decision 并写入本文件，否则执行 agent 不应自动实现：

- FastAPI endpoint
- SQLAlchemy ORM
- Alembic migration
- SQLite schema change
- Postgres / pgvector
- Android UI
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

下一步要先冻结 API contract 与 persistence decision，避免过早进入 API、DB、Android 或 Runtime 实现。

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
10. `docs/delivery/tasks/task_v2_sales_workspace_api_contract_v0.md`
11. `docs/delivery/tasks/task_v2_sales_workspace_persistence_decision.md`
12. 本文件

---

## 7. Auto-continue allowed when

执行 agent 只可在以下条件全部满足时自动继续：

- 当前任务是 API contract docs-only task 或 persistence decision docs-only task。
- 不触碰 code、API route、DB migration、Android、runtime graph、LLM 或 search。
- 任务文件已明确状态、验收标准和停止条件。
- 完成后同步 task / handoff / docs entry。

当前没有 next queued implementation task。

---

## 8. Stop conditions

命中以下任一条件时停止并交回规划层：

- 需要改变 V2 产品方向。
- 需要实现 DB migration。
- 需要新增 API route。
- 需要接 Android。
- 需要接 LangGraph / LLM / search。
- 需要引入新外部依赖。
- API contract 与现有 `backend/sales_workspace` 对象模型冲突。
- persistence decision 需要引入生产部署、云服务或数据迁移承诺。
