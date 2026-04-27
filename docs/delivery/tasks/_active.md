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

暂无 implementation task 自动开放。

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
- `docs/delivery/tasks/task_v2_sales_workspace_runtime_patchdraft_prototype.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_patchdraft_review_gate_prototype.md`（done）
- `docs/delivery/tasks/task_v2_android_patchdraft_review_ui_prototype.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_prototype_demo_runbook.md`（done）
- `docs/delivery/tasks/task_v2_post_demo_next_phase_decision.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_contract.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_routes_prototype.md`（done）
- `docs/delivery/tasks/task_v2_android_draft_review_id_flow_prototype.md`（done）
- `docs/delivery/tasks/task_v2_post_review_id_flow_persistence_decision_refresh.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_persistence_baseline_design.md`（done）
- `docs/delivery/tasks/task_v2_postgres_dev_environment_baseline.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_persistence_schema_design.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_persistence_schema.md`（done / folded）
- `docs/delivery/tasks/task_v2_sales_workspace_persistence_migration_v0.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_repository_layer_v0.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_api_postgres_store_v0.md`（done）
- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_persistence_v0.md`（done）
- `docs/delivery/tasks/task_v2_1_completion_closeout.md`（done）

Sales Workspace Kernel backend-only v0 已完成，API contract v0 已冻结，persistence decision 已完成，contract fixture examples / state transition examples 已补齐，no-DB FastAPI prototype v0 已完成，Android read-only workspace demo 已完成，JSON file store prototype 已完成，Runtime PatchDraft prototype 已完成，PatchDraft review gate prototype 已完成，Android PatchDraft review UI prototype 已完成，V2 prototype demo runbook 已完成，post-demo 下一阶段决策已完成，Draft review contract 已完成，Draft review routes prototype 已完成，Android Draft Review ID flow prototype 已完成，post-review-id-flow persistence decision refresh 已完成，persistence baseline design 已完成，Postgres dev environment baseline 已完成，persistence schema design 已完成，persistence migration v0 已完成，repository layer v0 已完成，API Postgres store v0 已完成，Draft Review persistence v0 已完成，V2.1 completion closeout 已完成。

---

## 3. 当前 V2.1 后续顺序

已完成：

1. Sales Workspace Kernel backend API contract。
2. Persistence decision。
3. Contract fixture examples / state transition examples。
4. Sales Workspace Backend API prototype v0。
5. Android read-only workspace demo。
6. Sales Workspace JSON file store prototype。
7. Runtime PatchDraft prototype。
8. PatchDraft review gate prototype。
9. Android PatchDraft review UI prototype。
10. Prototype demo runbook。
11. Post-demo next phase decision。
12. Draft review contract。
13. Draft review routes prototype。
14. Android Draft Review ID flow prototype。
15. Post Review-ID Flow persistence decision refresh。
16. Sales Workspace persistence baseline design。
17. Postgres dev environment baseline。
18. Sales Workspace persistence schema design。
19. Sales Workspace persistence migration v0。
20. Sales Workspace repository layer v0。
21. Sales Workspace API Postgres store v0。
22. Sales Workspace Draft Review persistence v0。
23. V2.1 completion closeout。

当前结论：

- V2 MVP persistence baseline 采用 Postgres / Alembic。
- SQLite 不作为 V2 Sales Workspace runtime fallback。
- 不开放 production hardening 或新增 API surface。
- `in-memory / JSON fixture` 与 JSON file store 仅作为 prototype / contract validation / demo continuity 支撑，不是正式 persistence baseline。
- 当前没有自动开放任务，不自动进入 Android 或 Runtime。
- 当前已存在 no-DB FastAPI prototype：`backend/api/sales_workspace.py`。
- 当前已存在 Android read-only workspace demo：top-level `Workspace` 页面。
- 当前已存在可选 JSON file store prototype：`OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR`。
- 当前已存在 deterministic Runtime PatchDraft prototype：`task_v2_sales_workspace_runtime_patchdraft_prototype.md`。
- 当前已存在 PatchDraft review gate prototype：`task_v2_sales_workspace_patchdraft_review_gate_prototype.md`。
- 当前已存在 Android PatchDraft review UI prototype：`task_v2_android_patchdraft_review_ui_prototype.md`。
- 当前已存在 V2 prototype demo runbook：`docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`。
- 当前已完成 clean demo verification。
- Draft review contract 已完成：`docs/reference/api/sales-workspace-draft-review-contract.md`。
- Draft review routes prototype 已完成：`docs/delivery/tasks/task_v2_sales_workspace_draft_review_routes_prototype.md`。
- Android Draft Review ID flow prototype 已完成：`docs/delivery/tasks/task_v2_android_draft_review_id_flow_prototype.md`。
- Post Review-ID Flow persistence decision refresh 已完成：`docs/delivery/tasks/task_v2_post_review_id_flow_persistence_decision_refresh.md`。
- Sales Workspace persistence baseline design 已完成：`docs/architecture/workspace/sales-workspace-persistence-baseline.md`。
- Postgres dev environment baseline 已完成：`docs/delivery/tasks/task_v2_postgres_dev_environment_baseline.md`。
- Sales Workspace persistence schema design 已完成：`docs/architecture/workspace/sales-workspace-persistence-schema.md`。
- Sales Workspace persistence migration v0 已完成：`docs/delivery/tasks/task_v2_sales_workspace_persistence_migration_v0.md`。
- Sales Workspace repository layer v0 已完成：`docs/delivery/tasks/task_v2_sales_workspace_repository_layer_v0.md`。
- Sales Workspace API Postgres store v0 已完成：`docs/delivery/tasks/task_v2_sales_workspace_api_postgres_store_v0.md`。
- Sales Workspace Draft Review persistence v0 已完成：`docs/delivery/tasks/task_v2_sales_workspace_draft_review_persistence_v0.md`。
- V2.1 completion closeout 已完成：`docs/delivery/tasks/task_v2_1_completion_closeout.md`。
- production hardening、history read API 和 DB reconstruction hardening 继续 blocked。
- 当前没有 next queued implementation task。

---

## 4. 当前禁止自动实现

除非后续单独创建 task 并写入本文件，否则执行 agent 不应自动实现：

- 新增或扩展 Sales Workspace FastAPI endpoint
- SQLAlchemy ORM
- Alembic migration
- SQLite schema change
- Postgres runtime cutover / pgvector
- 新增或扩展 Android workspace 写入 UI
- 正式 LangGraph graph
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

Runtime PatchDraft prototype 已完成：

- `docs/delivery/tasks/task_v2_sales_workspace_runtime_patchdraft_prototype.md`

PatchDraft review gate prototype 已完成：

- `docs/delivery/tasks/task_v2_sales_workspace_patchdraft_review_gate_prototype.md`

Android PatchDraft review UI prototype 已完成：

- `docs/delivery/tasks/task_v2_android_patchdraft_review_ui_prototype.md`

V2 Sales Workspace prototype demo runbook 已完成：

- `docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`
- `docs/delivery/tasks/task_v2_sales_workspace_prototype_demo_runbook.md`

Post-demo next phase decision 已完成：

- `docs/delivery/tasks/task_v2_post_demo_next_phase_decision.md`
- 推荐下一阶段：`docs/delivery/tasks/task_v2_sales_workspace_draft_review_contract.md`

Draft review contract 已完成：

- `docs/reference/api/sales-workspace-draft-review-contract.md`
- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_contract.md`

Draft review routes prototype 已完成：

- `backend/sales_workspace/draft_reviews.py`
- `backend/tests/test_sales_workspace_draft_reviews_api.py`
- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_routes_prototype.md`

Android Draft Review ID flow prototype 已完成：

- `docs/delivery/tasks/task_v2_android_draft_review_id_flow_prototype.md`

Post Review-ID Flow persistence decision refresh 已完成：

- `docs/delivery/tasks/task_v2_post_review_id_flow_persistence_decision_refresh.md`

Sales Workspace persistence baseline design 已完成：

- `docs/delivery/tasks/task_v2_sales_workspace_persistence_baseline_design.md`
- `docs/architecture/workspace/sales-workspace-persistence-baseline.md`

Sales Workspace persistence schema design 已完成：

- `docs/delivery/tasks/task_v2_sales_workspace_persistence_schema_design.md`
- `docs/architecture/workspace/sales-workspace-persistence-schema.md`

Sales Workspace persistence migration v0 已完成：

- `docs/delivery/tasks/task_v2_sales_workspace_persistence_migration_v0.md`

Sales Workspace repository layer v0 已完成：

- `docs/delivery/tasks/task_v2_sales_workspace_repository_layer_v0.md`

Sales Workspace API Postgres store v0 已完成：

- `docs/delivery/tasks/task_v2_sales_workspace_api_postgres_store_v0.md`

Sales Workspace Draft Review persistence v0 已完成：

- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_persistence_v0.md`

V2.1 completion closeout 已完成：

- `docs/delivery/tasks/task_v2_1_completion_closeout.md`

当前自动排定任务：

- 暂无。

后续 planned / blocked：

- `docs/delivery/tasks/task_v2_2_runtime_langgraph_design.md`
- `docs/delivery/tasks/task_v2_2_android_review_history_planning.md`
- `docs/delivery/tasks/task_v2_2_search_evidence_boundary_design.md`
- `docs/delivery/tasks/task_v2_runtime_langgraph_design.md`
- `docs/delivery/tasks/task_v2_android_review_history_view.md`

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
16. `docs/delivery/tasks/task_v2_sales_workspace_runtime_patchdraft_prototype.md`
17. `docs/delivery/tasks/task_v2_sales_workspace_patchdraft_review_gate_prototype.md`
18. `docs/delivery/tasks/task_v2_android_patchdraft_review_ui_prototype.md`
19. `docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`
20. `docs/delivery/tasks/task_v2_post_demo_next_phase_decision.md`
21. `docs/reference/api/sales-workspace-draft-review-contract.md`
22. `docs/delivery/tasks/task_v2_sales_workspace_draft_review_contract.md`
23. `docs/delivery/tasks/task_v2_sales_workspace_draft_review_routes_prototype.md`
24. `docs/delivery/tasks/task_v2_android_draft_review_id_flow_prototype.md`
25. `docs/delivery/tasks/task_v2_post_review_id_flow_persistence_decision_refresh.md`
26. `docs/delivery/tasks/task_v2_sales_workspace_persistence_baseline_design.md`
27. `docs/architecture/workspace/sales-workspace-persistence-baseline.md`
28. `docs/delivery/tasks/task_v2_postgres_dev_environment_baseline.md`
29. `docs/how-to/operate/postgres-dev-environment.md`
30. `docs/delivery/tasks/task_v2_sales_workspace_persistence_schema_design.md`
31. `docs/architecture/workspace/sales-workspace-persistence-schema.md`
32. `docs/delivery/tasks/task_v2_sales_workspace_persistence_migration_v0.md`
33. `docs/delivery/tasks/task_v2_sales_workspace_repository_layer_v0.md`
34. 本文件

---

## 7. Auto-continue allowed when

当前长线程的四个 persistence task 已完成；执行 agent 不应自动继续 Android 或 Runtime。

下一步需要先由规划层选择：Runtime / LangGraph design、Android review history view，或 DB hardening。

---

## 8. Stop conditions

命中以下任一条件时停止并交回规划层：

- 需要改变 V2 产品方向。
- 需要新增或扩展 API route。
- 需要新增 Android write path 或复杂交互。
- 需要接 LangGraph / LLM / search。
- 需要引入新外部依赖。
- 需要开放 production hardening 或新增 API surface。
