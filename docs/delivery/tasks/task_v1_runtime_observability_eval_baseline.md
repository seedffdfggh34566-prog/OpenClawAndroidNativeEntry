# Task：V1 Runtime Observability And Eval Baseline

更新时间：2026-04-24

## 1. 任务定位

- 任务名称：V1 Runtime Observability And Eval Baseline
- 建议路径：`docs/delivery/tasks/task_v1_runtime_observability_eval_baseline.md`
- 当前状态：`planned`
- 优先级：P1

本任务用于在 product learning 接入真实 LLM 前，先建立最小可观测性和最小评估基线，避免后续只有“能跑通”而没有“能判断质量是否更好”。

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/task_v1_product_learning_iteration_contract.md`
- 建议下游任务：
  1. `docs/delivery/tasks/task_v1_product_learning_llm_phase1.md`
- 停止条件：
  - 需要引入 Langfuse、OpenTelemetry、队列系统或新的平台基线
  - 需要把 eval 扩大成长期 benchmark 平台
  - 需要改动当前正式 API 语义

---

## 2. 任务目标

为 runtime 与 product learning 建立最小、可执行的观测与评估基线，至少包含：

1. `AgentRun.runtime_metadata` 最小字段约束
2. product learning / lead analysis / report generation 的统一 trace 信息
3. 一组固定样例输入
4. 最小人工评估维度与记录方式

---

## 3. 当前背景

当前已经有：

- `AgentRun.runtime_metadata`
- `graph_name / run_type / trace_id`
- LangGraph runtime graph

但当前还没有：

- 统一的 metadata 最小字段清单
- 针对 product learning 质量的固定样例集
- “这次换成 LLM 后到底更好还是更差”的判断标准

如果跳过这一步，后续 LLM 接入只能凭主观感觉推进。

---

## 4. 范围

本任务 In Scope：

- 最小 observability 字段规范
- 样例集与人工评估模板
- handoff / runbook / architecture 文档同步
- 如有必要，补一个轻量参考文档放在 `docs/how-to/` 或 `docs/reference/`

本任务 Out of Scope：

- Langfuse / OTEL / 外部 tracing 平台接入
- 大规模 benchmark 系统
- 自动评分平台
- Android UI 改造
- 真实 LLM 接入

---

## 5. 涉及文件

高概率涉及：

- `docs/architecture/runtime/langgraph-runtime-architecture.md`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/how-to/*`
- `docs/reference/*`
- `docs/delivery/handoffs/*`

参考文件：

- `docs/delivery/tasks/task_v1_real_runtime_integration_phase1.md`
- `docs/delivery/tasks/task_v1_product_learning_runtime_followup.md`

---

## 6. 产出要求

至少应产出：

1. runtime metadata baseline
2. 样例输入集定义
3. 人工评估维度定义
4. 执行与记录方式说明

---

## 7. 验收标准

满足以下条件可认为完成：

1. 仓库中明确记录 runtime metadata 最小字段
2. 至少定义一组固定 product learning 样例输入
3. 至少定义以下评估维度：
   - 必填字段补齐率
   - `ready_for_confirmation` 命中情况
   - 明显错误或幻觉字段数
   - 人工 review note
4. 文档明确本阶段不引入重型 observability 平台
5. `git diff --check` 通过

---

## 8. 推荐执行顺序

建议执行顺序：

1. 审查当前 runtime metadata 已有哪些字段
2. 冻结最小 metadata baseline
3. 定义 product learning 样例集
4. 定义人工评估模板
5. 更新 handoff / runbook / architecture 文档

---

## 9. 风险与注意事项

- 不要把“最小 observability”扩大成平台工程
- 不要为了 eval 引入新的正式对象
- 样例集应该服务 V1，不要一开始覆盖过宽行业

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. `docs/delivery/tasks/task_v1_product_learning_llm_phase1.md`

---

## 11. 实际产出

任务执行完成后补充。

---

## 12. 本次定稿边界

任务执行完成后补充。

---

## 13. 已做验证

任务执行完成后补充。

---

## 14. 实际结果说明

任务执行完成后补充。
