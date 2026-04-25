# 当前活跃任务

更新时间：2026-04-25

## 1. 使用说明

本文件用于告诉开发者和 agent：

- 当前优先推进哪个正式任务
- 哪个任务只是背景材料
- 哪个任务已经完成，可以作为参考而非继续追加
- 当前是否允许自动继续执行下一项任务

进入正式开发前，建议先读本文件，再进入对应 task。

---

## 2. 当前状态

### Current task

- 暂无。当前 V2 planning baseline 已建立，但尚未创建 V2 implementation task queue。

### Next queued tasks

- 尚未排定。

除非后续明确创建 task 并写入本文件，否则执行 agent 不应自动实现：

- V2 后端 schema / migration
- V2 API
- 搜索 provider
- Android UI
- Web 前端
- 联系方式采集或导出
- 自动触达

---

## 3. 最近完成

- `task_v2_conversational_sales_agent_definition_update.md`
- `task_v2_planning_baseline_update.md`
- `task_v1_closeout.md`
- `task_v1_demo_runbook_and_evidence_pack.md`
- `task_v1_extended_business_eval_round2.md`
- `task_v1_developer_llm_run_inspector.md`
- `task_v1_llm_latency_and_fallback_followup.md`
- `task_v1_demo_device_smoke_after_llm_lead_analysis.md`
- `task_v1_report_generation_polish.md`
- `task_v1_readiness_freeze_and_demo_acceptance.md`
- `task_v1_lead_analysis_llm_phase1.md`
- `task_v1_lead_analysis_quality_followup.md`
- `task_v1_real_business_sample_library_eval.md`
- `task_v1_runtime_usage_metadata_followup.md`
- `task_v1_product_learning_ui_polish_real_chinese_smoke.md`
- `task_android_chinese_input_device_preflight.md`
- `task_android_chinese_input_test_ime_device_smoke.md`
- `task_v1_product_learning_eval_prompt_tuning_followup.md`
- `task_android_chinese_input_smoke_mechanism.md`
- `task_v1_full_sales_flow_device_smoke.md`
- `task_v1_android_sales_flow_expression_closeout.md`
- `task_v1_android_product_learning_enrich_device_smoke.md`
- `task_v1_android_product_learning_iteration_ui.md`
- `task_v1_product_learning_llm_phase1.md`
- `task_v1_product_learning_backend_preflight.md`

更早的 V1 基础任务可直接在 `docs/delivery/tasks/` 中按文件名查阅。

---

## 4. 当前结论

V1 当前应视为：

- 已完成
- 可引用
- 不进入 MVP
- 不继续追加功能
- 只允许在明确 task 下修复阻断 demo 复现的严重问题

V2 当前应视为：

- 已进入 planning baseline
- 已有 PRD Draft v0.2
- 已有 sales agent data model Draft v0.1
- 已有 lead research data model Draft v0.1
- 已有 ADR-006 对话式专属销售 agent baseline
- 已有 ADR-005 搜索 / 来源证据 / 联系方式边界
- 尚未冻结 schema、API contract、搜索 provider 或 implementation queue

---

## 5. 当前执行入口

当前优先阅读：

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/product/overview.md`
4. `docs/product/research/v1_closeout_2026_04_25.md`
5. `docs/product/prd/ai_sales_assistant_v2_prd.md`
6. `docs/architecture/data/v2-sales-agent-data-model.md`
7. `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`
8. `docs/architecture/data/v2-lead-research-data-model.md`
9. `docs/adr/ADR-005-v2-lead-research-scope-and-search-boundary.md`
10. 本文件

当前 planning baseline task：

- `docs/delivery/tasks/task_v2_conversational_sales_agent_definition_update.md`
- `docs/delivery/tasks/task_v2_planning_baseline_update.md`

当前 handoff：

- `docs/delivery/handoffs/handoff_2026_04_25_v2_conversational_sales_agent_definition_update.md`
- `docs/delivery/handoffs/handoff_2026_04_25_v2_planning_baseline_update.md`

---

## 6. Auto-continue allowed when

满足以下条件时，执行 agent 可在不逐项审批的前提下继续 next queued tasks：

- 下一个 task 已在 `docs/delivery/tasks/` 中正式创建
- `_active.md` 已明确把它列入 next queued tasks
- 当前 task 已完成最小验证、task 状态更新、handoff 与原子 commit
- 未命中 stop conditions

当前没有满足这些条件的 next queued task。

---

## 7. Stop conditions

命中以下任一条件时，执行 agent 应停止并把控制权交回规划层：

- 需要改变产品方向、V2 planning baseline 或 ADR 基线
- 下一个 task 尚未写入 docs
- docs / contract / code 冲突，已超出当前 task 含义
- 需要新基础设施、迁移、部署调整或高风险环境变更
- 需要选择搜索 provider
- 需要决定个人联系方式保留、删除、脱敏或合规策略
- 连续验证失败说明当前 task 边界判断可能错误

---

## 8. 当前执行原则

1. 执行 agent 可以连续推进已排定 task 队列，不要求每个 task 都重新审批。
2. 当前没有已排定的 V2 implementation task queue。
3. 若发现是方向变化，先退出 task 执行，回到 overview / PRD / ADR / decision。
4. 若只是小修订，可拆为 follow-up task，而不是继续污染已完成 task。
5. 每个 task 都必须独立完成验证、handoff、状态更新与原子 commit。
6. V2 实现任务必须先由规划层写入 `docs/delivery/tasks/` 并排入本文件。
