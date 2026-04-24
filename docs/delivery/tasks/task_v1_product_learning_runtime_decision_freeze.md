# Task：V1 Product Learning Runtime 决策冻结

更新时间：2026-04-24

## 1. 任务定位

- 任务名称：V1 Product Learning Runtime 决策冻结
- 建议路径：`docs/delivery/tasks/task_v1_product_learning_runtime_decision_freeze.md`
- 当前状态：`done`
- 优先级：P0

本任务用于在进入 product learning runtime 实现前，先把对象边界、阶段判定、接口承载与第一版实现形态冻结为正式仓库基线。

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：
  1. `docs/delivery/tasks/task_v1_product_learning_runtime_followup.md`
- 停止条件：
  - 需要改变 V1 范围或 ADR 基线
  - 需要新增独立 public endpoint
  - 需要新增独立 product learning run 正式对象
  - 需要引入新的 lifecycle 或基础设施

---

## 2. 任务目标

本任务冻结以下 4 项决策：

1. 继续复用 `AgentRun`
2. `ready_for_confirmation` 由 backend product services 判定
3. backend 显式暴露 `learning_stage`
4. 第一版 product learning runtime 采用 single-turn enrich，并复用现有 public API

---

## 3. 当前背景

当前已经完成：

- 产品学习交互基线冻结
- `lead_analysis` / `report_generation` 的 LangGraph Phase 1 接入

当前仍存在的风险是：

- product learning run 边界仍可能被解释成新增正式对象
- backend 与客户端可能分别推断阶段状态
- 第一版 product learning runtime 可能被扩大成多轮聊天 API

因此，在进入实现前，需要先完成一轮 docs-only 决策冻结。

---

## 4. 范围

本任务 In Scope：

- 新增 product learning runtime boundary ADR
- 改写 follow-up task 为纯实现任务
- 同步 PRD / system-context / mobile IA / reference docs
- 更新 `_active.md`、roadmap、docs 导航与 handoff

本任务 Out of Scope：

- backend 代码实现
- Android UI 改造
- 新增 public endpoint
- 新 lifecycle 或新基础设施

---

## 5. 验收标准

满足以下条件可认为完成：

1. 仓库明确只保留 `ProductProfile / LeadAnalysisResult / AnalysisReport / AgentRun`
2. 文档明确 product learning 继续复用 `AgentRun`
3. 文档明确 `ready_for_confirmation` 是 backend 派生阶段，而不是正式对象状态
4. 文档明确 backend 暴露 `learning_stage`
5. 文档明确第一版 product learning runtime 采用 single-turn enrich
6. `task_v1_product_learning_runtime_followup.md` 被改写为纯实现任务
7. `git diff --check` 通过

---

## 6. 风险与注意事项

- 不要把这轮 docs 收口扩大成 product learning 代码实现
- 不要把产品学习阶段字段写成新的正式对象状态
- 不要在未定义必要契约前引入新的 public endpoint

---

## 7. 实际产出

- `docs/adr/ADR-003-v1-product-learning-runtime-boundary.md`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/reference/schemas/v1-domain-model-baseline.md`
- `docs/architecture/runtime/langgraph-runtime-architecture.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/architecture/system-context.md`
- `docs/architecture/clients/mobile-information-architecture.md`
- `docs/delivery/tasks/task_v1_product_learning_runtime_followup.md`
- `docs/delivery/handoffs/handoff_2026_04_24_product_learning_runtime_decision_freeze.md`

---

## 8. 已做验证

1. `git diff --check` 通过
2. 全仓搜索不再保留本轮需要消除的未定表述

---

## 9. 实际结果说明

- V1 已正式固定复用 `AgentRun`
- backend 已被定义为 `learning_stage` 的唯一判定与暴露方
- 第一版 product learning runtime 已正式固定为 single-turn enrich + 现有 API 承载
