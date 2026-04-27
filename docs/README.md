# 文档导航

更新时间：2026-04-27

## 1. 文档定位

本文件是当前仓库文档系统的总入口。

它主要服务以下目标：

- 让开发者快速知道当前项目主线是什么
- 让 Codex / Dev Agent 快速知道应先读哪些文件
- 让 `docs/` 结构成为正式唯一入口
- 减少后续 Android、backend、runtime 与文档推进时的歧义

---

## 2. 当前项目一句话说明

当前仓库已不再以早期 OpenClaw Android Native Entry 实验为主线。

当前正式主线为：

> **AI 销售助手 App：V1 已冻结为 demo-ready baseline，V2.1 engineering baseline completed；V2.1 product experience not completed yet。**

当前 V2 的核心架构方向是：

> **Sales Workspace Kernel：结构化 workspace 状态机 + WorkspacePatch 写回门禁 + 候选排序 + Markdown projection + ContextPack Compiler。**

Sales Workspace Kernel backend-only v0、no-DB FastAPI prototype v0、Android read-only workspace demo、可选 JSON file store prototype、deterministic Runtime PatchDraft prototype、PatchDraft review gate prototype、Android PatchDraft review UI prototype、Draft review contract、Draft review routes prototype、Android Draft Review ID flow prototype、post-review-id-flow persistence decision refresh、persistence baseline design、Postgres dev environment baseline、persistence schema design、persistence migration v0、repository layer v0、API Postgres store v0、Draft Review persistence v0、V2.1 engineering baseline closeout 和 V2.1 chat-first Runtime design 已完成。当前不是 V1 继续开发阶段，也不是扩展 Android write path、正式 Runtime / LangGraph implementation 或 V2.2 evidence / search 阶段。V2.1 product experience 仍需补齐 contract examples、backend prototype 和 Android chat-first UI。

当前 V2 prototype demo runbook 已补齐：

- `docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`

当前 clean demo verification 已完成，Draft review contract 已补齐：

- `docs/reference/api/sales-workspace-draft-review-contract.md`

---

## 3. 当前建议阅读顺序

无论是开发者还是 Dev Agent，进入仓库后建议按以下顺序阅读：

1. 根目录 `AGENTS.md`
2. `docs/product/overview.md`
3. `docs/product/research/v1_closeout_2026_04_25.md`
4. `docs/product/prd/ai_sales_assistant_v2_prd.md`
5. `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`
6. `docs/architecture/workspace/workspace-object-model.md`
7. `docs/architecture/workspace/sales-workspace-kernel.md`
8. `docs/architecture/workspace/workspace-kernel-v0-scope.md`
9. `docs/architecture/workspace/markdown-projection.md`
10. `docs/architecture/workspace/context-pack-compiler.md`
11. `docs/delivery/tasks/_active.md`
12. 当前 task 引用的 task / handoff

V2.2 搜索、来源证据和联系方式边界继续参考：

- `docs/adr/ADR-005-v2-lead-research-scope-and-search-boundary.md`

V1 细节可继续参考：

- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/reference/schemas/v1-domain-model-baseline.md`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/adr/ADR-001-backend-deployment-baseline.md`
- `docs/adr/ADR-002-v1-runtime-and-product-learning-baseline.md`
- `docs/adr/ADR-003-v1-product-learning-runtime-boundary.md`
- `docs/adr/ADR-004-v1-product-learning-iteration-contract.md`

---

## 4. 当前文档结构如何使用

当前仓库正式采用以下文档结构：

- `product/`：产品方向、PRD、研究与路线图
- `architecture/`：系统分层、仓库结构与 backend / runtime / data / clients / workspace 方案
- `reference/`：API contract、领域模型与其他权威参考
- `how-to/`：运行、运维、协作和排障手册
- `adr/`：关键架构与部署决策
- `delivery/`：任务与交接文档
- `archive/`：历史资料归档

旧的编号目录已迁出，不再作为正式入口。

---

## 5. 当前最重要的入口文件

### 5.1 项目方向

- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v2_prd.md`
- `docs/product/roadmap.md`
- `docs/adr/ADR-007-v2-sales-workspace-persistence-decision.md`
- `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`
- `docs/adr/ADR-005-v2-lead-research-scope-and-search-boundary.md`

### 5.2 当前 V2 workspace 架构

- `docs/architecture/workspace/workspace-object-model.md`
- `docs/architecture/workspace/sales-workspace-kernel.md`
- `docs/architecture/workspace/sales-workspace-persistence-baseline.md`
- `docs/architecture/workspace/sales-workspace-persistence-schema.md`
- `docs/architecture/runtime/v2-1-chat-first-runtime-design.md`
- `docs/architecture/workspace/workspace-kernel-v0-scope.md`
- `docs/architecture/workspace/markdown-projection.md`
- `docs/architecture/workspace/context-pack-compiler.md`

### 5.3 当前执行入口

- `docs/delivery/tasks/_active.md`
- `docs/adr/ADR-007-v2-sales-workspace-persistence-decision.md`
- `docs/reference/api/sales-workspace-kernel-v0-contract.md`
- `docs/reference/api/sales-workspace-kernel-v0-examples.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_persistence_decision.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_api_contract_v0.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_post_kernel_v0_planning.md`
- `docs/delivery/tasks/task_v2_sales_workspace_runtime_patchdraft_prototype.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_runtime_patchdraft_prototype.md`
- `docs/delivery/tasks/task_v2_sales_workspace_patchdraft_review_gate_prototype.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_patchdraft_review_gate_prototype.md`
- `docs/delivery/tasks/task_v2_android_patchdraft_review_ui_prototype.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_android_patchdraft_review_ui_prototype.md`
- `docs/delivery/tasks/task_v2_sales_workspace_prototype_demo_runbook.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_prototype_demo_runbook.md`
- `docs/delivery/tasks/task_v2_post_demo_next_phase_decision.md`
- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_contract.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_post_demo_next_phase_decision.md`
- `docs/reference/api/sales-workspace-draft-review-contract.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_draft_review_contract.md`
- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_routes_prototype.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_draft_review_routes_prototype.md`
- `docs/delivery/tasks/task_v2_android_draft_review_id_flow_prototype.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_android_draft_review_id_flow_prototype.md`
- `docs/delivery/tasks/task_v2_post_review_id_flow_persistence_decision_refresh.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_post_review_id_flow_persistence_decision_refresh.md`
- `docs/delivery/tasks/task_v2_sales_workspace_persistence_baseline_design.md`
- `docs/architecture/workspace/sales-workspace-persistence-baseline.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_persistence_baseline_design.md`
- `docs/delivery/tasks/task_v2_postgres_dev_environment_baseline.md`
- `docs/how-to/operate/postgres-dev-environment.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_postgres_dev_environment_baseline.md`
- `docs/delivery/tasks/task_v2_sales_workspace_persistence_schema_design.md`
- `docs/architecture/workspace/sales-workspace-persistence-schema.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_persistence_schema_design.md`
- `docs/delivery/tasks/task_v2_1_completion_closeout.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_1_completion_closeout.md`
- `docs/delivery/tasks/task_v2_1_chat_first_runtime_design.md`
- `docs/architecture/runtime/v2-1-chat-first-runtime-design.md`
- `docs/reference/api/sales-workspace-chat-first-runtime-contract.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_1_chat_first_runtime_design.md`

### 5.4 V1 baseline 与参考

- `docs/product/research/v1_closeout_2026_04_25.md`
- `docs/reference/schemas/v1-domain-model-baseline.md`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/architecture/system-context.md`
- `docs/architecture/runtime/langgraph-runtime-architecture.md`

### 5.5 当前工作流

- `docs/how-to/operate/developer_workflow_playbook.md`
- `docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`
- `docs/how-to/operate/postgres-dev-environment.md`
- `docs/how-to/operate/dev-agent-vs-sales-agent-runbook.md`
- `docs/how-to/operate/jianglab_codex_ops.md`
- `docs/how-to/operate/codex_backend_first_workflow.md`

### 5.6 目录级入口

- `docs/product/README.md`
- `docs/architecture/README.md`
- `docs/reference/README.md`
- `docs/how-to/README.md`
- `docs/adr/README.md`
- `docs/delivery/README.md`

---

## 6. 当前 Dev Agent 文档工作原则

当前推荐把文档分成三层理解：

1. **方向层**
   - `product/overview.md`
   - `product/prd/*`
   - `adr/*`
2. **方案层**
   - `architecture/workspace/*`
   - `architecture/*`
   - `reference/*`
   - `how-to/*`
3. **执行层**
   - `delivery/tasks/*`
   - `delivery/handoffs/*`

Dev Agent 的标准动作应为：

1. 先确认方向层没有变化
2. 再读取 workspace 方案层确认边界
3. 最后在执行层领取和推进 `_active.md` 指向的任务

---

## 7. 当前结构摘要

当前文档系统按以下结构运行：

```text
docs/
├─ README.md
├─ product/
├─ architecture/
│  ├─ workspace/
│  ├─ backend/
│  ├─ runtime/
│  ├─ clients/
│  └─ data/
├─ reference/
├─ how-to/
├─ adr/
├─ delivery/
└─ archive/
```

当前阶段最重要的是：

- 用 workspace-native sales agent 方向统一 V2 文档入口
- 以 Sales Workspace Kernel 作为 V2 当前技术主线
- 让 Dev Agent 工作流统一依赖 `docs/README.md` 与 `docs/delivery/tasks/_active.md`
- 避免回到 V1 线性报告链路或 2026-04-25 的 session-first 草案

---

## 8. 当前最推荐的下一步

当前 V1 已正式收口为 demo-ready release candidate / learning milestone，不进入 MVP。

最近完成或导入的 V2 planning / kernel baseline 文档包括：

- `task_v2_sales_workspace_direction_update.md`
- `task_v2_workspace_object_model.md`
- `task_v2_sales_workspace_kernel_backend_only_v0.md`
- `handoff_2026_04_26_v2_sales_workspace_direction_update.md`
- `handoff_2026_04_26_v2_workspace_object_model.md`
- `handoff_2026_04_26_v2_sales_workspace_kernel_v0_design.md`
- `handoff_2026_04_26_v2_sales_workspace_kernel_backend_only_v0.md`

当前正式执行入口为：

- `docs/delivery/tasks/_active.md`

当前自动排定任务：

- 暂无 implementation task 自动开放。

当前 Draft review contract 为：

- `docs/reference/api/sales-workspace-draft-review-contract.md`

当前 Draft review routes prototype 为：

- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_routes_prototype.md`

当前 Android Draft Review ID flow prototype 为：

- `docs/delivery/tasks/task_v2_android_draft_review_id_flow_prototype.md`

当前 post-review-id-flow persistence decision refresh 为：

- `docs/delivery/tasks/task_v2_post_review_id_flow_persistence_decision_refresh.md`

当前 persistence baseline design 为：

- `docs/architecture/workspace/sales-workspace-persistence-baseline.md`
- `docs/delivery/tasks/task_v2_sales_workspace_persistence_baseline_design.md`

当前 Postgres dev environment baseline 为：

- `docs/how-to/operate/postgres-dev-environment.md`
- `docs/delivery/tasks/task_v2_postgres_dev_environment_baseline.md`

当前 Sales Workspace persistence schema design 为：

- `docs/architecture/workspace/sales-workspace-persistence-schema.md`
- `docs/delivery/tasks/task_v2_sales_workspace_persistence_schema_design.md`

当前 demo 复现入口为：

- `docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`

最近完成的 contract / persistence decision 文档为：

- `docs/reference/api/sales-workspace-kernel-v0-contract.md`
- `docs/reference/api/sales-workspace-kernel-v0-examples.md`
- `docs/adr/ADR-007-v2-sales-workspace-persistence-decision.md`

当前结论：

- Postgres / Alembic persistence chain 已完成 migration、repository、API store 和 Draft Review persistence v0。
- no-DB FastAPI prototype v0 已完成。
- Android read-only workspace demo 已完成。
- JSON file store prototype 已完成。
- deterministic Runtime PatchDraft prototype 已完成。
- PatchDraft review gate prototype 已完成。
- Android PatchDraft review UI prototype 已完成。
- V2 Sales Workspace prototype demo runbook 已完成。
- clean demo verification 已完成。
- Draft review contract 已完成。
- Draft review routes prototype 已完成。
- Android Draft Review ID flow prototype 已完成。
- Post Review-ID Flow persistence decision refresh 已完成。
- Sales Workspace persistence baseline design 已完成。
- Postgres dev environment baseline 已完成。
- Sales Workspace persistence schema design 已完成。
- Sales Workspace persistence migration v0 已完成。
- Sales Workspace repository layer v0 已完成。
- Sales Workspace API Postgres store v0 已完成。
- Sales Workspace Draft Review persistence v0 已完成。
- V2.1 engineering baseline closeout 已完成。
- V2.1 chat-first Runtime design 已完成。
- V2.1 product experience 仍需完成 contract examples 和 backend / Android 实现后才算闭环完成。
- 当前没有 implementation task 自动开放。
- V2 MVP persistence baseline 采用 Postgres / Alembic。
- 当前不开放 Android 或 Runtime / LangGraph implementation。
- `in-memory / JSON fixture` 与 JSON file store 仅作为 prototype / contract validation / demo continuity 支撑，不是正式 persistence baseline。
- contract fixture examples / state transition examples 已补齐。

Sales Workspace Kernel backend-only v0 已完成：

- Pydantic schema
- in-memory / JSON fixture store
- WorkspacePatch apply
- deterministic candidate ranking
- Markdown projection
- ContextPack compiler
- FastAPI prototype endpoints
- Android read-only workspace demo
- optional JSON file store prototype
- deterministic Runtime PatchDraft prototype
- PatchDraft review gate prototype
- Android PatchDraft review UI prototype
- prototype demo runbook
- clean demo verification
- Draft review contract
- Draft review routes prototype
- Android Draft Review ID flow prototype
- Post Review-ID Flow persistence decision refresh
- Sales Workspace persistence baseline design
- Postgres dev environment baseline
- Sales Workspace persistence schema design
- pytest

当前 V2.1 后续顺序冻结为：

1. Sales Workspace Kernel backend API contract。
2. Persistence decision。
3. Backend API prototype。
4. Android read-only workspace view。
5. JSON file store prototype。
6. Runtime PatchDraft prototype。
7. PatchDraft review gate prototype。
8. Android PatchDraft review UI prototype。
9. Prototype demo runbook。
10. Post-demo next phase decision。
11. Draft review contract。
12. Draft review routes prototype。
13. Android Draft Review ID flow prototype。
14. Post Review-ID Flow persistence decision refresh。
15. Sales Workspace persistence baseline design。
16. Postgres dev environment baseline。
17. Sales Workspace persistence schema design。
18. Sales Workspace persistence migration v0。
19. Sales Workspace repository layer v0。
20. Sales Workspace API Postgres store v0。
21. Sales Workspace Draft Review persistence v0。
22. V2.1 engineering baseline closeout。
23. V2.1 chat-first runtime design。
24. V2.1 chat-first runtime contract examples。
25. V2.1 chat-first runtime backend prototype。

当前仍不应自动实现：

- 新增或扩展 Sales Workspace FastAPI endpoint
- SQLAlchemy ORM / Alembic migration / SQLite schema change
- 新增或扩展 Android write path 或复杂 workspace 交互
- 正式 LangGraph graph
- 真实 LLM
- 联网搜索 / search provider
- ContactPoint
- CRM / 自动触达
- V2.2 evidence / search / ContactPoint

当前自动排定任务：

- 暂无 implementation task 自动开放。

V2.2 planned / blocked task placeholders：

- `docs/delivery/tasks/task_v2_2_runtime_langgraph_design.md`
- `docs/delivery/tasks/task_v2_2_android_review_history_planning.md`
- `docs/delivery/tasks/task_v2_2_search_evidence_boundary_design.md`

---

## 9. 一句话总结

当前项目已经从 V1 demo baseline 转入：

> **AI 销售助手 V2.1 engineering baseline completed：Sales Workspace Kernel、Android Draft Review ID flow、Postgres persistence chain 与 Draft Review audit persistence 已进入 main；V2.1 chat-first Runtime design 已完成，但 product experience 仍需 contract examples、backend prototype 和 Android chat-first UI 才算闭环完成；当前不直接写 V2.2 LangGraph / LLM / search 或 Android 扩展。**
