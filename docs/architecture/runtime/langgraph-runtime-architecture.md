# LangGraph Runtime Architecture Spec

更新时间：2026-04-25

## 1. 文档定位

本文档用于定义 V1 当前阶段的 LangGraph runtime 接入方式。

它回答的问题包括：

- LangGraph 在当前仓库中放在哪一层
- 它应该如何与 `AgentRun`、`services.py`、正式对象写回配合
- `lead_analysis` 与 `report_generation` 应该先怎样 graph 化
- 当前阶段不能假设哪些 lifecycle 和平台能力已经存在

本文档不是：

- 对 LangGraph 的通用教程
- 直接替代 task 的实施清单
- 产品学习最终实现文档

---

## 2. 当前目标

当前阶段引入 LangGraph 的目标非常收敛：

> **在不改动产品后端主真相边界的前提下，用 LangGraph 取代 `backend/runtime/adapter.py` 中的 stub execution。**

Phase 1 仅覆盖：

- `lead_analysis`
- `report_generation`

当前不覆盖：

- product learning runtime 的正式实现
- queue worker infrastructure
- 可恢复人工审核流
- 持久化 checkpoint 恢复流程

---

## 3. 系统边界

LangGraph 当前应严格位于：

```text
Android / client
    ->
FastAPI API
    ->
backend/api/services.py
    ->
backend/runtime/ (LangGraph execution layer)
    ->
LLM / search / tool adapters
    ->
structured draft payload
    ->
backend/api/services.py writeback
    ->
formal product objects
```

这意味着：

- LangGraph 是执行编排层
- `FastAPI + services.py` 仍是产品后端主干
- 正式对象主真相仍在 backend models
- runtime 不能直接把结果写进正式业务表

---

## 4. 当前 lifecycle 基线

在 dedicated lifecycle task 之前，LangGraph 接入必须兼容当前已实现的最小 lifecycle：

- `queued`
- `running`
- `succeeded`
- `failed`

当前不应默认引入：

- `waiting_for_user`
- `paused`
- `resumed`
- durable queue worker
- 分布式执行器

如果后续确实需要这些能力，应先拆独立 task / ADR。

---

## 5. 当前推荐模块结构

建议在 `backend/runtime/` 下保持最小、显式的结构：

```text
backend/runtime/
  adapter.py
  types.py
  graphs/
    lead_analysis.py
    report_generation.py
  nodes/
    load_inputs.py
    llm_generate.py
    validate_output.py
  prompts/
    lead_analysis.py
    report_generation.py
```

说明：

- `adapter.py`：对外暴露 runtime provider 接口
- `types.py`：LangGraph state 与 draft payload typing
- `graphs/*`：每种 run_type 一张清晰 graph
- `nodes/*`：复用节点逻辑
- `prompts/*`：把 prompt 从 services 层与 graph wiring 层分离

当前不建议：

- 一开始就做高度泛化的“万能 graph”
- 把所有 run_type 混在一张超图里

---

## 6. 状态模型

当前建议把 LangGraph 内部 state 保持为 typed state，而不是直接传 ORM model。

Phase 1 最小 state 可包含：

- `run_id`
- `run_type`
- `product_profile_id`
- `product_profile_payload`
- `lead_analysis_result_id`（仅 report generation 用）
- `lead_analysis_result_payload`（仅 report generation 用）
- `draft_output`
- `error`
- `runtime_metadata`

product learning follow-up 默认应新增：

- `learning_stage`
- `confidence_score`

建议继续使用 `Pydantic` 作为 schema 核心。

原因：

- 与当前 backend schema core 一致
- 方便把 runtime 输出限制为正式 draft payload
- 可减少 graph state 与 ORM model 的耦合

---

## 7. Graph 设计

### 7.0 product learning 的默认后续落地方式

当前 product learning follow-up 已固定：

- 继续复用 `AgentRun`
- 第一版 create 继续复用原有 public API，iteration 使用已落地的 `POST /product-profiles/{id}/enrich`
- 采用 single-turn enrich
- 由 backend 负责 `learning_stage` 判定与写回

这意味着 product learning 第一版 graph 不应被设计成：

- 多轮聊天 public API
- 独立 product learning run 正式对象
- 新 lifecycle 或人工暂停流

### 7.1 `lead_analysis` graph

Phase 1 推荐最小节点顺序：

1. `load_confirmed_product_profile`
2. `normalize_product_profile_context`
3. `generate_lead_analysis_draft`
4. `validate_lead_analysis_draft`
5. `return_draft_payload`

要求：

- 只接受 `confirmed` `ProductProfile`
- 生成结构化 draft，而不是 markdown blob
- 验证失败直接走 runtime error

### 7.2 `report_generation` graph

Phase 1 推荐最小节点顺序：

1. `load_product_profile_and_analysis_result`
2. `build_report_context`
3. `generate_report_draft`
4. `validate_report_draft`
5. `return_draft_payload`

要求：

- 输入必须包含 `ProductProfile` + `LeadAnalysisResult`
- 输出保持结构化 section-based report draft
- 不把报告导出、文件存储一起塞进这个图

---

## 8. 与 `services.py` 的协作方式

LangGraph 当前不负责正式对象写回。

推荐职责切分如下：

### `backend/api/services.py`

负责：

- 读取 `AgentRun`
- 把 `AgentRun.status` 从 `queued` 推到 `running`
- 调用 runtime provider
- 接收 draft payload
- 校验并创建正式 ORM 对象
- 更新 `output_refs`
- 把 `AgentRun.status` 更新为 `succeeded` / `failed`

### `backend/runtime/`

负责：

- 根据 run_type 选择 graph
- 读取输入上下文
- 调用模型与工具
- 返回 typed draft payload
- 返回最小 runtime metadata

这条边界在 Phase 1 不应改变。

---

## 9. 输出与写回边界

LangGraph 对外输出应是：

- `LeadAnalysisDraft`
- `AnalysisReportDraft`

或等价的 typed draft payload。

不应输出：

- 已经落库的 ORM 对象
- 已经分配版本号的正式对象
- 直接写入数据库后的 object ref

原因：

- 正式对象版本、状态与写回所有权属于产品 backend
- 这能避免 runtime 反向成为 truth layer

---

## 10. 错误与最小可观测性

当前阶段不强求完整 observability 平台，但至少需要：

- `runtime_provider`
- graph 名称或 run_type
- 最小 trace / call id
- 节点失败信息

当前 baseline 已补齐：

- `prompt_version`
- `round_index`

这些信息建议写入：

- `AgentRun.runtime_metadata`
- 结构化日志

具体 baseline 以：

- `docs/reference/runtime-v1-observability-eval-baseline.md`

为准。

---

## 11. Product Learning Follow-up 默认形态

product learning 第一版默认流程为：

1. `POST /product-profiles` 创建初始 draft
2. backend 创建 `run_type = product_learning` 的 `AgentRun`
3. LangGraph 执行单轮富化，并在 LLM Phase 1 中通过 TokenHub `minimax-m2.5` 生成 typed draft
4. runtime 输出 `ProductLearningDraft`、候选 `missing_fields` 与 `confidence_score`
5. backend 写回同一个 `ProductProfile`
6. backend 计算 `learning_stage`
7. 客户端通过现有轮询与详情接口读取结果

当前不做：

- 新增 `/product-learning/*`
- `waiting_for_user / paused / resumed`
- 多轮聊天 public API

## 11.1 Product Learning Iteration 默认形态

在 single-turn enrich 已落地后，下一轮默认流程固定为：

1. 客户端调用 `POST /product-profiles/{id}/enrich`
2. 请求体只承接 `supplemental_notes` 与 `trigger_source`
3. backend 先将 `supplemental_notes` 追加到同一个 `ProductProfile.source_notes`
4. backend 再创建新的 `run_type = product_learning` `AgentRun`
5. LangGraph 继续基于同一个 `ProductProfile` 执行富化
6. runtime 输出新的 `ProductLearningDraft`
7. backend 继续按“补空优先，有限覆盖弱默认值”写回同一个 `ProductProfile`
8. backend 重算 `missing_fields` 与 `learning_stage`
9. 客户端继续通过 `GET /analysis-runs/{id}` 与 `GET /product-profiles/{id}` 读取结果

当前 iteration 仍不引入：

- `/product-learning/messages`
- 新正式对象
- 新 lifecycle

Phase 1 不要求：

- `Langfuse` 必须落地
- 节点级 UI trace 浏览器
- 全量 prompt replay 平台

---

## 11. 验证边界

LangGraph runtime 接入 Phase 1 的最低验证应包括：

1. `backend/.venv/bin/python -m pytest backend/tests`
2. backend 本地启动
3. `/health` smoke
4. 至少一条 `lead_analysis` 手动 API 流验证
5. 至少一条 `report_generation` 手动 API 流验证

若 graph state、writeback boundary 或 `AgentRun` 处理方式变化，应按 runtime boundary 风险处理，而不是只跑 schema 单测。

## 12. 当前落地事实（2026-04-24）

当前已经落地：

- `POST /product-profiles` 创建后同步返回 `current_run`
- `product_learning` 继续复用 `AgentRun`
- `product_learning_graph` 已在 `backend/runtime/graphs/product_learning.py` 实现
- backend 对 `ProductProfile` 执行同对象写回、`version += 1`
- `learning_stage` 作为派生字段暴露到 summary/detail/history
- `confirm` 已按 `ready_for_confirmation` 收紧，未达标 draft 返回 `409`

---

## 12. 当前明确不做的实现

在当前 spec 下，不应顺手引入：

- product learning LangGraph graph
- 长期记忆数据库
- `SQLite -> Postgres`
- `Langfuse`
- `MCP` 内部服务化
- 任意 SQL database tools
- 流式 token UI

这些都超出当前 Phase 1 目标。

---

## 13. 推荐实施顺序

1. 保持现有 `services.py` 生命周期与写回所有权不变
2. 把 `StubRuntimeAdapter` 抽象成可替换 provider interface
3. 先实现 `lead_analysis` graph
4. 再实现 `report_generation` graph
5. 通过 typed draft payload 完成正式对象写回
6. 用 handoff 和 smoke 记录 boundary 是否保持稳定

---

## 14. 直接依赖关系

本文档直接依赖以下决策与任务：

- `docs/adr/ADR-002-v1-runtime-and-product-learning-baseline.md`
- `docs/delivery/tasks/task_v1_real_runtime_integration_phase1.md`
- `docs/architecture/backend/backend-agent-stack-phased-adoption.md`
- `docs/architecture/system-context.md`

在上述文档发生语义变化前，本 spec 可作为后续 runtime 实现事实源。
