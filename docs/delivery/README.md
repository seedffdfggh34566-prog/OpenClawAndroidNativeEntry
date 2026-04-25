# 任务目录说明

更新时间：2026-04-25

## 1. 目录定位

本目录用于承载当前项目的正式任务文档。

任务文档的作用不是重复 PRD 或 spec，而是把已经明确的方向拆成可以独立执行、独立验证、独立交接的小闭环。

---

## 2. 当前阶段说明

当前项目已经完成：

- 主线切换到 AI 销售助手 V1
- V1 范围与非目标初步收口
- 本地服务器承载正式后端的部署基线明确
- 文档体系、runbook 和 decision 骨架建立

当前项目正在推进：

- 当前正式任务队列已收口为空，下一步需要规划层重新排定。

因此，当前阶段的重点是：

> 保持 V1 demo 链路可验证，并按明确任务继续做小闭环质量提升。

---

## 3. 当前推荐执行顺序

最近完成的下一批任务：

1. product learning LLM phase 1
2. Android product learning iteration UI

原因如下：

- 文档结构现已切到新 docs 架构，后续任务应直接按新入口推进
- Android 已完成从占位数据切到真实 `/history` 与对象详情读取
- Android 已完成最小 ProductProfile 创建
- Android 已完成 `lead_analysis` 触发与轮询
- Android 已完成 `report_generation` 触发与轮询
- runtime observability / eval baseline 已冻结
- product learning 已切到真实 LLM draft 生成
- Android 产品学习页已补齐最小“继续补充一轮信息”交互
- Android 端已完成真实 backend 联通环境下的 product learning enrich 真机 smoke
- 首页 / 产品画像确认页 / 结果页 / 报告页的 V1 销售闭环产品表达收口已完成
- 完整 V1 真机端到端 smoke 已完成，当前主闭环从空库到报告可复看已跑通
- Product learning 真实样例评估 / prompt tuning follow-up 已完成，当前 `minimax-m2.5 + product_learning_llm_v1` 在 8 个样例中未触发 prompt tuning
- ProductLearning 页面表达 polish 与真实中文 create / enrich smoke 已完成
- runtime usage metadata follow-up 已完成，后续真实样例评估可记录 token usage
- 真实业务样例库扩展与全链路质量评估已完成，8 个真实中文样例均跑通完整 backend API 链路
- lead_analysis 质量提升 follow-up 已完成，heuristic 已补齐邻近 / 上下游机会、首轮销售验证建议和不优先建议
- lead_analysis LLM phase1 已完成，当前 `lead_analysis` 已切到 TokenHub `minimax-m2.5`
- V1 readiness freeze 已完成，demo acceptance、known limitations、TTFT 延迟风险和固定 demo 样例已收口
- report_generation polish 已完成，报告 sections 已收口为可复看的销售分析交付物结构
- 真机 demo smoke after LLM lead analysis 已完成，真实中文 demo 路径已跑通；过程中修复了 lead_analysis LLM JSON 解析稳定性问题
- LLM latency / fallback follow-up 已收口为 conditional not triggered，当前未实现 fallback
- V1 demo release candidate hardening 已完成，RC demo 能力、验收标准、固定样例和已知限制已冻结
- report readability postprocess 已完成，报告 summary 和 section bullet 可读性已做轻量收口
- developer LLM run inspector 已完成
- extended business eval round2 已完成，16 个真实中文业务样例全链路通过
- demo runbook and evidence pack 已完成，V1 真机中文 demo 路径和证据包已收口

---

## 4. 当前任务状态总览

| 任务 | 目标 | 当前状态 |
|---|---|---|
| `task_v1_domain_model_baseline.md` | 定义 V1 正式业务对象与状态流转基线 | `done` |
| `task_v1_information_architecture.md` | 明确手机端 V1 页面结构与核心闭环入口 | `done` |
| `task_v1_android_control_shell_refactor.md` | 将现有 Android 入口重构为 AI 销售助手控制壳层 | `done` |
| `task_v1_backend_api_contract.md` | 冻结 V1 最小后端 API contract 与历史状态查询边界 | `done` |
| `task_backend_first_repo_and_docs_alignment.md` | 对齐后端优先的仓库理解、docs 入口与 agent 工作流 | `done` |
| `task_docs_structure_migration.md` | 将 docs 从旧编号目录迁移到新 docs 架构 | `done` |
| `task_docs_migration_review_and_old_path_cleanup.md` | 复核 docs 迁移结果并清理旧路径与旧项目叙事残留 | `done` |
| `task_v1_backend_minimum_implementation.md` | 落地 V1 最小正式后端实现 | `done` |
| `task_v1_android_minimum_real_backend_integration.md` | 让 Android 壳层切到真实 `/history`、`ProductProfile` 与报告读取 | `done` |
| `task_v1_android_minimum_product_profile_write_path.md` | 让 Android 壳层创建第一版 ProductProfile 草稿 | `done` |
| `task_v1_android_analysis_run_trigger_poll.md` | 让 Android 壳层触发 lead_analysis 并轮询 AgentRun | `done` |
| `task_v1_android_report_generation_trigger_poll.md` | 让 Android 壳层触发 report_generation 并打开 AnalysisReport | `done` |
| `task_v1_analysis_result_detail_contract.md` | 补齐 AnalysisResult 详情 contract 与页面读取 | `done` |
| `task_v1_product_profile_confirmation_flow.md` | 补齐 ProductProfile `draft -> confirmed` 确认闭环 | `done` |
| `task_v1_product_learning_interaction_baseline.md` | 冻结产品学习交互基线、最低完整度门槛与阶段状态 | `done` |
| `task_v1_real_runtime_integration_phase1.md` | 以 backend-direct LangGraph 替换 analysis/report stub runtime | `done` |
| `task_v1_product_learning_runtime_decision_freeze.md` | 冻结 product learning runtime 的对象边界、阶段判定与接口承载 | `done` |
| `task_v1_product_learning_runtime_followup.md` | 以现有 public API 落地 product learning single-turn enrich 实现 | `done` |
| `task_v1_product_learning_iteration_contract.md` | 冻结下一轮 product learning enrich endpoint 与写回 contract | `done` |
| `task_v1_runtime_observability_eval_baseline.md` | 冻结 runtime metadata、样例集与最小评估基线 | `done` |
| `task_v1_product_learning_llm_phase1.md` | 将 heuristic product learning 切换到真实 LLM draft 生成 | `done` |
| `task_v1_android_product_learning_iteration_ui.md` | 让 Android 学习页支持继续补充一轮信息 | `done` |
| `task_v1_android_product_learning_enrich_device_smoke.md` | 真机跑通 Android product learning enrich 完整链路 | `done` |
| `task_v1_android_sales_flow_expression_closeout.md` | 收口 Android 首页、产品画像确认页、结果页和报告页的销售闭环表达 | `done` |
| `task_v1_full_sales_flow_device_smoke.md` | 真机从空库验证 V1 主闭环完整跑通 | `done` |
| `task_android_chinese_input_smoke_mechanism.md` | 记录 Android 真机中文自动化输入机制与测试 IME 方案 | `done` |
| `task_v1_product_learning_eval_prompt_tuning_followup.md` | 扩展真实 product learning 样例评估并按阈值决定是否调 prompt | `done` |
| `task_v1_product_learning_ui_polish_real_chinese_smoke.md` | 收口 ProductLearning 页面表达并执行真实中文 smoke | `done` |
| `task_android_chinese_input_device_preflight.md` | 一次性准备 jianglab 真机中文输入测试 IME | `done` |
| `task_v1_runtime_usage_metadata_followup.md` | 补齐 product learning LLM token usage metadata 与 API 可见性 | `done` |
| `task_v1_real_business_sample_library_eval.md` | 扩展真实业务样例库并评估 V1 全链路质量 | `done` |
| `task_v1_lead_analysis_quality_followup.md` | 增强 lead_analysis heuristic 的销售判断深度 | `done` |
| `task_v1_lead_analysis_llm_phase1.md` | 将 lead_analysis 切换到真实 LLM draft 生成 | `done` |
| `task_v1_readiness_freeze_and_demo_acceptance.md` | 冻结 V1 demo acceptance 与 known limitations | `done` |
| `task_v1_report_generation_polish.md` | 增强最终报告交付物表达 | `done` |
| `task_v1_demo_device_smoke_after_llm_lead_analysis.md` | 真机验证 LeadAnalysis LLM 后的完整 demo 路径 | `done` |
| `task_v1_llm_latency_and_fallback_followup.md` | 仅在 LLM timeout 阻断 demo 时执行延迟 / fallback 最小修复 | `conditional_not_triggered` |
| `task_v1_demo_release_candidate_hardening.md` | 冻结 V1 RC demo 验收标准和后续 hardening 顺序 | `done` |
| `task_v1_report_readability_postprocess_followup.md` | 收口最终报告 summary 与 bullet 可读性 | `done` |
| `task_v1_developer_llm_run_inspector.md` | 提供开发者本地 LLM run inspector 以支持样例评估 | `done` |
| `task_v1_extended_business_eval_round2.md` | 用 16 个真实中文业务样例评估 RC 质量、稳定性和 token 成本 | `done` |
| `task_v1_demo_runbook_and_evidence_pack.md` | 固化可重复 demo 流程并收集真机证据包 | `done` |

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

`docs/delivery/handoffs/` 中 2026-04-23 文档结构迁移前的 handoff，可能仍保留旧目录名或旧阶段表述。

这些内容只反映当时状态，不作为当前正式路径或当前默认导航依据。当前正式入口仍以：

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/delivery/tasks/_active.md`

为准。

---

## 7. 当前默认原则

- 优先做小闭环，不做大重构
- 优先把 AI 销售助手 V1 的新主线落成，而不是继续扩展旧 OpenClaw 入口功能
- Android 端当前只做控制入口，不抢后端主存职责
- 正式后端实现当前优先级高于继续扩展 Android 壳层
- 若对象模型、页面结构与代码现实冲突，先更新 task / spec，再动实现
