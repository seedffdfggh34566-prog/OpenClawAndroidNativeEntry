# Task：V1 Product Learning Runtime Follow-up

更新时间：2026-04-24

## 1. 任务定位

- 任务名称：V1 Product Learning Runtime Follow-up
- 建议路径：`docs/delivery/tasks/task_v1_product_learning_runtime_followup.md`
- 当前状态：`planned`
- 优先级：P1

本任务用于在产品学习交互基线与 runtime Phase 1 已收口后，继续把 product learning 从“页面与对象门控”推进到“真实 runtime 驱动的产品学习流程”。

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：
  1. 视实现结果再拆 observability 或 product learning API follow-up
- 停止条件：
  - 需要改变 V1 范围、最低完整度门槛或 ADR 基线
  - 需要新增高风险生命周期状态或独立基础设施
  - 需要正式新增 `ProductLearningRun` 但对象语义未冻结

---

## 2. 任务目标

在不突破当前 V1 边界的前提下，明确并实现：

- product learning runtime 的最小 graph / agent flow
- `ready_for_confirmation` 的判断边界
- 是否继续复用 `AgentRun`，还是新增独立 `ProductLearningRun`
- product learning draft 与正式 `ProductProfile` 的写回边界

---

## 3. 当前背景

当前已经完成：

- 产品学习交互基线冻结
- `lead_analysis` / `report_generation` 的 LangGraph Phase 1 接入

当前仍未完成：

- 真实 product learning runtime
- `ready_for_confirmation` 的正式归属
- product learning 独立 run object 是否必要

---

## 4. 范围

本任务 In Scope：

- product learning runtime follow-up 设计与实现
- 最小状态门控与 draft 生成
- 相关 task / handoff / docs 对齐

本任务 Out of Scope：

- CRM、联系人抓取、自动触达
- 新的基础设施基线
- 流式 UI、大规模多轮记忆

---

## 5. 验收标准

满足以下条件可认为完成：

1. product learning runtime 的最小执行路径已形成
2. `ready_for_confirmation` 判断边界已冻结
3. 正式对象写回所有权仍在 backend product services
4. 对象与生命周期文档保持一致

---

## 6. 风险与注意事项

- 不要为了 product learning 直接扩大成完整聊天客户端
- 不要让 runtime 直接成为 formal truth layer
- 若新增正式对象，应先明确对象语义与状态边界
