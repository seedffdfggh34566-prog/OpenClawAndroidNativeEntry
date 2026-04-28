# 任务目录说明

更新时间：2026-04-28

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

> **V2.1 validated prototype path completed；V2.1 product milestone remains open under planning control。**

当前阶段已经完成 Sales Workspace Kernel backend API contract、persistence decision、contract examples、no-DB FastAPI prototype、Android read-only workspace demo、可选 JSON file store prototype、deterministic Runtime PatchDraft prototype、PatchDraft review gate prototype、Android PatchDraft review UI prototype、prototype demo runbook、post-demo next phase decision、Draft review contract、Draft review routes prototype、Android Draft Review ID flow prototype、post-review-id-flow persistence decision refresh、persistence baseline design、Postgres dev environment baseline、persistence schema design、persistence migration v0、repository layer v0、API Postgres store v0、Draft Review persistence v0 和 V2.1 engineering baseline closeout。V2.1 chat-first Runtime design、contract examples、trace persistence、backend prototype、Android chat-first UI、demo runbook、PRD Acceptance Traceability、backend-level 5-sample conversational acceptance 和 Tencent TokenHub LLM runtime prototype 已形成 validated prototype path。当前状态以 `docs/product/project_status.md` 为准；task / handoff 不自行定义产品阶段完成。不自动进入扩展 Android write path、正式 LangGraph、V2.2 搜索或 ContactPoint 实现。

---

## 3. 当前任务状态

当前正式任务队列以 `_active.md` 为准。

当前入口：

- Current delivery package：暂无自动开放 delivery package
- Current task：暂无自动排定任务
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
| `package_v2_1_implementation_rebaseline.md` | 复核 V2.1 实现状态并收敛阻断复现缺口 | `done` |
| `task_v2_1_implementation_rebaseline_and_gap_closure.md` | 执行 V2.1 implementation rebaseline、最小验证和阻断 bug 修复 | `done` |
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
| `task_v2_1_completion_closeout.md` | 完成 V2.1 engineering baseline closeout | `done` |
| `task_v2_1_chat_first_runtime_design.md` | 设计 V2.1 chat-first Runtime / WorkspacePatchDraft 产品体验闭环 | `done` |
| `task_v2_1_chat_first_runtime_contract_examples.md` | 补 V2.1 chat-first Runtime contract examples | `done` |
| `task_v2_1_chat_first_runtime_trace_persistence_schema_design.md` | 设计 chat-first trace persistence schema | `done` |
| `task_v2_1_chat_first_runtime_trace_persistence_migration_v0.md` | 实现 chat-first trace persistence migration v0 | `done` |
| `task_v2_1_chat_first_runtime_backend_prototype.md` | 实现 V2.1 chat-first Runtime backend prototype | `done` |
| `task_v2_1_android_chat_first_workspace_ui_prototype.md` | Android chat-first workspace UI prototype | `done` |
| `task_v2_1_product_experience_demo_runbook.md` | 固化 V2.1 product experience demo runbook | `done` |
| `task_v2_1_product_experience_closeout.md` | 收口 deterministic chat-first demo flow；不代表 PRD-level V2.1 完成 | `done / corrected` |
| `task_v2_1_prd_acceptance_gap_review.md` | 将 PRD 成功标准映射到实现、测试、真机证据和缺口 | `done` |
| `task_v2_1_conversational_completion_scope.md` | 定义 V2.1 conversational completion 最小范围 | `done` |
| `task_v2_1_conversation_acceptance_examples.md` | 定义 5 个中文业务验收样例 | `done` |
| `task_v2_1_conversational_implementation_queue.md` | 创建 V2.1 conversational implementation queue | `done` |
| `task_v2_1_clarifying_questions_backend_prototype.md` | 实现主动追问 3-5 个问题的 backend prototype | `done` |
| `task_v2_1_workspace_explanation_backend_prototype.md` | 实现基于 workspace objects 的解释型回答 | `done` |
| `task_v2_1_product_profile_extraction_runtime.md` | 扩展产品理解 deterministic extraction | `done` |
| `task_v2_1_lead_direction_adjustment_runtime.md` | 扩展获客方向调整 deterministic runtime | `done` |
| `task_v2_1_conversation_acceptance_e2e.md` | 用 5 个中文样例验收 V2.1 conversational experience | `done` |
| `task_v2_1_android_conversation_polish.md` | Android 最小 conversation polish | `done` |
| `task_v2_1_android_conversation_sample_smoke.md` | Android 代表性 conversation sample smoke | `done` |
| `task_v2_1_product_experience_device_acceptance.md` | 真机端到端验收 V2.1 product experience | `done` |
| `task_v2_1_prd_acceptance_final_review.md` | V2.1 PRD Acceptance final review | `done` |
| `task_v2_1_product_experience_final_closeout.md` | 历史 prototype-path closeout evidence；当前 V2.1 milestone 状态以 `docs/product/project_status.md` 为准 | `done` |
| `task_v2_1_llm_runtime_boundary_design.md` | 定义 V2.1 Tencent TokenHub LLM runtime 边界 | `done` |
| `task_v2_1_llm_provider_dev_baseline.md` | 复用 Tencent TokenHub provider 并增加 runtime mode 配置 | `done` |
| `task_v2_1_sales_agent_structured_output_contract.md` | 定义 Sales Agent LLM structured output contract | `done` |
| `task_v2_1_llm_sales_agent_turn_backend_prototype.md` | 实现 LLM sales-agent-turn backend prototype | `done` |
| `task_v2_1_llm_eval_acceptance_examples.md` | 运行 fake-client 与 live TokenHub eval | `done` |
| `task_v2_1_llm_runtime_docs_sync.md` | 同步 LLM runtime docs / runbook / reference 入口 | `done` |
| `task_v2_1_llm_runtime_closeout.md` | 收口 V2.1 LLM runtime prototype | `done` |
| `task_v2_2_runtime_langgraph_design.md` | 设计 V2.2 Runtime / LangGraph WorkspacePatchDraft flow | `planned / blocked until explicitly opened` |
| `task_v2_2_android_review_history_planning.md` | 规划 Android Draft Review history / detail view | `planned / blocked until explicitly opened` |
| `task_v2_2_search_evidence_boundary_design.md` | 设计搜索证据与 ContactPoint 边界 | `planned / blocked until explicitly opened` |
| `task_v2_sales_workspace_draft_review_persistence_schema.md` | 设计 Draft Review 正式 persistence schema | `done / folded into persistence schema design` |
| `task_v2_runtime_langgraph_design.md` | 设计正式 Runtime / LangGraph WorkspacePatchDraft flow | `planned / blocked until explicitly opened` |
| `task_v2_android_review_history_view.md` | Android Draft Review history / detail view | `planned / blocked until explicitly opened` |
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

### 5.1 Milestone closeout rule

任务文档是执行入口，不是产品完成标准。

任何版本级 closeout 必须回到上位文档检查：

- PRD
- roadmap
- ADR
- architecture baseline

版本级 closeout 必须包含 `PRD Acceptance Traceability` 表，并将每条 PRD 成功标准标注为 `done / partial / missing / out of scope`。不能只引用 task done、handoff 或测试通过来宣称版本完成。

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
- V2.1 engineering baseline 已完成 API contract -> persistence decision -> contract examples -> no-DB backend API prototype -> Android read-only demo -> JSON file store prototype -> Runtime PatchDraft prototype -> PatchDraft review gate prototype -> Android PatchDraft review UI prototype -> prototype demo runbook -> Draft review contract -> Draft review routes prototype -> Android Draft Review ID flow prototype -> post-review-id-flow persistence decision refresh -> persistence baseline design -> Postgres dev environment -> persistence schema -> migration -> repository -> API Postgres store -> Draft Review persistence -> V2.1 engineering baseline closeout。
- V2.1 chat-first Runtime design 已完成。
- V2.1 chat-first deterministic demo flow、backend-level 5-sample conversational acceptance、Android polish、真机端到端验收、PRD Acceptance final review 和 Tencent TokenHub LLM runtime prototype 已形成 validated prototype path；V2.1 product milestone 仍开放于规划控制下。V2.2 evidence / search / ContactPoint implementation 继续 blocked。
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
- V2.1 engineering baseline closeout 已完成：`docs/delivery/tasks/task_v2_1_completion_closeout.md`。
- 当前自动排定任务：暂无。
- 推荐下一步：由规划层决定是否开放 V2.2 docs-level planning 或 V2.1 LLM prompt quality follow-up；V2.2 implementation 继续 blocked。
- 后续 Android 体验增强、正式 Runtime / LangGraph implementation、V2.2 evidence/search/contact 或 DB hardening 必须等待对应 task 解锁后再推进。
