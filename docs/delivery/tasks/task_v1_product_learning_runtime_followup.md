# Task：V1 Product Learning Runtime Follow-up

更新时间：2026-04-24

## 1. 任务定位

- 任务名称：V1 Product Learning Runtime Follow-up
- 建议路径：`docs/delivery/tasks/task_v1_product_learning_runtime_followup.md`
- 当前状态：`planned`
- 优先级：P1

本任务用于在产品学习交互基线、runtime Phase 1 与 product learning runtime 决策冻结完成后，继续把 product learning 从“页面与对象门控”推进到“真实 runtime 驱动的产品学习流程”。

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/task_v1_product_learning_runtime_decision_freeze.md`
- 建议下游任务：
  1. 视实现结果再拆 observability 或 product learning public endpoint follow-up
- 停止条件：
  - 需要改变 V1 范围、最低完整度门槛或 ADR 基线
  - 需要新增高风险生命周期状态或独立基础设施
  - 需要新增独立 public endpoint 或更重的多轮聊天协议

---

## 2. 任务目标

在不突破当前 V1 边界的前提下，实现：

- product learning runtime 的最小 graph / agent flow
- `learning_stage` 的 backend 写回与对外暴露
- `product_learning` run type 的最小执行闭环
- product learning draft 与正式 `ProductProfile` 的写回边界

---

## 3. 当前背景

当前已经完成：

- 产品学习交互基线冻结
- `lead_analysis` / `report_generation` 的 LangGraph Phase 1 接入
- product learning runtime boundary 决策冻结

当前仍未完成：

- 真实 product learning runtime
- `product_learning` run type 的正式实现
- `learning_stage` 的接口与客户端接线

---

## 4. 范围

本任务 In Scope：

- product learning runtime follow-up 实现
- 复用 `POST /product-profiles` + `GET /analysis-runs/{id}` 的最小闭环
- 最小状态门控、draft 生成与 `learning_stage` 写回
- 相关 task / handoff / docs 对齐

本任务 Out of Scope：

- CRM、联系人抓取、自动触达
- 新的基础设施基线
- 流式 UI、大规模多轮记忆
- 新 public endpoint
- 多轮聊天 API

---

## 5. 验收标准

满足以下条件可认为完成：

1. product learning runtime 的最小执行路径已形成
2. `product_learning` 继续复用 `AgentRun`
3. `learning_stage` 由 backend 写回并对外暴露
4. 正式对象写回所有权仍在 backend product services
5. 对象与生命周期文档保持一致

---

## 6. 风险与注意事项

- 不要为了 product learning 直接扩大成完整聊天客户端
- 不要让 runtime 直接成为 formal truth layer
- 不要顺手新增独立 product learning run 正式对象
- 不要顺手新增 public endpoint 或 lifecycle

---

## 7. 默认实现路径

当前默认实现路径固定为：

1. `POST /product-profiles` 创建初始 `ProductProfile` draft
2. backend 立即创建 `run_type = product_learning` 的 `AgentRun`
3. runtime 执行 single-turn enrich
4. backend 写回同一个 `ProductProfile`
5. backend 基于完整度计算 `learning_stage`
6. 客户端轮询 `GET /analysis-runs/{id}` 并读取 `GET /product-profiles/{id}`

---

## 8. 预期接口与类型变更

实现本任务时，默认应补：

- `RunType` 新增 `product_learning`
- `ProductProfileSummary` 新增 `learning_stage`
- `ProductProfileDetail` 新增 `learning_stage`
- `POST /product-profiles` 的 `current_run` 允许返回非空 `AgentRun`

当前不补：

- `/product-learning/*`
- `waiting_for_user / paused / resumed`
- 独立聊天消息对象
