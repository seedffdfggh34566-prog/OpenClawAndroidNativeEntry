# 当前活跃任务

更新时间：2026-04-25

## 1. 使用说明

本文件用于告诉开发者和 agent：

- 当前优先推进哪个正式任务
- 哪个任务只是背景材料
- 哪个任务已经完成，可以作为参考而非继续追加

进入正式开发前，建议先读本文件，再进入对应 task。

---

## 2. 当前状态

### 已完成的基础冻结任务

- `task_v1_domain_model_baseline.md`
- `task_v1_information_architecture.md`
- `task_v1_android_control_shell_refactor.md`
- `task_v1_backend_api_contract.md`
- `task_backend_first_repo_and_docs_alignment.md`
- `task_docs_structure_migration.md`
- `task_docs_migration_review_and_old_path_cleanup.md`
- `task_v1_backend_minimum_implementation.md`
- `task_v1_android_minimum_real_backend_integration.md`
- `task_v1_android_minimum_product_profile_write_path.md`
- `task_v1_android_analysis_run_trigger_poll.md`
- `task_v1_android_report_generation_trigger_poll.md`
- `task_v1_analysis_result_detail_contract.md`
- `task_v1_product_profile_confirmation_flow.md`
- `task_v1_product_learning_interaction_baseline.md`
- `task_v1_real_runtime_integration_phase1.md`
- `task_v1_product_learning_runtime_decision_freeze.md`
- `task_v1_product_learning_iteration_contract.md`
- `task_v1_product_learning_backend_preflight.md`
- `task_v1_product_learning_llm_phase1.md`
- `task_v1_android_product_learning_iteration_ui.md`
- `task_v1_android_product_learning_enrich_device_smoke.md`
- `task_v1_android_sales_flow_expression_closeout.md`
- `task_v1_full_sales_flow_device_smoke.md`
- `task_android_chinese_input_smoke_mechanism.md`
- `task_v1_product_learning_eval_prompt_tuning_followup.md`

这些任务当前应视为：

- 已完成
- 可引用
- 不在原文件中继续无限追加新需求

### Current task

- 暂无正在执行中的正式 implementation task

### Next queued tasks

- 暂无已排定的下一项 implementation task

最近完成：

- `task_v1_product_learning_eval_prompt_tuning_followup.md`
- `task_android_chinese_input_smoke_mechanism.md`
- `task_v1_full_sales_flow_device_smoke.md`
- `task_v1_android_sales_flow_expression_closeout.md`
- `task_v1_android_product_learning_enrich_device_smoke.md`
- `task_v1_android_product_learning_iteration_ui.md`
- `task_v1_product_learning_llm_phase1.md`
- `task_v1_product_learning_backend_preflight.md`
- `task_v1_runtime_observability_eval_baseline.md`
- `task_v1_product_learning_iteration_contract.md`
- `task_v1_product_learning_runtime_decision_freeze.md`
- `task_v1_product_learning_runtime_followup.md`
- `task_v1_real_runtime_integration_phase1.md`
- `task_v1_product_learning_interaction_baseline.md`
- `task_v1_product_profile_confirmation_flow.md`
- `task_v1_analysis_result_detail_contract.md`
- `task_v1_android_report_generation_trigger_poll.md`
- `task_v1_android_analysis_run_trigger_poll.md`
- `task_v1_android_minimum_product_profile_write_path.md`
- `task_v1_android_minimum_real_backend_integration.md`

当前切换原因：

- product learning runtime follow-up 已完成最小 backend + Android 闭环
- product learning backend preflight 已补齐 enrich endpoint 与 runtime metadata baseline
- 当前下一阶段的核心风险不再是“能否跑通”，而是：
  - product learning LLM 是否能在现有 contract 与 eval baseline 下稳定输出
  - heuristic 与真实 LLM 的差异是否可被样例集约束
  - Android 是否会在 runtime 未稳定时被过早拉进交互重写
- 当前 product learning LLM Phase 1 与 Android iteration UI 均已完成最小实现与收口；下一步需要规划层决定是否进入 UI polish、真机完整 enrich smoke、或新的 V1 表达收口任务。
- 真机完整 enrich smoke 已完成，并修复了真实 LLM 耗时下 Android enrich 状态显示滞后的问题。
- 首页 / 产品画像确认页 / 结果页 / 报告页的 V1 销售闭环产品表达收口任务已完成。
- 完整 V1 真机端到端 smoke 已完成，主闭环从空库到报告可复看已跑通。
- Android 中文输入 smoke 机制已记录为 runbook；当前设备仅有 `com.baidu.input_oppo/.ImeService`，正式中文自动化输入需后续准备测试 IME。
- Product learning 真实样例评估 / prompt tuning follow-up 已完成，8 个真实样例均稳定通过，未触发 prompt tuning。
- 下一步需要规划层决定是否继续 ProductLearning 页面表达 polish、扩大真实业务样例库，或拆 runtime usage metadata follow-up。

### Auto-continue allowed when

满足以下条件时，执行 agent 可在不逐项审批的前提下继续 next queued tasks：

- 下一个 task 已在 `docs/delivery/tasks/` 中正式创建
- `_active.md` 已明确把它列入 next queued tasks
- 当前 task 已完成最小验证、task 状态更新、handoff 与原子 commit
- 未命中 stop conditions

### Stop conditions

命中以下任一条件时，执行 agent 应停止并把控制权交回规划层：

- 需要改变产品方向、V1 范围或 ADR 基线
- 下一个 task 尚未写入 docs
- docs / contract / code 冲突，已超出当前 task 含义
- 需要新基础设施、迁移、部署调整或高风险环境变更
- 连续验证失败说明当前 task 边界判断可能错误

---

## 3. 当前执行原则

当前默认执行原则为：

1. 执行 agent 可以连续推进已排定 task 队列，不要求每个 task 都重新审批
2. 若发现是方向变化，先退出 task 执行，回到 overview / PRD / decision
3. 若只是小修订，可拆为 follow-up task，而不是继续污染已完成 task
4. 每个 task 都必须独立完成验证、handoff、状态更新与原子 commit
