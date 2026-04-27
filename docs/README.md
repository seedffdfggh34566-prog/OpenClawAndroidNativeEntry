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

> **AI 销售助手 App：V1 已冻结为 demo-ready baseline，当前进入 V2 workspace-native sales agent / Sales Workspace Kernel prototype 阶段。**

当前 V2 的核心架构方向是：

> **Sales Workspace Kernel：结构化 workspace 状态机 + WorkspacePatch 写回门禁 + 候选排序 + Markdown projection + ContextPack Compiler。**

Sales Workspace Kernel backend-only v0、no-DB FastAPI prototype v0、Android read-only workspace demo、可选 JSON file store prototype、deterministic Runtime PatchDraft prototype、PatchDraft review gate prototype 和 Android PatchDraft review UI prototype 已完成。当前不是 V1 继续开发阶段，也不是 V2 MVP、数据库 migration、扩展 Android write path 或正式 Runtime / LangGraph 集成阶段。

当前 V2 prototype demo runbook 已补齐：

- `docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`

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
- `docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_json_store_prototype.md`
- `docs/delivery/tasks/task_v2_sales_workspace_runtime_patchdraft_prototype.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_runtime_patchdraft_prototype.md`
- `docs/delivery/tasks/task_v2_sales_workspace_patchdraft_review_gate_prototype.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_patchdraft_review_gate_prototype.md`
- `docs/delivery/tasks/task_v2_android_patchdraft_review_ui_prototype.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_android_patchdraft_review_ui_prototype.md`
- `docs/delivery/tasks/task_v2_sales_workspace_prototype_demo_runbook.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_prototype_demo_runbook.md`

### 5.4 V1 baseline 与参考

- `docs/product/research/v1_closeout_2026_04_25.md`
- `docs/reference/schemas/v1-domain-model-baseline.md`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/architecture/system-context.md`
- `docs/architecture/runtime/langgraph-runtime-architecture.md`

### 5.5 当前工作流

- `docs/how-to/operate/developer_workflow_playbook.md`
- `docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`
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

- 暂无自动排定 implementation task。

当前 demo 复现入口为：

- `docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`

最近完成的 contract / persistence decision 文档为：

- `docs/reference/api/sales-workspace-kernel-v0-contract.md`
- `docs/reference/api/sales-workspace-kernel-v0-examples.md`
- `docs/adr/ADR-007-v2-sales-workspace-persistence-decision.md`

当前结论：

- 不进入 SQLite / Alembic。
- no-DB FastAPI prototype v0 已完成。
- Android read-only workspace demo 已完成。
- JSON file store prototype 已完成。
- deterministic Runtime PatchDraft prototype 已完成。
- PatchDraft review gate prototype 已完成。
- Android PatchDraft review UI prototype 已完成。
- V2 Sales Workspace prototype demo runbook 已完成。
- 不开放 persistence-backed backend API implementation。
- `in-memory / JSON fixture` 仅作为 prototype / contract validation 支撑，不是正式 persistence baseline。
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

当前仍不应自动实现：

- 新增或扩展 Sales Workspace FastAPI endpoint
- SQLAlchemy ORM / Alembic migration / SQLite schema change
- 新增或扩展 Android write path 或复杂 workspace 交互
- 正式 LangGraph graph
- 真实 LLM
- 联网搜索 / search provider
- ContactPoint
- CRM / 自动触达

---

## 9. 一句话总结

当前项目已经从 V1 demo baseline 转入：

> **AI 销售助手 V2 workspace-native sales agent：Sales Workspace Kernel backend-only v0、no-DB FastAPI prototype v0、Android read-only workspace demo、JSON file store prototype、Runtime PatchDraft prototype、PatchDraft review gate prototype、Android PatchDraft review UI prototype 与 prototype demo runbook 已完成；下一步由规划层决定正式 Runtime / LangGraph integration、draft persistence / review history、DB-backed persistence 或 Android review UX 谁先进入任务队列。**
