# Handoff：2026-04-24 Runtime Observability / Eval Baseline

## 本次变更

- 新增 `docs/reference/runtime-v1-observability-eval-baseline.md`
- 冻结 `AgentRun.runtime_metadata` 的最小 baseline：
  - `provider`
  - `mode`
  - `phase`
  - `graph_name`
  - `run_type`
  - `trace_id`
  - `prompt_version`
  - `round_index`
- 冻结 product learning 的最小样例集为 3 组
- 冻结人工 eval 的最小记录维度为 4 项
- 明确当前不引入 Langfuse、OTEL、外部 eval 平台或自动评分器

## 主要文件

- `docs/reference/runtime-v1-observability-eval-baseline.md`
- `docs/reference/README.md`
- `docs/architecture/runtime/langgraph-runtime-architecture.md`
- `docs/delivery/tasks/task_v1_runtime_observability_eval_baseline.md`
- `docs/delivery/tasks/_active.md`

## 为什么这么定

- 当前 `product_learning` 接入真实 LLM 前，最大的风险不是“接不上模型”，而是“接上以后无法判断是否更好”
- 先补 metadata baseline 和样例集，后续 LLM task 才能在同一套约束下做对比
- 当前阶段仍应保持最小 blast radius，不应过早进入外部 observability 平台建设

## 验证

- `git diff --check`
- 交叉检查 reference、architecture、task queue 已对齐到同一套 baseline

## 已知限制

- 本轮只冻结 baseline，不实现 backend metadata 字段补齐
- heuristic 样例结果记录仍留给下一条 LLM task 顺手完成
- analysis/report 暂未要求维护独立样例集

## 建议下一步

- 进入 `task_v1_product_learning_llm_phase1.md`
