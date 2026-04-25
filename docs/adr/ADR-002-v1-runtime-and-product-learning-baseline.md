# 决策记录：V1 Runtime 选型与产品学习交互基线

- 文档路径建议：`docs/adr/ADR-002-v1-runtime-and-product-learning-baseline.md`
- 文档状态：Approved baseline v0.1
- 决策日期：2026-04-24
- 关联文档：
  - `docs/product/overview.md`
  - `docs/product/prd/ai_sales_assistant_v1_prd.md`
  - `docs/architecture/system-context.md`
  - `docs/architecture/backend/backend-agent-stack-phased-adoption.md`
  - `docs/delivery/tasks/task_v1_product_learning_interaction_baseline.md`
  - `docs/delivery/tasks/task_v1_real_runtime_integration_phase1.md`

---

## 1. 决策目的

本文档用于正式记录两项会直接约束后续 V1 实现路线的选择：

1. 真实 runtime 接入时，当前默认采用哪一类开源 agent/runtime 方案
2. V1 产品学习阶段，当前默认采用什么交互形态

这两项都不是一次性实现细节，而是会影响：

- backend/runtime 的实现边界
- Android 产品学习页的呈现方式
- `ProductProfile` 的形成与确认路径
- 后续 task 的排队顺序与 scope 控制

因此，它们应写入 decision 文档，而不只停留在聊天结论或单个 task 注释中。

---

## 2. 决策背景

当前仓库已经完成：

- 正式后端最小实现
- Android 最小控制入口
- `ProductProfile` 创建与确认
- `lead_analysis` 和 `report_generation` 的触发、轮询、结果读取

当前未完成的关键点是：

- runtime 仍为 stub
- 产品学习交互形态当时尚未冻结
- 真实 AI 价值闭环尚未验证

在这一阶段，如果不先固定 runtime 与产品学习的基线，后续容易出现：

- backend 选型与 task 方向频繁变化
- Android 按纯聊天推进，backend 按结构化对象推进
- 产品学习页与 `ProductProfile` 确认边界模糊

因此，需要先形成正式 decision。

---

## 3. 最终决策

当前 V1 采用以下工作基线。

### 3.1 决策 A：真实 runtime 的默认方案采用 LangGraph

当前真实 runtime 接入的默认方案为：

> **LangGraph 作为 V1 的默认 runtime / orchestration 方案。**

适用边界：

- 仅限 `backend/runtime/`
- 仅用于执行编排、checkpoint / resume、human-in-the-loop 与 step 状态管理
- 不替代 `FastAPI + services.py` 的产品后端主干

不意味着：

- 用 LangGraph 重写整个后端
- 用 graph runtime 取代正式对象主真相
- 允许 runtime 直接写正式数据库对象

### 3.2 决策 B：Microsoft Agent Framework 是强备选，但不是当前默认

当前也评估了其他开源 agent/runtime 方案。

其中：

- `Microsoft Agent Framework` 是当前最接近的强备选

但当前不把它作为默认方案，原因包括：

- 现有后端是 Python + FastAPI + Pydantic，LangGraph 与当前分层更贴合
- 仓库已有 backend stack adoption 文档，已把 LangGraph 预设为未来 runtime 层方向
- 当前 V1 更需要低摩擦地替换 stub runtime，而不是切入更重的企业工作流栈

### 3.3 决策 C：V1 产品学习采用混合式交互，而不是纯聊天或纯表单

当前产品学习的默认交互形态为：

> **聊天优先 + 结构化摘要辅助 + 阶段门控确认**

这意味着：

- 主界面以问答流推进
- 页面同时持续显示系统当前已理解的结构化摘要
- 页面显式提示仍缺失的关键字段
- 只有达到最低完整度或用户主动要求先生成草稿时，才进入确认页

当前明确不采用：

- 纯聊天自由流，不控制何时收口为正式对象
- 纯静态表单，不让 AI 主动追问关键缺失信息

### 3.4 决策 D：产品学习的最低完整度与阶段状态需要显式门控

进入 `ProductProfile` 确认前，当前最低完整度至少要求：

- `name`
- `one_line_description`
- `target_customers` 至少 1 条
- `typical_use_cases` 至少 1 条
- `pain_points_solved` 至少 1 条
- `core_advantages` 至少 1 条

可缺省但应显式标为 missing 的字段包括：

- `target_industries`
- `delivery_model`
- `constraints`

当前产品学习阶段至少包含以下状态：

- `collecting`
- `ready_for_confirmation`
- `confirmed`

---

## 4. 为什么这样决策

### 4.1 为什么当前默认选 LangGraph

当前项目需要的不是“自由聊天型 agent 平台”，而是具备以下能力的执行层：

- 有状态编排
- pause / resume
- human-in-the-loop
- 结构化输出
- Python 友好
- 能清晰放在 `backend/runtime/` 边界内

LangGraph 与这些要求最贴近，也与当前仓库已有的 backend stack adoption 结论一致。

### 4.2 为什么不把其他框架作为默认主 runtime

当前评估中：

- `Microsoft Agent Framework`：强备选，但当前不是默认
- `Agno`、`CrewAI`、`LlamaIndex Workflows`：可作为参考或局部补充，但不是当前主选
- `Letta`、`PydanticAI`：更适合作为记忆层或 typed agent layer 补充
- `Mastra`、`smolagents`、`OpenHands`、`AutoGen`：不适合作为当前主 runtime 基线

这不是永久排除，而是当前阶段的默认路线控制。

### 4.3 为什么产品学习不能做成纯聊天

如果采用纯聊天：

- 何时结束产品学习不清楚
- `ProductProfile` 很难稳定收口
- 后续 analysis 输入边界会不稳

### 4.4 为什么产品学习也不能退化成纯表单

PRD 已明确 V1 的价值之一是：

- 用户不需要一开始就准备完整资料
- AI 应主动追问关键补充问题

如果退成纯表单，会直接削弱产品学习的核心价值。

---

## 5. 这项决策带来的明确约束

从当前起，以下约束视为有效：

1. 真实 runtime 默认沿 `LangGraph -> backend/runtime/` 方向推进
2. runtime 不能直接越过 backend 写正式对象
3. `backend/api/services.py` 仍是正式写回与业务协调边界
4. 产品学习页默认按混合式交互设计，不按纯聊天或纯表单假设推进
5. 进入确认页必须受最低完整度或显式用户动作门控
6. 如需改用其他默认 runtime，必须先更新 decision 文档

---

## 6. 不在本决策内解决的内容

本文档不直接决定：

- 真实 product learning runtime 的最终实现细节
- 正式 observability 平台何时接入
- `SQLite -> Postgres` 迁移时机
- `MCP`、`pgvector` 是否进入 V1
- Android 产品学习页的最终视觉细节

这些内容应通过后续独立 task 或后续 ADR 再定。

---

## 7. 直接 follow-up

基于本决策，当前推荐的后续任务顺序为：

1. `docs/delivery/tasks/task_v1_product_learning_interaction_baseline.md`
2. `docs/delivery/tasks/task_v1_real_runtime_integration_phase1.md`

在上述两项收口后，再单独创建真实 product learning runtime 接入 task。
