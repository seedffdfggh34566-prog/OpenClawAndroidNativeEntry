# Product Learning LLM Eval：2026-04-25

## 1. 评估定位

本记录用于验证 `minimax-m2.5 + product_learning_llm_v1` 在 V1 product learning 场景下的真实样例稳定性。

本次评估发生在完整 V1 真机端到端 smoke 已跑通之后，目标是确认当前 product learning LLM 是否需要进入 prompt tuning。

---

## 2. 执行环境

- provider：腾讯云 TokenHub
- model：`minimax-m2.5`
- prompt_version：`product_learning_llm_v1`
- backend DB：`/tmp/openclaw_product_learning_eval_2026_04_25.db`
- API key：从 `backend/.env` 读取，未写入文档或日志
- 执行方式：真实 backend API，`POST /product-profiles` + `POST /product-profiles/{id}/enrich`

说明：

- 当前 API response / AgentRun detail 未暴露 token usage。
- `TokenHubClient` 内部可获得 usage，但当前服务层未写入 runtime metadata 或 public API。
- 因此本次 `token_usage` 统一记录为 `not_exposed`。

---

## 3. 样例输入

| sample_id | 类型 | name | one_line_description | source / supplemental notes |
|---|---|---|---|---|
| sample_a | create | AI 销售助手 V1 | 帮助创业团队先讲清产品，再生成获客分析和结构化报告 | 适合销售负责人、创始人、早期商业化团队；重点关注客户是谁、典型场景和为什么买。 |
| sample_b | create | 工厂设备巡检助手 | 帮助工厂班组记录巡检结果、发现异常并沉淀维修线索 | 主要给设备主管和维修负责人使用；适用于制造工厂；当前仍缺更完整销售材料。 |
| sample_c | create | 门店经营看板 | 帮助连锁门店老板查看营收、库存和员工排班异常 | 适合门店老板和区域运营；强调日常经营异常处理；当前没有完整价格与部署材料。 |
| sample_d | create | 招生线索跟进助手 | 帮助教育培训机构整理试听线索、跟进家长咨询并提醒课程顾问下一步动作 | 适合 K12 素质教育、职业培训和成人学习机构；重点解决线索遗漏、顾问跟进不及时、试听后转化记录分散。 |
| sample_e | create | 门店会员复购助手 | 帮助本地生活门店沉淀会员标签、识别沉睡客户并组织复购活动 | 适合美容美发、健身房、宠物店和社区零售门店；关注会员分层、消费频次下降提醒、活动触达和到店复购。 |
| sample_f | create | 工业备件询价管理工具 | 帮助工贸企业统一管理备件询价、供应商报价和采购跟进记录 | 适合卖工业备件、MRO 耗材和设备配件的 B2B 团队；痛点是微信群报价混乱、历史价格难查、采购进度不透明。 |
| sample_b | enrich | 工厂设备巡检助手 | 同 create | 补充：重点服务离散制造、机械加工和设备密集型工厂；核心痛点是纸质巡检漏项、故障记录分散、维修响应慢；优势是低成本部署、移动端离线可用、现场照片和维修闭环。 |
| sample_c | enrich | 门店经营看板 | 同 create | 补充：多门店老板需要按门店、员工和品类查看异常；希望识别库存预警、会员消费频次下降和复购活动效果；暂不做复杂 ERP 替换。 |

---

## 4. 评估结果

| sample_id | profile_id | run_id | round_index | model | prompt_version | agent_run_status | learning_stage | required_fields_filled | hallucination_count | token_usage | review_note |
|---|---|---|---:|---|---|---|---|---|---:|---|---|
| sample_a | `pp_494cdea2` | `run_00bc5cb8` | 0 | minimax-m2.5 | product_learning_llm_v1 | succeeded | ready_for_confirmation | 4/4 | 0 | not_exposed | 企业服务 / 销售场景识别清楚，未见明显行业偏移。 |
| sample_b | `pp_018d0fc9` | `run_88b687fc` | 0 | minimax-m2.5 | product_learning_llm_v1 | succeeded | ready_for_confirmation | 4/4 | 0 | not_exposed | 制造业、设备主管、巡检维修场景识别清楚。 |
| sample_c | `pp_6ef0f201` | `run_3fb6b500` | 0 | minimax-m2.5 | product_learning_llm_v1 | succeeded | ready_for_confirmation | 4/4 | 0 | not_exposed | 门店经营、零售连锁和异常处理表达合理。 |
| sample_d | `pp_69176256` | `run_098b11e2` | 0 | minimax-m2.5 | product_learning_llm_v1 | succeeded | ready_for_confirmation | 4/4 | 0 | not_exposed | 教育培训、课程顾问和试听转化场景识别合理。 |
| sample_e | `pp_a15e88d6` | `run_ad8d026d` | 0 | minimax-m2.5 | product_learning_llm_v1 | succeeded | ready_for_confirmation | 4/4 | 0 | not_exposed | 本地服务门店、会员分层和复购场景识别合理。 |
| sample_f | `pp_809e0757` | `run_e255a17e` | 0 | minimax-m2.5 | product_learning_llm_v1 | succeeded | ready_for_confirmation | 4/4 | 0 | not_exposed | 工业备件、供应商报价和采购跟进场景识别合理。 |
| sample_b | `pp_018d0fc9` | `run_b625a20e` | 1 | minimax-m2.5 | product_learning_llm_v1 | succeeded | ready_for_confirmation | 4/4 | 0 | not_exposed | enrich 后字段继续收敛，补充信息被吸收。 |
| sample_c | `pp_6ef0f201` | `run_01b41486` | 1 | minimax-m2.5 | product_learning_llm_v1 | succeeded | ready_for_confirmation | 4/4 | 0 | not_exposed | enrich 后字段继续收敛，补充信息被吸收。 |

---

## 5. 触发规则判断

本次未触发 prompt tuning：

- 6 个 create 样例中 `AgentRun.failed = 0`
- `required_fields_filled < 4/4` 的样例数为 0
- 明显幻觉字段总数为 0
- Sample A 未再次出现稳定偏窄或错误行业归类

因此：

- 不创建 `product_learning_llm_v1_1`
- 不修改 `backend/runtime/graphs/product_learning.py`
- 不切换默认模型
- 不跑 `kimi-k2.5` / `glm-5` 对照

---

## 6. 结论

`minimax-m2.5 + product_learning_llm_v1` 在本轮 6 个 create 样例和 2 个 enrich 样例中表现稳定，可继续作为 V1 product learning 默认 baseline。

下一步如果继续提升质量，建议优先增加真实业务样例覆盖，而不是立即调 prompt 或切换模型。
