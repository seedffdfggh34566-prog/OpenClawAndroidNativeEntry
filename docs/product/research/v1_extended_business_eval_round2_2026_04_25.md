# V1 Extended Business Eval Round 2：2026-04-25

## 1. 评估目标

本轮评估用于验证 V1 RC 在更多真实业务输入下的完整链路质量：

```text
ProductLearning -> ProductProfile confirmation -> LeadAnalysis LLM -> ReportGeneration
```

本轮只评估质量、稳定性和成本，不新增功能。

---

## 2. 执行环境

- backend：`127.0.0.1:8014`
- 端口说明：`8013` 已有人工 inspector backend 占用，为避免停止人工查看进程，本轮 eval 临时使用 `8014`。
- database：`/tmp/openclaw_v1_extended_business_eval_round2_2026_04_25.db`
- trace dir：`/tmp/openclaw_llm_traces_round2`
- provider：Tencent TokenHub
- model：`minimax-m2.5`
- prompt versions：`product_learning_llm_v1`、`lead_analysis_llm_v1`
- API key：从 `backend/.env` 或环境变量读取，未打印、未写入文档。
- inspector：开启 `/dev/llm-inspector`，仅记录 run id、usage、parse status 和耗时摘要。

---

## 3. 样例输入

| sample_id | name | one_line_description |
|---|---|---|
| sample_01_manufacturing_inspection | 制造业设备巡检助手 | 面向制造业设备主管的移动巡检和故障记录工具 |
| sample_02_store_membership | 门店会员复购助手 | 帮助本地生活门店识别沉睡会员并组织复购活动 |
| sample_03_education_leads | 教培招生线索跟进助手 | 帮助培训机构整理试听线索并提醒课程顾问持续跟进 |
| sample_04_industrial_parts_quote | 工业备件询价管理工具 | 帮助工贸企业统一管理备件询价、供应商报价和采购跟进记录 |
| sample_05_dental_recall | 口腔诊所预约与复诊运营工具 | 帮助口腔诊所管理预约、复诊提醒和患者回访 |
| sample_06_project_quote_followup | 装修工程报价跟进助手 | 帮助装修和工程服务团队管理报价、客户沟通和项目跟进 |
| sample_07_export_inquiry_followup | 外贸 B2B 询盘跟进助手 | 帮助外贸团队整理询盘、报价和客户跟进节奏 |
| sample_08_local_service_scheduling | 本地生活门店排班与经营异常助手 | 帮助多门店服务业老板发现排班、营收和库存异常 |
| sample_09_community_group_fulfillment | 社区团购订单履约助手 | 帮助社区团购团长和供应商管理订单、分拣和配送履约 |
| sample_10_property_work_order | 物业工单巡检助手 | 帮助物业公司管理报修工单、公共区域巡检和处理闭环 |
| sample_11_chain_restaurant_supervision | 连锁餐饮门店督导助手 | 帮助连锁餐饮总部检查门店标准执行和经营异常 |
| sample_12_warehouse_inventory_count | 仓储库存盘点助手 | 帮助中小仓库管理库存盘点、差异复核和补货提醒 |
| sample_13_corporate_training_signup | 企业培训报名转化助手 | 帮助企业培训机构管理报名线索、企业客户需求和转化跟进 |
| sample_14_saas_customer_success_renewal | SaaS 客户成功续费助手 | 帮助 SaaS 团队识别续费风险并安排客户成功跟进 |
| sample_15_agri_dealer_customer_management | 农资经销客户管理助手 | 帮助农资经销商管理种植户客户、赊账和农时服务提醒 |
| sample_16_legal_case_followup | 法律咨询案件跟进助手 | 帮助律所和法律咨询团队管理咨询线索、案件阶段和材料提醒 |

---

## 4. 评估结果

| sample_id | profile_id | product_learning_run_id | lead_analysis_run_id | report_generation_run_id | agent_run_status | learning_stage | required_fields_filled | product_learning_tokens | lead_analysis_tokens | lead_analysis_trace | report_readability | hallucination_count | review_note |
|---|---|---|---|---|---|---|---|---:|---:|---|---|---:|---|
| sample_01_manufacturing_inspection | `pp_99d488a1` | `run_132e3c89` | `run_c2463c0d` | `run_45034eaa` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1085 | 1796 | succeeded; 8.5s | pass | 0 | 获客分析结构完整；报告结构完整，可读性通过 |
| sample_02_store_membership | `pp_0845d356` | `run_71527447` | `run_159680a3` | `run_e8402bde` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1165 | 1932 | succeeded; 10.7s | pass | 0 | 首次 lead_analysis malformed JSON，重试成功；报告结构完整 |
| sample_03_education_leads | `pp_aa35a5f7` | `run_2962f06b` | `run_118204ef` | `run_969a939f` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1193 | 1647 | succeeded; 10.3s | pass | 0 | 获客分析结构完整；报告结构完整，可读性通过 |
| sample_04_industrial_parts_quote | `pp_5a59071a` | `run_53745e00` | `run_3bb01ccd` | `run_4578c1c8` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1190 | 1948 | succeeded; 24.3s | pass | 0 | 两次 lead_analysis malformed JSON；最小 parser 修复后重跑成功 |
| sample_05_dental_recall | `pp_09f7b684` | `run_7d6918c0` | `run_7fd3f80a` | `run_47b7a78f` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1247 | 1530 | succeeded; 14.9s | pass | 0 | 获客分析结构完整；报告结构完整，可读性通过 |
| sample_06_project_quote_followup | `pp_e454355c` | `run_e6552aa1` | `run_a1b7af40` | `run_8067eb1a` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1162 | 1703 | succeeded; 16.9s | pass | 0 | 获客分析结构完整；报告结构完整，可读性通过 |
| sample_07_export_inquiry_followup | `pp_6c584ae7` | `run_98995ebf` | `run_26a35223` | `run_ddfb5a91` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1245 | 1520 | succeeded; 6.7s | pass | 0 | 获客分析结构完整；报告结构完整，可读性通过 |
| sample_08_local_service_scheduling | `pp_bd0c5a6f` | `run_770bcfbb` | `run_b5ff5017` | `run_149e1817` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1158 | 1683 | succeeded; 11.4s | pass | 0 | 首次 lead_analysis malformed JSON，重试成功；报告结构完整 |
| sample_09_community_group_fulfillment | `pp_27f35fac` | `run_8ef43ffb` | `run_e6efe3a6` | `run_b16aa452` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1195 | 1872 | succeeded; 11.0s | pass | 0 | 获客分析结构完整；报告结构完整，可读性通过 |
| sample_10_property_work_order | `pp_4df37849` | `run_b3db71ab` | `run_9d1bceb7` | `run_7ed85456` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1232 | 2108 | succeeded; 22.4s | pass | 0 | 获客分析结构完整；报告结构完整，可读性通过 |
| sample_11_chain_restaurant_supervision | `pp_2054d78b` | `run_51ac7fec` | `run_b49e19eb` | `run_c6a5cddb` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1073 | 1705 | succeeded; 7.0s | pass | 0 | 获客分析结构完整；报告结构完整，可读性通过 |
| sample_12_warehouse_inventory_count | `pp_ecd69bc0` | `run_38666bd4` | `run_e7bdc26d` | `run_9b675f84` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1081 | 1730 | succeeded; 8.0s | pass | 0 | 获客分析结构完整；报告结构完整，可读性通过 |
| sample_13_corporate_training_signup | `pp_5efd1949` | `run_ed67eaba` | `run_9b82180d` | `run_01f94be7` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1099 | 1742 | succeeded; 32.5s | pass | 0 | 获客分析结构完整；报告结构完整，可读性通过 |
| sample_14_saas_customer_success_renewal | `pp_5b2c5c80` | `run_f21ff815` | `run_0bae609d` | `run_bf1362d7` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1180 | 1922 | succeeded; 16.7s | pass | 0 | 获客分析结构完整；报告结构完整，可读性通过 |
| sample_15_agri_dealer_customer_management | `pp_621be619` | `run_91d8ee61` | `run_e1cbf099` | `run_a2df7f17` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1302 | 1698 | succeeded; 19.0s | pass | 0 | 获客分析结构完整；报告结构完整，可读性通过 |
| sample_16_legal_case_followup | `pp_b889a350` | `run_8a5078cc` | `run_7ab8332e` | `run_7b550cff` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1178 | 1915 | succeeded; 27.8s | pass | 0 | 获客分析结构完整；报告结构完整，可读性通过 |

---

## 5. 汇总判断

- product_learning succeeded：16/16
- lead_analysis succeeded：16/16
- report_generation succeeded：16/16
- report_readability pass：16/16
- required_fields_filled：16/16 为 4/4
- 工程词泄漏：0
- hallucination_count total：0
- product_learning token total：18785
- lead_analysis token total：28451
- combined LLM token total：47236
- combined LLM token average：约 2952 / 样例

本轮达到验收线。

---

## 6. 发现与修复

初始执行结果：

- ProductLearning：16/16 succeeded。
- LeadAnalysis：13/16 succeeded。
- ReportGeneration：13/16 succeeded。
- 失败样例均为 `lead_analysis_llm_json_decode_failed`，不是 timeout。

inspector trace 显示，失败集中在 MiniMax 输出的 JSON 尾部轻微 malformed：

- 数组结尾多出一个 `}`。
- 数组尾部缺少 `]`。
- raw content 不写入文档，仅通过本地 inspector 定位。

本任务内做了最小 parser 修复：

- 只在 LeadAnalysis parser 已经失败时尝试尾部括号修复。
- 不改 prompt、模型、provider、public API、schema 或 Android。
- 增加单测覆盖这两种尾部 malformed JSON。

修复后只重跑受影响样例，最终 16/16 全链路通过。

---

## 7. 结论

V1 RC 在 16 个真实中文业务样例上已达到稳定性、报告可读性和成本记录验收线。当前最大剩余风险不是主链路稳定性，而是 demo 证据打包、可重复演示 runbook，以及长期 LLM 输出质量 / 成本观测。
