# 任务目录说明

更新时间：2026-04-27

## 1. 目录定位

本目录用于承载当前项目的正式任务文档。

任务文档的作用不是重复 PRD 或 spec，而是把已经明确的方向拆成可以独立执行、独立验证、独立交接的小闭环。

---

## 2. 当前阶段说明

当前项目已经完成：

- AI 销售助手 V1 demo-ready release candidate / learning milestone closeout。
- V1 demo runbook 与 evidence pack。
- V2 workspace-native sales agent 产品北极星更新。
- V2 Sales Workspace object model 草案。
- V2 Sales Workspace Kernel backend-only v0 设计与实现。
- V2 Sales Workspace no-DB FastAPI prototype v0。
- V2 Android read-only workspace demo。
- V2 Sales Workspace JSON file store prototype。
- V2 Runtime PatchDraft prototype。
- V2 PatchDraft review gate prototype。
- V2 Android PatchDraft review UI prototype。
- V2 Sales Workspace prototype demo runbook。
- V2 post-demo next phase decision。
- V2 Draft review contract。
- V2 Draft review routes prototype。
- V2 Android Draft Review ID flow prototype。
- V2 post-review-id-flow persistence decision refresh。
- V2 Sales Workspace persistence baseline design。
- V2 Postgres dev environment baseline。
- V2 Sales Workspace persistence schema design。

当前项目处于：

> **V2 workspace-native sales agent / Sales Workspace Kernel prototype 阶段**

当前阶段已经完成 Sales Workspace Kernel backend API contract、persistence decision、contract examples、no-DB FastAPI prototype、Android read-only workspace demo、可选 JSON file store prototype、deterministic Runtime PatchDraft prototype、PatchDraft review gate prototype、Android PatchDraft review UI prototype、prototype demo runbook、post-demo next phase decision、Draft review contract、Draft review routes prototype、Android Draft Review ID flow prototype、post-review-id-flow persistence decision refresh、persistence baseline design、Postgres dev environment baseline、persistence schema design、persistence migration v0、repository layer v0、API Postgres store v0 和 Draft Review persistence v0。当前没有自动排定任务，不自动进入扩展 Android write path、正式 LangGraph、真实 LLM 或搜索实现。

---

## 3. 当前任务状态

当前正式任务队列以 `_active.md` 为准。

当前入口：

- Current task：暂无自动排定
- Next queued task：暂无 implementation task 自动开放

Sales Workspace Kernel backend-only v0 已完成：

- Pydantic schema
- in-memory / JSON fixture store
- WorkspacePatch apply
- deterministic candidate ranking
- Markdown projection
- ContextPack compiler
- pytest
- no-DB FastAPI prototype endpoints
- Android read-only workspace demo
- optional JSON file store prototype
- deterministic Runtime PatchDraft prototype
- PatchDraft review gate prototype
- Android PatchDraft review UI prototype
- prototype demo runbook
- post-demo next phase decision
- Draft review contract
- Draft review routes prototype
- Android Draft Review ID flow prototype
- post-review-id-flow persistence decision refresh
- persistence baseline design
- Postgres dev environment baseline
- persistence schema design

---

## 4. 当前任务状态总览

| 任务 | 目标 | 当前状态 |
|---|---|---|
| `task_v2_sales_workspace_direction_update.md` | 将 V2 北极星升级为 workspace-native sales agent | `done` |
| `task_v2_workspace_object_model.md` | 定义 Sales Workspace 核心对象模型 | `done` |
| `task_v2_sales_workspace_kernel_backend_only_v0.md` | 实现 Sales Workspace Kernel backend-only v0 | `done` |
| `task_v2_sales_workspace_post_v0_entry_sync.md` | 同步 post-v0 入口与任务队列 | `done` |
| `task_v2_sales_workspace_api_contract_v0.md` | 定义 Sales Workspace Kernel backend API contract v0 | `done` |
| `task_v2_sales_workspace_persistence_decision.md` | 决策 v0.1 persistence 路线 | `done` |
| `task_v2_sales_workspace_contract_fixture_examples.md` | 补齐 API contract examples / state transitions | `done` |
| `task_v2_sales_workspace_backend_api_prototype_v0.md` | 实现 no-DB backend API prototype v0 | `done` |
| `task_v2_sales_workspace_backend_api_v0.md` | 实现 persistence-backed backend API v0 | `superseded by API Postgres store chain` |
| `task_v2_android_workspace_readonly_view.md` | Android read-only workspace view | `done` |
| `task_v2_sales_workspace_json_store_prototype.md` | 可选 JSON file store prototype | `done` |
| `task_v2_sales_workspace_runtime_patchdraft_prototype.md` | deterministic Runtime PatchDraft prototype | `done` |
| `task_v2_sales_workspace_patchdraft_review_gate_prototype.md` | PatchDraft preview / explicit apply review gate | `done` |
| `task_v2_android_patchdraft_review_ui_prototype.md` | Android 人工审阅并显式 apply PatchDraft | `done` |
| `task_v2_sales_workspace_prototype_demo_runbook.md` | 固化 V2 prototype demo 复现流程 | `done` |
| `task_v2_post_demo_next_phase_decision.md` | 决定 post-demo 下一阶段方向 | `done` |
| `task_v2_sales_workspace_draft_review_contract.md` | 定义 Draft persistence / review history contract | `done` |
| `task_v2_sales_workspace_draft_review_routes_prototype.md` | 实现 backend-managed Draft review routes prototype | `done` |
| `task_v2_android_draft_review_id_flow_prototype.md` | Android 使用 backend-managed draft_review_id 审阅和 apply | `done` |
| `task_v2_post_review_id_flow_persistence_decision_refresh.md` | Android review-id flow 后刷新 persistence 方向判断 | `done` |
| `task_v2_sales_workspace_persistence_baseline_design.md` | 设计正式 persistence baseline，优先评估 Postgres / Alembic | `done` |
| `task_v2_postgres_dev_environment_baseline.md` | 补本地 Postgres dev environment 与验证命令 | `done` |
| `task_v2_sales_workspace_persistence_schema_design.md` | 设计 Sales Workspace 正式 persistence schema | `done` |
| `task_v2_sales_workspace_persistence_migration_v0.md` | 实现首版 Sales Workspace Postgres / Alembic migration | `done` |
| `task_v2_sales_workspace_repository_layer_v0.md` | 实现 Sales Workspace Postgres repository layer | `done` |
| `task_v2_sales_workspace_api_postgres_store_v0.md` | 将 Sales Workspace API 切到 Postgres-backed store | `done` |
| `task_v2_sales_workspace_draft_review_persistence_v0.md` | 将 Draft Review lifecycle 落入 Postgres persistence | `done` |
| `task_v2_sales_workspace_draft_review_persistence_schema.md` | 设计 Draft Review 正式 persistence schema | `done / folded into persistence schema design` |
| `task_v2_runtime_langgraph_design.md` | 设计正式 Runtime / LangGraph WorkspacePatchDraft flow | `planned / blocked by persistence schema and writeback boundary` |
| `task_v2_android_review_history_view.md` | Android Draft Review history / detail view | `planned / blocked by persistence and read API` |
| `task_v2_sales_workspace_runtime_patchdraft_integration.md` | Runtime / LangGraph WorkspacePatchDraft integration | `planned / blocked by API and persistence` |
| `task_v2_conversational_sales_agent_definition_update.md` | 2026-04-25 旧 V2 定义更新 | `done / superseded by workspace-native direction` |
| `task_v2_planning_baseline_update.md` | 将仓库入口、ADR、roadmap 和 active task 状态对齐到 V2 planning baseline | `done` |
| `task_v1_closeout.md` | 将 V1 收口为 demo baseline / learning milestone，并停止继续追加 V1 功能 | `done` |
| `task_v1_demo_runbook_and_evidence_pack.md` | 固化可重复 demo 流程并收集真机证据包 | `done` |

更早的 V1 已完成任务仍可在 `docs/delivery/tasks/` 中按文件名查阅。

---

## 5. 使用规则

执行正式任务前，应至少完成以下动作：

1. 阅读仓库根目录 `AGENTS.md`
2. 阅读 `docs/README.md`
3. 阅读 `docs/delivery/tasks/_active.md`
4. 阅读本目录下对应 task 文档
5. 阅读 task 引用的 PRD / spec / decision 文档
6. 仅在 task 范围内实施最小改动
7. 完成后更新 task 状态并补充 handoff

---

## 6. 历史 handoff 说明

`docs/delivery/handoffs/` 中历史 handoff 只反映当时状态，不作为当前正式路径或当前默认导航依据。

当前正式入口仍以：

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/delivery/tasks/_active.md`

为准。

---

## 7. 当前默认原则

- 优先做 Sales Workspace Kernel，而不是继续扩展 V1 线性报告链路。
- 结构化对象是主真相，Markdown 是 projection，不是唯一主存。
- WorkspacePatch 是 workspace 状态变更入口。
- CandidateRankingBoard 必须由 deterministic ranking 派生，不能由 Product Sales Agent / Runtime draft 直接写入。
- ContextPack 从结构化 workspace state 编译，不读取 Markdown、LangGraph checkpoint 或 SDK session。
- Android 端仍只做控制入口，不抢后端主存职责。
- Backend services / workspace kernel 负责正式对象写回裁决。
- Runtime / Product Sales Agent execution layer 后续只产出 draft payload、工具结果和中间推理。
- 若对象模型、页面结构与代码现实冲突，先更新 task / spec，再动实现。
- V2.1 已完成 API contract -> persistence decision -> contract examples -> no-DB backend API prototype -> Android read-only demo -> JSON file store prototype -> Runtime PatchDraft prototype -> PatchDraft review gate prototype -> Android PatchDraft review UI prototype -> prototype demo runbook -> Draft review contract -> Draft review routes prototype -> Android Draft Review ID flow prototype -> post-review-id-flow persistence decision refresh -> persistence baseline design。
- 当前 demo 复现入口为 `docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`。
- Draft review contract 已完成：`docs/reference/api/sales-workspace-draft-review-contract.md`。
- Draft review routes prototype 已完成：`docs/delivery/tasks/task_v2_sales_workspace_draft_review_routes_prototype.md`。
- Android Draft Review ID flow prototype 已完成：`docs/delivery/tasks/task_v2_android_draft_review_id_flow_prototype.md`。
- post-review-id-flow persistence decision refresh 已完成：`docs/delivery/tasks/task_v2_post_review_id_flow_persistence_decision_refresh.md`。
- persistence baseline design 已完成：`docs/architecture/workspace/sales-workspace-persistence-baseline.md`。
- Postgres dev environment baseline 已完成：`docs/how-to/operate/postgres-dev-environment.md`。
- Sales Workspace persistence schema design 已完成：`docs/architecture/workspace/sales-workspace-persistence-schema.md`。
- Sales Workspace persistence migration v0 已完成：`docs/delivery/tasks/task_v2_sales_workspace_persistence_migration_v0.md`。
- Sales Workspace repository layer v0 已完成：`docs/delivery/tasks/task_v2_sales_workspace_repository_layer_v0.md`。
- Sales Workspace API Postgres store v0 已完成：`docs/delivery/tasks/task_v2_sales_workspace_api_postgres_store_v0.md`。
- Sales Workspace Draft Review persistence v0 已完成：`docs/delivery/tasks/task_v2_sales_workspace_draft_review_persistence_v0.md`。
- 当前没有自动排定任务。
- 后续 Android 体验增强、正式 Runtime / LangGraph integration 或 DB hardening 必须等待对应 task 解锁后再推进。
