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
- `task_android_chinese_input_test_ime_device_smoke.md`
- `task_android_chinese_input_device_preflight.md`
- `task_v1_product_learning_ui_polish_real_chinese_smoke.md`
- `task_v1_runtime_usage_metadata_followup.md`
- `task_v1_real_business_sample_library_eval.md`
- `task_v1_lead_analysis_quality_followup.md`
- `task_v1_lead_analysis_llm_phase1.md`
- `task_v1_readiness_freeze_and_demo_acceptance.md`
- `task_v1_report_generation_polish.md`
- `task_v1_demo_device_smoke_after_llm_lead_analysis.md`
- `task_v1_llm_latency_and_fallback_followup.md`
- `task_v1_demo_release_candidate_hardening.md`
- `task_v1_report_readability_postprocess_followup.md`
- `task_v1_developer_llm_run_inspector.md`
- `task_v1_closeout.md`

这些任务当前应视为：

- 已完成
- 可引用
- 不在原文件中继续无限追加新需求

### Current task

- 暂无。当前正式任务队列已收口，下一步需要规划层重新排定。

### Next queued tasks

- 尚未排定。

最近完成：

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
- Android 中文输入 smoke 机制已验证：当前 Android 16 真机已保留 `com.android.adbkeyboard`，后续可通过 `ADB_INPUT_B64` 注入中文，结束后恢复原输入法。
- Product learning 真实样例评估 / prompt tuning follow-up 已完成，8 个真实样例均稳定通过，未触发 prompt tuning。
- 中文输入设备预检已完成：当前真机已保留 `com.android.adbkeyboard`，日常 smoke 只切换输入法，不再重复安装 / 卸载。
- ProductLearning UI polish 与真实中文 create / enrich smoke 已完成，`工厂设备巡检助手` 样例在真机上跑通 create 和 enrich，最终 ProductProfile 进入 `ready_for_confirmation`。
- runtime usage metadata follow-up 已完成，product learning 真实 LLM token usage 已写入 `AgentRun.runtime_metadata.llm_usage` 并通过 run detail 可见。
- 真实业务样例库扩展与全链路质量评估已完成，8 个真实中文样例均跑通完整 backend API 链路，并修复了 lead/report 用户可见工程表述泄漏。
- lead_analysis 质量提升 follow-up 已完成，当前 heuristic 已补齐邻近 / 上下游机会、首轮销售验证建议和不优先建议，并通过 8 个真实中文样例 eval。
- lead_analysis LLM phase1 已完成，当前 `lead_analysis` 使用 TokenHub `minimax-m2.5` 生成 draft，并通过 8 个真实中文样例 eval。
- V1 readiness freeze 已完成，当前 V1 具备 demo 条件但仍有 TTFT 延迟、报告交付感和 fallback 未实现等 known limitations。
- report_generation polish 已完成，最终报告 sections 已收口为更像可复看的销售分析交付物。
- demo device smoke after LLM lead analysis 已完成。真实中文真机 demo 路径已跑通；过程中修复了 lead_analysis LLM JSON 解析稳定性问题。未出现 timeout 阻断，因此 latency / fallback follow-up 暂不触发实现。
- LLM latency / fallback follow-up 已作为 conditional task 收口为未触发；当前没有已排定的下一项 implementation task。
- V1 demo release candidate hardening 已完成，当前 RC demo 能力、验收标准、固定样例和已知限制已冻结。下一项进入 report readability postprocess。
- report readability postprocess 已完成，报告 summary 和 section bullet 长度已做轻量控制。下一项进入 16 个真实业务样例 round 2 eval。
- developer LLM run inspector 已完成，当前可用 `/dev/llm-inspector` 查看 ProductLearning / LeadAnalysis 的本地 LLM trace。下一项恢复为 16 个真实业务样例 round 2 eval。
- extended business eval round2 已完成，16 个真实中文业务样例全链路通过；过程中修复了 LeadAnalysis LLM 尾部 malformed JSON 的最小解析兼容问题。下一项进入 demo runbook and evidence pack。
- demo runbook and evidence pack 已完成，V1 真机中文 demo 路径、开发者复现 runbook 和 evidence pack 已收口。当前没有下一项已排定 implementation task。
- V1 closeout 已完成，V1 正式冻结为 demo-ready release candidate / learning milestone，不进入 MVP；当前不定义 V2，不创建 V2 task 队列，下一阶段需要规划层重新决定。

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
