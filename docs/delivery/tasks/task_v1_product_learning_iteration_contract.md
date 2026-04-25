# Task：V1 Product Learning Iteration Contract

更新时间：2026-04-24

## 1. 任务定位

- 任务名称：V1 Product Learning Iteration Contract
- 建议路径：`docs/delivery/tasks/task_v1_product_learning_iteration_contract.md`
- 当前状态：`done`
- 优先级：P0

本任务用于在当前 single-turn enrich 已落地后，先冻结 product learning 下一轮迭代的 public contract、对象边界和交互承载方式，再进入新的 runtime 或 Android 实现。

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：
  1. `docs/delivery/tasks/task_v1_runtime_observability_eval_baseline.md`
  2. `docs/delivery/tasks/task_v1_product_learning_llm_phase1.md`
- 停止条件：
  - 需要改变 ADR-002 / ADR-003 的边界
  - 需要把 V1 扩大成完整聊天协议或消息持久化系统
  - 需要引入新的正式对象而不只是扩展现有 contract

---

## 2. 任务目标

冻结下一轮 product learning 的最小 contract，至少明确：

1. 是否新增 `POST /product-profiles/{id}/enrich`
2. 是否继续只复用 `AgentRun`
3. 单轮 enrich 的请求/响应 schema
4. enrich 的写回规则是“补空优先”还是允许有限覆盖
5. `learning_stage` 与 `ProductProfile.status` 的关系是否保持不变
6. Android 如何承接“继续补充信息”的最小交互，而不立即引入完整消息系统

---

## 3. 当前背景

当前已完成：

- `POST /product-profiles` 创建即触发 `product_learning`
- backend 派生 `learning_stage`
- `ready_for_confirmation` 门控与 Android 最小轮询链路

当前缺口在于：

- 用户只能“创建一次然后等待富化”
- 没有正式定义“继续补充一轮信息”的 contract
- 若直接进入 LLM 或 UI 迭代，容易出现 API、对象边界和端侧交互各自发散

因此，本任务必须先完成 docs-only 冻结。

---

## 4. 范围

本任务 In Scope：

- product learning 迭代入口 contract 冻结
- backend / Android / runtime 边界澄清
- reference / architecture / PRD 相关文档同步
- `_active.md` 与下游任务的衔接修正

本任务 Out of Scope：

- backend API 代码实现
- Android UI 代码实现
- 真实 LLM 接入
- observability 平台建设
- 多轮聊天消息持久化

---

## 5. 涉及文件

高概率涉及：

- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/reference/schemas/v1-domain-model-baseline.md`
- `docs/architecture/system-context.md`
- `docs/architecture/clients/mobile-information-architecture.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/architecture/runtime/langgraph-runtime-architecture.md`
- `docs/adr/*`（如需新增 ADR）

参考文件：

- `docs/delivery/tasks/task_v1_product_learning_runtime_followup.md`
- `docs/adr/ADR-003-v1-product-learning-runtime-boundary.md`

---

## 6. 产出要求

至少应产出：

1. 一份明确的 iteration contract 方案
2. 对现有 8 个 public endpoint 是否扩展的明确结论
3. 对 `AgentRun`、`learning_stage`、写回规则的正式说明
4. 一份 handoff，说明为何选择该 contract

---

## 7. 验收标准

满足以下条件可认为完成：

1. 仓库主文档明确 product learning 下一轮入口方案
2. 文档明确是否新增 `POST /product-profiles/{id}/enrich`
3. 文档明确继续复用 `AgentRun`
4. 文档明确 backend 仍是 `learning_stage` 判定方
5. 文档明确 Android 只消费 backend 阶段表达，不自行推断
6. `git diff --check` 通过

---

## 8. 推荐执行顺序

建议执行顺序：

1. 先审查 ADR-003 与当前 follow-up 实现边界
2. 明确 iteration 是“轻量 enrich”还是“完整聊天”
3. 冻结 endpoint / payload / writeback 规则
4. 同步 reference、architecture、PRD、mobile IA
5. 更新 `_active.md` 与下游任务描述

---

## 9. 风险与注意事项

- 不要把本任务扩大成 LLM 实现
- 不要提前引入 ProductLearning message object
- 不要为了 Android 方便就把规则推给客户端
- 若新增 endpoint，必须解释为何现有 `POST /product-profiles` 已不足够

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. `docs/delivery/tasks/task_v1_runtime_observability_eval_baseline.md`
2. `docs/delivery/tasks/task_v1_product_learning_llm_phase1.md`

---

## 11. 实际产出

- `docs/adr/ADR-004-v1-product-learning-iteration-contract.md`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/reference/schemas/v1-domain-model-baseline.md`
- `docs/architecture/system-context.md`
- `docs/architecture/clients/mobile-information-architecture.md`
- `docs/architecture/runtime/langgraph-runtime-architecture.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/product/overview.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/handoffs/handoff_2026_04_24_product_learning_iteration_contract.md`

---

## 12. 本次定稿边界

- 默认新增 `POST /product-profiles/{id}/enrich`
- iteration 继续复用 `AgentRun`
- enrich 请求体固定为 `supplemental_notes + trigger_source`
- backend 先把 `supplemental_notes` 追加到 `ProductProfile.source_notes`
- 写回规则固定为“补空优先，有限覆盖弱默认值”
- Android 只承接轻量 iteration 交互，不引入消息持久化

---

## 13. 已做验证

- `git diff --check`
- 交叉检查 PRD / system-context / mobile IA / API contract / runtime architecture 已对齐到 `ADR-004`

---

## 14. 实际结果说明

- 仓库已正式冻结下一轮 product learning iteration contract
- `POST /product-profiles/{id}/enrich` 已成为默认下一轮接口方向
- 当前下一条 queued task 已切到 `task_v1_runtime_observability_eval_baseline.md`
