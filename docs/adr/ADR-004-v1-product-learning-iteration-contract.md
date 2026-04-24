# 决策记录：V1 Product Learning Iteration Contract

- 文档路径建议：`docs/adr/ADR-004-v1-product-learning-iteration-contract.md`
- 文档状态：Approved baseline v0.1
- 决策日期：2026-04-24
- 关联文档：
  - `docs/product/overview.md`
  - `docs/product/prd/ai_sales_assistant_v1_prd.md`
  - `docs/architecture/system-context.md`
  - `docs/architecture/clients/mobile-information-architecture.md`
  - `docs/reference/api/backend-v1-minimum-contract.md`
  - `docs/reference/schemas/v1-domain-model-baseline.md`
  - `docs/architecture/runtime/langgraph-runtime-architecture.md`
  - `docs/delivery/tasks/task_v1_product_learning_iteration_contract.md`

---

## 1. 决策目的

本文档用于冻结 product learning 从 single-turn enrich 进入下一轮迭代时的最小 public contract，避免后续 backend、runtime 与 Android 在以下问题上继续各自解释：

1. 是否新增 product learning iteration endpoint
2. iteration 是否继续复用 `AgentRun`
3. iteration 请求体与响应体长什么样
4. enrich 写回时哪些字段允许覆盖，哪些字段必须保留
5. Android 是否需要引入独立消息对象或消息持久化

---

## 2. 最终决策

### 2.1 下一轮 product learning 采用单轮 iteration endpoint

在现有 8 个 public endpoint 的基础上，下一轮 product learning contract 固定新增：

- `POST /product-profiles/{id}/enrich`

该接口的职责固定为：

- 承接用户补充的一轮自然语言信息
- 将补充文本合并进同一个 `ProductProfile`
- 创建一次新的 `run_type = product_learning` 的 `AgentRun`
- 由 runtime 重新富化同一个 `ProductProfile`

它不是新的聊天消息接口，也不是独立的会话 API。

### 2.2 iteration 继续复用 `AgentRun`

V1 继续只保留以下正式业务对象：

1. `ProductProfile`
2. `LeadAnalysisResult`
3. `AnalysisReport`
4. `AgentRun`

当前不新增：

- `ProductLearningRun`
- `ProductLearningMessage`
- 独立的 conversation / session 正式对象

`POST /product-profiles/{id}/enrich` 返回值固定为：

- `agent_run`

客户端继续通过：

- `GET /analysis-runs/{id}`

轮询运行状态。

### 2.3 iteration 请求与响应 contract

`POST /product-profiles/{id}/enrich` 的最小请求体固定为：

```json
{
  "supplemental_notes": "补充一轮产品、客户或场景说明。",
  "trigger_source": "android_product_learning_iteration"
}
```

约束：

- `supplemental_notes` 必填、非空
- `trigger_source` 必填
- 当前不支持 message list、attachments、structured patch payload

最小响应体固定为：

```json
{
  "agent_run": {
    "id": "run_002",
    "run_type": "product_learning",
    "status": "queued",
    "triggered_by": "user",
    "trigger_source": "android_product_learning_iteration",
    "input_refs": [
      {
        "object_type": "product_profile",
        "object_id": "pp_001",
        "version": 2
      }
    ],
    "output_refs": [],
    "started_at": null,
    "ended_at": null,
    "error_message": null
  }
}
```

### 2.4 补充文本的持久化方式

iteration 输入文本的持久化方式固定为：

- backend 在创建 `product_learning` `AgentRun` 前，将 `supplemental_notes` 追加到同一个 `ProductProfile.source_notes`

追加规则固定为：

- 使用换行分隔追加
- 保留历史说明文本
- 不引入独立消息时间线

因此，runtime 每一轮读取的都是：

- 当前最新的 `ProductProfile`
- 已累计的 `source_notes`

### 2.5 iteration 写回规则

下一轮 enrich 的写回规则固定为：

- `name`、`one_line_description`：不允许 runtime 覆盖
- 非空的 `target_customers`、`target_industries`、`typical_use_cases`、`pain_points_solved`、`core_advantages`：默认保留，runtime 只补空
- `delivery_model`：仅当当前值仍为弱默认值时，允许 runtime 覆盖
- `constraints`：允许以去重后的 append 方式补充
- `missing_fields`：始终由 backend 重算并覆盖
- `learning_stage`：始终由 backend 重算并对外暴露

默认原则固定为：

> **补空优先，有限覆盖弱默认值。**

### 2.6 `learning_stage` 与正式状态保持不变

下一轮 iteration 不改变以下事实：

- `ProductProfile.status` 继续只使用：
  - `draft`
  - `confirmed`
  - `superseded`
- `learning_stage` 继续只使用：
  - `collecting`
  - `ready_for_confirmation`
  - `confirmed`

`ready_for_confirmation` 仍不是新的正式对象状态，而是 backend 派生阶段。

### 2.7 Android 只承接轻量 iteration 交互

Android 下一轮默认只承接：

- 一次补充输入框
- 当前理解摘要
- 缺失字段展示
- 当前 run 状态展示
- `ready_for_confirmation` 后的确认 CTA

当前不引入：

- 完整聊天消息气泡系统
- 消息持久化时间线
- streaming token UI

---

## 3. 明确约束

从当前起，以下约束视为有效：

1. 下一轮 product learning iteration 默认新增 `POST /product-profiles/{id}/enrich`
2. 仍继续复用 `AgentRun`
3. iteration 输入只承接 `supplemental_notes + trigger_source`
4. backend 负责把 `supplemental_notes` 追加到 `source_notes`
5. backend 保留 `missing_fields` 与 `learning_stage` 的最终所有权
6. Android 不引入新正式消息对象
7. 当前不新增新的 lifecycle

---

## 4. 不在本决策内解决的内容

本文档不直接决定：

- runtime observability / eval baseline 的具体字段清单
- 真实 LLM provider、prompt 版本与模型选择
- analysis/report 的下一轮策略
- 完整聊天协议与消息持久化
- 长期记忆与多轮 session 策略

这些内容应留给后续独立 task。

---

## 5. 直接 follow-up

基于本决策，当前直接后续任务应为：

1. 完成 `task_v1_product_learning_iteration_contract.md` 的 docs 收口
2. 进入 `task_v1_runtime_observability_eval_baseline.md`
3. 再进入 `task_v1_product_learning_llm_phase1.md`
4. 最后进入 `task_v1_android_product_learning_iteration_ui.md`
