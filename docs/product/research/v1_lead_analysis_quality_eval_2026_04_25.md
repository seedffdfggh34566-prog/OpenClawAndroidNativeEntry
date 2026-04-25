# V1 Lead Analysis Quality Eval：2026-04-25

## 1. 评估定位

本记录用于评估 V1 `lead_analysis` heuristic quality follow-up 后的完整价值链路质量：

`ProductLearning -> ProductProfile confirmation -> lead_analysis -> report_generation`

本轮目标不是验证链路能否跑通，而是验证增强后的 `lead_analysis` 是否能提供更有用的获客判断，尤其是：

- 上下游 / 邻近机会
- 更具体的优先级判断依据
- 首轮销售验证建议
- 明确的“不建议优先做什么”
- 报告是否能承接这些内容

---

## 2. 执行环境

- backend DB：`/tmp/openclaw_v1_lead_analysis_quality_followup_2026_04_25.db`
- product learning provider：腾讯云 TokenHub
- product learning model：`minimax-m2.5`
- product learning prompt_version：`product_learning_llm_v1`
- lead_analysis：backend heuristic graph
- report_generation：backend heuristic graph
- 执行方式：真实 backend API
- API key：从 `backend/.env` 读取，未写入文档或日志

---

## 3. 样例输入

复用上一轮 8 个真实中文业务样例：

1. 制造业设备巡检助手
2. 门店会员复购助手
3. 教培招生线索跟进助手
4. 工业备件询价管理工具
5. 口腔诊所预约与复诊运营工具
6. 装修 / 工程项目报价跟进助手
7. 外贸 B2B 询盘跟进助手
8. 本地生活门店排班与经营异常助手

---

## 4. 评估结果

| sample_id | profile_id | product_learning_run_id | lead_analysis_run_id | report_generation_run_id | agent_run_status | learning_stage | required_fields_filled | llm_usage.total_tokens | lead_analysis_relevance | lead_analysis_actionability | neighbor_opportunity_quality | report_readability | hallucination_count | review_note |
|---|---|---|---|---|---|---|---|---:|---|---|---|---|---:|---|
| sample_01_manufacturing_inspection | `pp_c33ead0e` | `run_49da8f03` | `run_ff5523df` | `run_deaafc64` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1237 | pass | pass | pass | pass | 0 | 邻近/上下游机会、首轮验证建议、不优先建议均可见；报告承接判断依据 |
| sample_02_store_membership | `pp_475eb935` | `run_f89f0863` | `run_069a7886` | `run_cc36ba7e` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1110 | pass | pass | pass | pass | 0 | 邻近/上下游机会、首轮验证建议、不优先建议均可见；报告承接判断依据 |
| sample_03_education_leads | `pp_7eac6998` | `run_bdd0770b` | `run_85576deb` | `run_ec5b33d7` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 956 | pass | pass | pass | pass | 0 | 邻近/上下游机会、首轮验证建议、不优先建议均可见；报告承接判断依据 |
| sample_04_industrial_parts_quote | `pp_8bf25e63` | `run_c2a3bc94` | `run_76561aff` | `run_58386ca6` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1111 | pass | pass | pass | pass | 0 | 邻近/上下游机会、首轮验证建议、不优先建议均可见；报告承接判断依据 |
| sample_05_dental_recall | `pp_220b5009` | `run_01c9a397` | `run_1d92ed61` | `run_54fb837f` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1135 | pass | pass | pass | pass | 0 | 邻近/上下游机会、首轮验证建议、不优先建议均可见；报告承接判断依据 |
| sample_06_project_quote_followup | `pp_f9c5d109` | `run_18677924` | `run_ab4a9549` | `run_6eb9ce83` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1125 | pass | pass | pass | pass | 0 | 邻近/上下游机会、首轮验证建议、不优先建议均可见；报告承接判断依据 |
| sample_07_export_inquiry_followup | `pp_6ebb8091` | `run_622af947` | `run_23f5ffd7` | `run_c141f188` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1144 | pass | pass | pass | pass | 0 | 邻近/上下游机会、首轮验证建议、不优先建议均可见；报告承接判断依据 |
| sample_08_local_service_scheduling | `pp_cf82c4ec` | `run_18c4f1c4` | `run_d4000200` | `run_5c084fad` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1163 | pass | pass | pass | pass | 0 | 邻近/上下游机会、首轮验证建议、不优先建议均可见；报告承接判断依据 |

---

## 5. 汇总判断

- product_learning succeeded：8/8
- lead_analysis succeeded：8/8
- report_generation succeeded：8/8
- required_fields_filled：8/8 为 4/4
- lead_analysis relevance pass：8/8
- lead_analysis actionability pass：8/8
- neighbor_opportunity_quality pass：8/8
- report_readability pass：8/8
- 工程词泄漏：0
- hallucination_count total：0
- product_learning LLM token total：8981
- product_learning LLM token average：约 1123 / 样例

本轮达到验收线。

---

## 6. 结论

增强后的 `lead_analysis` 在 8 个真实中文业务样例上稳定成功，并且比上一轮基础 heuristic 多出更明确的销售验证动作、上下游 / 邻近机会和不优先建议。报告生成已能把这些判断依据带入最终报告。

当前仍是 deterministic heuristic，内容深度受产品画像字段限制。若后续希望进一步提升行业判断、渠道证据和竞争替代方案质量，下一步再拆 `task_v1_lead_analysis_llm_phase1.md` 或引入更严格的行业知识评估，不建议混入本任务。
