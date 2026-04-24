# 决策记录：V1 Product Learning Runtime Boundary

- 文档路径建议：`docs/adr/ADR-003-v1-product-learning-runtime-boundary.md`
- 文档状态：Approved baseline v0.1
- 决策日期：2026-04-24
- 关联文档：
  - `docs/product/overview.md`
  - `docs/product/prd/ai_sales_assistant_v1_prd.md`
  - `docs/architecture/system-context.md`
  - `docs/reference/api/backend-v1-minimum-contract.md`
  - `docs/reference/schemas/v1-domain-model-baseline.md`
  - `docs/delivery/tasks/task_v1_product_learning_runtime_decision_freeze.md`
  - `docs/delivery/tasks/task_v1_product_learning_runtime_followup.md`

---

## 1. 决策目的

本文档用于冻结 product learning runtime 进入正式实现前仍悬空的边界决策，避免后续 backend、Android 与 runtime 在以下问题上继续各自解释：

1. V1 是否需要独立 product learning run 正式对象
2. `ready_for_confirmation` 应由谁判定
3. 客户端应读取什么阶段字段
4. 第一版 product learning runtime 采用什么接入形态

补充说明：

- 本文档冻结的是 **第一版 single-turn enrich 基线**
- 下一轮 iteration contract 已由 `ADR-004-v1-product-learning-iteration-contract.md` 单独承接

---

## 2. 最终决策

### 2.1 V1 继续只保留 4 个正式业务对象

V1 正式业务对象继续固定为：

1. `ProductProfile`
2. `LeadAnalysisResult`
3. `AnalysisReport`
4. `AgentRun`

当前**不新增独立 product learning run 正式对象**。

product learning 执行记录继续通过 `AgentRun` 承担，只新增：

- `run_type = product_learning`

---

### 2.2 `ready_for_confirmation` 不是正式对象状态

`ready_for_confirmation` 的含义固定为：

> **backend 基于当前 `ProductProfile` 完整度计算出的产品学习阶段表达。**

它不是新的持久化正式对象状态。

`ProductProfile.status` 继续保持：

- `draft`
- `confirmed`
- `superseded`

因此：

- `learning_stage` 用于表达“当前处于产品学习哪个阶段”
- `status` 用于表达“正式对象当前处于什么生命周期状态”

二者不能混用。

---

### 2.3 backend services 负责阶段判定

阶段判定责任固定为：

- runtime 负责输出：
  - draft 字段候选
  - `missing_fields`
  - `confidence_score`
- backend product services 负责：
  - 校验最低完整度
  - 写回 `ProductProfile`
  - 计算 `learning_stage`

客户端只消费 backend 暴露出来的阶段字段，不自行从 `status + missing_fields` 推断。

---

### 2.4 backend 显式暴露 `learning_stage`

从当前起，产品学习阶段表达的默认对外方式固定为：

- backend 在 `ProductProfileSummary` 与 `ProductProfileDetail` 中显式暴露 `learning_stage`

固定值为：

- `collecting`
- `ready_for_confirmation`
- `confirmed`

---

### 2.5 第一版 product learning runtime 采用 single-turn enrich

当前默认实现形态固定为：

> **single-turn enrich + 现有 API 承载**

具体含义：

1. `POST /product-profiles` 仍作为第一版 product learning 入口
2. backend 创建初始 `ProductProfile` draft
3. backend 立即创建 `run_type = product_learning` 的 `AgentRun`
4. runtime 执行单轮富化，补全结构化字段、`missing_fields` 与 `confidence_score`
5. backend 写回同一个 `ProductProfile`
6. 客户端通过现有 `GET /analysis-runs/{id}` 轮询 run 状态
7. 客户端通过现有 `GET /product-profiles/{id}` 读取富化后的正式对象

当前**不新增新的 public endpoint**，V1 第一版保持当前 8 个接口。

下一轮“继续补充一轮信息”的 contract 不再由本文档承接，改由 `ADR-004` 冻结。

当前也**不引入多轮聊天 public API**、`/product-learning/*` 路径或额外 lifecycle 状态。

---

## 3. 明确约束

从当前起，以下约束视为有效：

1. V1 不新增独立 product learning run 正式对象
2. product learning 执行继续复用 `AgentRun`
3. `ready_for_confirmation` 由 backend services 判定
4. backend 必须显式下发 `learning_stage`
5. 客户端不得自行推断产品学习阶段
6. 第一版 product learning runtime 必须复用现有 public API
7. 第一版 product learning runtime 采用 single-turn enrich，不直接进入多轮聊天 API

---

## 4. 不在本决策内解决的内容

本文档不直接决定：

- 更完整的多轮聊天协议
- 长期记忆与会话持久化策略
- `waiting_for_user / paused / resumed` 等新 lifecycle
- 额外 observability 平台或基础设施
- 首页、结果页、报告页的最终产品表达

这些内容应留给后续独立 task 或 ADR。

---

## 5. 直接 follow-up

基于本决策，当前直接后续任务应为：

1. 完成 `task_v1_product_learning_runtime_decision_freeze.md` 的 docs 收口
2. 将 `task_v1_product_learning_runtime_followup.md` 改写为无开放决策空洞的实现任务
3. 再进入 product learning runtime 实现
