# V1 Lead Analysis LLM Eval：2026-04-25

## 1. 评估定位

本记录用于评估 `lead_analysis` 从增强 heuristic 切换到真实 LLM draft 生成后的 V1 完整价值链路质量：

`ProductLearning -> ProductProfile confirmation -> lead_analysis -> report_generation`

本轮只评估 `lead_analysis` LLM phase 1；`report_generation` 仍是 heuristic graph，并被动承接 `LeadAnalysisResult`。

---

## 2. 执行环境

- backend DB：`/tmp/openclaw_v1_lead_analysis_llm_phase1_2026_04_25.db`
- provider：腾讯云 TokenHub
- model：`minimax-m2.5`
- product learning prompt_version：`product_learning_llm_v1`
- lead analysis prompt_version：`lead_analysis_llm_v1`
- 执行方式：真实 backend API
- API key：从 `backend/.env` 读取，未写入文档或日志

---

## 3. 样例输入

复用 8 个真实中文业务样例：

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

| sample_id | profile_id | product_learning_run_id | lead_analysis_run_id | report_generation_run_id | agent_run_status | learning_stage | required_fields_filled | product_learning_tokens | lead_analysis_tokens | lead_analysis_relevance | lead_analysis_actionability | neighbor_opportunity_quality | report_readability | hallucination_count | review_note |
|---|---|---|---|---|---|---|---|---:|---:|---|---|---|---|---:|---|
| sample_01_manufacturing_inspection | `pp_8b7f7fb8` | `run_ddeda776` | `run_625ee579` | `run_4c4426e5` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1367 | 1840 | pass | pass | pass | pass | 0 | LLM lead_analysis 输出可被报告承接；未见工程词泄漏 |
| sample_02_store_membership | `pp_2dfff0ee` | `run_d8ea41da` | `run_b634974f` | `run_4a45be35` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1226 | 2021 | pass | pass | pass | pass | 0 | LLM lead_analysis 输出可被报告承接；未见工程词泄漏 |
| sample_03_education_leads | `pp_6fade20a` | `run_182839cd` | `run_9c05b62b` | `run_28b890e1` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1125 | 1865 | pass | pass | pass | pass | 0 | LLM lead_analysis 输出可被报告承接；未见工程词泄漏 |
| sample_04_industrial_parts_quote | `pp_30abd223` | `run_89b9a69a` | `run_434a7d38` | `run_8912529e` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1118 | 1924 | pass | pass | pass | pass | 0 | LLM lead_analysis 输出可被报告承接；未见工程词泄漏 |
| sample_05_dental_recall | `pp_a6021178` | `run_71dcb4d3` | `run_cc8d5742` | `run_a0fe360c` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1091 | 1900 | pass | pass | pass | pass | 0 | LLM lead_analysis 输出可被报告承接；未见工程词泄漏 |
| sample_06_project_quote_followup | `pp_9efffd2b` | `run_1e7df031` | `run_9b01f565` | `run_1f1c9eda` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1101 | 1860 | pass | pass | pass | pass | 0 | LLM lead_analysis 输出可被报告承接；未见工程词泄漏 |
| sample_07_export_inquiry_followup | `pp_685ab2c4` | `run_2ee7d854` | `run_7c59743a` | `run_56e5f6c2` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1158 | 1973 | pass | pass | pass | pass | 0 | LLM lead_analysis 输出可被报告承接；未见工程词泄漏 |
| sample_08_local_service_scheduling | `pp_0b09b668` | `run_1042a5fa` | `run_d9f60e85` | `run_82f31b5b` | pl=succeeded;lead=succeeded;report=succeeded | confirmed | 4/4 | 1036 | 1903 | pass | pass | pass | pass | 0 | LLM lead_analysis 输出可被报告承接；未见工程词泄漏 |

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
- product_learning token total：9222
- lead_analysis token total：15286
- combined LLM token total：24508
- combined LLM token average：约 3064 / 样例

本轮达到验收线。

---

## 6. 超时处理记录

初始 eval 到 sample 08 时，`lead_analysis` 连续两次出现 `tokenhub_request_timeout`：

- `run_9ad33f91`
- `run_72f9770d`

定位为 lead_analysis LLM 输出更长，当前 30s 默认超时对该路径偏紧。任务内做了最小修复：

- `lead_analysis` TokenHub client 调用使用 `max(settings.llm_timeout_seconds, 60.0)`。
- prompt 增加“每条数组内容控制在 80 个中文字符以内”。

修复后复用同一 ProductProfile 重试：

- `run_d9f60e85` succeeded。
- `run_82f31b5b` report_generation succeeded。

---

## 7. 结论

`lead_analysis_llm_v1` 在 8 个真实中文业务样例上达到了稳定性和可读性验收线，并且相较 heuristic 版本能生成更完整的行业、客户、场景、邻近 / 上下游机会和验证建议。

当前成本显著高于只做 ProductLearning：本轮 lead_analysis LLM token 总量 15286，高于 ProductLearning 的 9222。后续若继续推进，应优先做报告层 polish 或 V1 readiness freeze；是否继续优化 prompt 成本可单独拆任务。
