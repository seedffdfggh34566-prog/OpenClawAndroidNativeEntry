# V1 Runtime Observability / Eval Baseline

更新时间：2026-04-24

## 1. 文档定位

本文档用于冻结 V1 当前阶段的最小 runtime observability 与人工 eval baseline。

它服务于以下后续工作：

- `product_learning` 接入真实 LLM 前的 baseline 对齐
- `lead_analysis` / `report_generation` / `product_learning` 的 runtime metadata 一致化
- 样例集与人工评估记录方式统一

本文档不是：

- Langfuse / OTEL / 外部 tracing 平台方案
- 自动 benchmark 系统设计
- 模型选择文档

---

## 2. 当前结论

当前阶段固定以下 baseline：

1. `AgentRun.runtime_metadata` 采用统一最小字段集
2. `trace_id` 继续作为 runtime trace 的最小主键
3. `prompt_version` 与 `round_index` 进入 metadata baseline
4. product learning 至少维护 3 组固定样例输入
5. 样例结果至少按 4 个维度人工记录

当前明确不做：

- Langfuse
- OpenTelemetry
- 外部 dataset/eval 平台
- 自动评分器

---

## 3. Runtime Metadata Baseline

### 3.1 必填字段

所有 `AgentRun.runtime_metadata` 至少应包含：

- `provider`
- `mode`
- `phase`
- `graph_name`
- `run_type`
- `trace_id`

### 3.2 新增 baseline 字段

从本轮起，以下字段也应进入最小 baseline：

- `prompt_version`
- `round_index`

### 3.3 字段含义

- `provider`：当前 runtime provider，例如 `langgraph`
- `mode`：当前执行模式，例如 `backend_direct_langgraph`
- `phase`：当前阶段标签，例如 `phase1`、`product_learning_followup`、`llm_phase1`
- `graph_name`：实际执行 graph 名称
- `run_type`：`product_learning` / `lead_analysis` / `report_generation`
- `trace_id`：一次运行的最小 trace 标识
- `prompt_version`：当前 prompt / generation 策略版本号
- `round_index`：当前是第几轮 product learning iteration

### 3.4 默认值约束

当前默认约束如下：

- `prompt_version`
  - heuristic 阶段：`heuristic_v1`
  - product learning LLM phase 1：`product_learning_llm_v1`
  - lead analysis / report generation 当前可先写 `heuristic_v1`
- `round_index`
  - `POST /product-profiles` 首轮创建：`0`
  - `POST /product-profiles/{id}/enrich` 的第一次补充：`1`
  - 后续 iteration 依次递增

### 3.5 失败路径补充字段

失败时继续允许补充：

- `error_type`

### 3.6 Product Learning LLM usage

product learning 使用真实 LLM 成功返回时，应在 `AgentRun.runtime_metadata.llm_usage` 中记录非敏感 token 统计：

- `prompt_tokens`
- `completion_tokens`
- `total_tokens`
- `cached_tokens`，如供应商返回
- `reasoning_tokens`，如供应商返回

不记录：

- prompt 原文
- 用户输入全文
- API key 或其他 secret

当前不强制补：

- model latency breakdown
- tool call list
- full prompt replay

---

## 4. Product Learning 样例集 Baseline

当前最小样例集固定为 3 组，先服务 V1 的产品学习质量验证。

### Sample A：企业服务 SaaS

- `name`：AI 销售助手 V1
- `one_line_description`：帮助创业团队先讲清产品，再生成获客分析和结构化报告
- `source_notes`：适合销售负责人、创始人、早期商业化团队；重点关注客户是谁、典型场景和为什么买
- 预期：
  - 能补齐 `target_customers`
  - 能生成至少 1 条 `typical_use_cases`
  - `learning_stage` 应达到 `ready_for_confirmation`

### Sample B：制造业软件工具

- `name`：工厂设备巡检助手
- `one_line_description`：帮助工厂班组记录巡检结果、发现异常并沉淀维修线索
- `source_notes`：主要给设备主管和维修负责人使用；适用于制造工厂；当前仍缺更完整销售材料
- 预期：
  - 能识别制造业 / 工厂相关行业
  - 能补齐痛点与场景
  - 若限制信息不足，允许仍保留 `collecting`

### Sample C：零售运营工具

- `name`：门店经营看板
- `one_line_description`：帮助连锁门店老板查看营收、库存和员工排班异常
- `source_notes`：适合门店老板和区域运营；强调日常经营异常处理；当前没有完整价格与部署材料
- 预期：
  - 能识别门店 / 零售连锁场景
  - 能生成较合理的 `target_customers` 与 `typical_use_cases`
  - 缺失字段应主要收敛到 `constraints` 或其他非必填项

---

## 5. 人工 Eval 维度

每组样例至少记录以下 4 个维度：

1. **必填字段补齐率**
   - 统计：
     - `target_customers`
     - `typical_use_cases`
     - `pain_points_solved`
     - `core_advantages`
   - 结果可写为 `0/4` 到 `4/4`

2. **`ready_for_confirmation` 命中情况**
   - 记录：
     - `match`
     - `too_early`
     - `too_late`

3. **明显错误 / 幻觉字段数**
   - 只统计人工可直接判断明显不成立的字段
   - 结果写整数：`0 / 1 / 2...`

4. **人工 review note**
   - 一句话说明：
     - 哪些字段最好
     - 哪些字段需要下轮调整

---

## 6. 结果记录格式

当前建议用 Markdown 表格记录最小结果：

| sample_id | run_type | prompt_version | round_index | required_fields_filled | ready_stage_judgement | hallucination_count | review_note |
|---|---|---|---:|---|---|---:|---|
| sample_a | product_learning | heuristic_v1 | 0 | 4/4 | match | 0 | 目标客户和场景清楚，限制项仍偏弱 |

说明：

- `run_type` 当前主要记录 `product_learning`
- 后续如需扩展到 `lead_analysis` / `report_generation`，可复用同一表头
- 当前不要求把结果落数据库，允许先保存在 handoff / reference / research 文档中

---

## 7. 与后续任务的关系

### 7.1 对 LLM Phase 1 的约束

`task_v1_product_learning_llm_phase1.md` 实施时，默认必须：

- 为 `product_learning` 补齐 `prompt_version`
- 为 create / enrich 维护 `round_index`
- 至少用本文件样例集做一次 heuristic vs LLM 对比

### 7.2 当前不要求的能力

本 baseline 当前不要求：

- 线上监控看板
- prompt diff 平台
- 节点级 trace UI
- 自动回归平台

---

## 8. 当前最小执行建议

在真实 LLM 接入前，建议执行顺序为：

1. 先让 `runtime_metadata` baseline 进入实现与测试
2. 再为 product learning 建立样例输入
3. 然后记录 heuristic baseline
4. 最后在 LLM phase 1 中做最小对比
