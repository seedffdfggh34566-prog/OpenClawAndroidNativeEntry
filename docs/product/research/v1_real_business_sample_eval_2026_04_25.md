# V1 Real Business Sample Eval：2026-04-25

## 1. 评估定位

本记录用于评估 V1 在更多真实中文业务输入下的完整价值链路质量：

`ProductLearning -> ProductProfile confirmation -> lead_analysis -> report_generation`

本轮评估发生在以下能力完成后：

- product learning 已接入真实 TokenHub `minimax-m2.5`
- Android 主闭环与真实中文 smoke 已跑通
- `AgentRun.runtime_metadata.llm_usage` 已可记录 token usage

---

## 2. 执行环境

- backend DB：`/tmp/openclaw_v1_real_business_sample_eval_2026_04_25.db`
- provider：腾讯云 TokenHub
- model：`minimax-m2.5`
- prompt_version：`product_learning_llm_v1`
- 执行方式：真实 backend API
- API key：从 `backend/.env` 读取，未写入文档或日志

说明：

- 每个样例只触发一次真实 product learning LLM。
- lead_analysis / report_generation 当前仍是 heuristic LangGraph phase1。
- 本轮曾先发现 lead/report 暴露 `Phase 1 / LangGraph / v1_langgraph_phase1` 等用户可见工程表述；已做最小修复后，复用同一批 ProductProfile 重新跑 lead/report，不重复消耗 product learning LLM token。

---

## 3. 样例输入

| sample_id | name | one_line_description | source_notes |
|---|---|---|---|
| sample_01_manufacturing_inspection | 制造业设备巡检助手 | 面向制造业设备主管的移动巡检和故障记录工具 | 支持离线巡检、设备台账、异常拍照、维修派单；目标客户是中小制造工厂、设备主管和维修班组。核心痛点是纸质巡检漏项、故障记录分散、维修响应慢。 |
| sample_02_store_membership | 门店会员复购助手 | 帮助本地生活门店识别沉睡会员并组织复购活动 | 适合美容美发、健身房、宠物店和社区零售门店；关注会员分层、消费频次下降提醒、活动触达和到店复购。 |
| sample_03_education_leads | 教培招生线索跟进助手 | 帮助培训机构整理试听线索并提醒课程顾问持续跟进 | 适合 K12 素质教育、职业培训和成人学习机构；解决线索遗漏、顾问跟进不及时、试听后转化记录分散。 |
| sample_04_industrial_parts_quote | 工业备件询价管理工具 | 帮助工贸企业统一管理备件询价、供应商报价和采购跟进记录 | 适合卖工业备件、MRO 耗材和设备配件的 B2B 团队；痛点是微信群报价混乱、历史价格难查、采购进度不透明。 |
| sample_05_dental_recall | 口腔诊所预约与复诊运营工具 | 帮助口腔诊所管理预约、复诊提醒和患者回访 | 适合单体口腔诊所和小型连锁；解决预约冲突、复诊遗漏、治疗后回访不及时、前台手工记录分散的问题。 |
| sample_06_project_quote_followup | 装修工程报价跟进助手 | 帮助装修和工程服务团队管理报价、客户沟通和项目跟进 | 适合装修公司、工装团队和工程服务商；痛点是报价版本混乱、客户跟进断档、项目阶段不透明、销售和设计协同不顺。 |
| sample_07_export_inquiry_followup | 外贸 B2B 询盘跟进助手 | 帮助外贸团队整理询盘、报价和客户跟进节奏 | 适合做机械设备、五金配件、消费品出口的 B2B 外贸团队；痛点是询盘来源分散、报价记录难查、时差导致跟进延迟、客户优先级不清。 |
| sample_08_local_service_scheduling | 本地生活门店排班与经营异常助手 | 帮助多门店服务业老板发现排班、营收和库存异常 | 适合餐饮、洗衣、宠物护理和社区服务门店；解决排班冲突、门店营收异常、库存预警滞后和店长汇报不及时。 |

---

## 4. 最终评估结果

| sample_id | profile_id | product_learning_run_id | lead_analysis_run_id | report_generation_run_id | agent_run_status | learning_stage | required_fields_filled | llm_usage.total_tokens | lead_analysis_relevance | lead_analysis_actionability | report_readability | hallucination_count | review_note |
|---|---|---|---|---|---|---|---|---:|---|---|---|---:|---|
| sample_01_manufacturing_inspection | `pp_c3b34d05` | `run_8745948b` | `run_ae7b5e85` | `run_8843021f` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1147 | pass | pass | pass | 0 | 工程表述已移除；分析建议结构完整；报告分节完整 |
| sample_02_store_membership | `pp_42c22381` | `run_00749a52` | `run_585249d7` | `run_fe4e92ed` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1138 | pass | pass | pass | 0 | 工程表述已移除；分析建议结构完整；报告分节完整 |
| sample_03_education_leads | `pp_1e3ed10e` | `run_feb03957` | `run_2708c5de` | `run_c181ab3c` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1069 | pass | pass | pass | 0 | 工程表述已移除；分析建议结构完整；报告分节完整 |
| sample_04_industrial_parts_quote | `pp_e6525eed` | `run_8722ed8f` | `run_7ce03031` | `run_acb3892e` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1169 | pass | pass | pass | 0 | 工程表述已移除；分析建议结构完整；报告分节完整 |
| sample_05_dental_recall | `pp_7f061432` | `run_8c9a4eaf` | `run_baca3319` | `run_e84789ba` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1174 | pass | pass | pass | 0 | 工程表述已移除；分析建议结构完整；报告分节完整 |
| sample_06_project_quote_followup | `pp_70abdac1` | `run_62a73733` | `run_f5a9b8df` | `run_45b6d6f4` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1163 | pass | pass | pass | 0 | 工程表述已移除；分析建议结构完整；报告分节完整 |
| sample_07_export_inquiry_followup | `pp_c495169e` | `run_025f2e05` | `run_723afed5` | `run_914aa848` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1169 | pass | pass | pass | 0 | 工程表述已移除；分析建议结构完整；报告分节完整 |
| sample_08_local_service_scheduling | `pp_99960dea` | `run_b825e27c` | `run_5d14365d` | `run_4181bd27` | pl=succeeded;lead=succeeded;report=succeeded | ready_for_confirmation -> confirmed | 4/4 | 1204 | pass | pass | pass | 0 | 工程表述已移除；分析建议结构完整；报告分节完整 |

---

## 5. 汇总判断

- product_learning failed：0/8
- ready_for_confirmation before confirm：8/8
- required_fields_filled：8/8 为 4/4
- lead_analysis relevance pass：8/8
- lead_analysis actionability pass：8/8
- report readability pass：8/8
- hallucination_count total：0
- product_learning LLM token total：9233
- product_learning LLM token average：约 1154 / 样例

本轮达到验收线。

---

## 6. 发现与修复

初始 eval 发现：

- 8/8 样例的 product_learning、lead_analysis、report_generation 都成功。
- 但 report readability 初始为 0/8。
- 原因是 lead_analysis / report_generation 暴露了 `Phase 1`、`LangGraph`、`v1_langgraph_phase1` 等用户可见工程表述。

本任务内做了最小修复：

- 将 lead_analysis 的工程说明替换为用户可理解的“后续可结合更多真实客户反馈和外部市场资料继续校准优先级”。
- 将 limitations 中的 runtime 说明替换为“当前分析主要基于已确认的产品画像，尚未接入外部检索和长期客户反馈”。
- 将 `analysis_scope` 改为 `基于已确认产品画像的获客方向分析`。

修复后复用同一批 ProductProfile 重新跑 lead_analysis / report_generation，report readability 变为 8/8 pass。

---

## 7. 结论

当前 V1 全链路在 8 个真实中文业务样例上可稳定跑通，product learning LLM 输出稳定，lead_analysis 和 report_generation 在去除工程表述后具备基础可读性和相关性。

后续如果继续提升产品价值，优先方向不是继续修链路，而是提升 lead_analysis 的分析深度，例如接入 LLM draft 或更丰富的行业/客户证据。
