# Handoff：2026-04-24 Product Learning Iteration Contract

## 本次变更

- 新增 `ADR-004`，冻结下一轮 product learning iteration contract
- 明确默认新增 `POST /product-profiles/{id}/enrich`
- 明确 iteration 继续复用 `AgentRun`
- 明确 enrich 请求体固定为：
  - `supplemental_notes`
  - `trigger_source`
- 明确 backend 在创建 `product_learning` `AgentRun` 前，先将补充文本追加到同一个 `ProductProfile.source_notes`
- 明确写回规则固定为：
  - 补空优先
  - 有限覆盖弱默认值
  - `missing_fields` 与 `learning_stage` 继续由 backend 重算
- 明确 Android 只承接轻量 iteration 交互，不引入消息持久化

## 主要文件

- `docs/adr/ADR-004-v1-product-learning-iteration-contract.md`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/reference/schemas/v1-domain-model-baseline.md`
- `docs/architecture/system-context.md`
- `docs/architecture/clients/mobile-information-architecture.md`
- `docs/architecture/runtime/langgraph-runtime-architecture.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/product/overview.md`
- `docs/delivery/tasks/task_v1_product_learning_iteration_contract.md`
- `docs/delivery/tasks/_active.md`

## 为什么这么定

- single-turn enrich 已经跑通，下一阶段的主要风险变成“继续补充一轮信息”没有正式 contract
- 若直接进入 LLM 或 Android UI，执行层必须自行决定 endpoint、请求体、写回规则和端侧交互，后续返工概率很高
- 先冻结 enrich contract，能让后续 observability、LLM 与 Android 都建立在同一套边界上

## 验证

- `git diff --check`
- 交叉检查 PRD / system-context / mobile IA / API contract / runtime architecture 与 ADR-004 一致

## 已知限制

- 本轮只冻结 contract，不实现 backend enrich endpoint
- `prompt_version`、`round_index` 等 metadata baseline 留给下一条 observability task
- analysis/report 路线不在本轮调整

## 建议下一步

- 进入 `task_v1_runtime_observability_eval_baseline.md`
