# V1 仓库与产品缺口 Planning Note

更新时间：2026-04-24

## 1. 文档定位

本文档用于把当前阶段仍未收口的仓库管理缺口、产品定义缺口与实现前置缺口整理成一份 planning note。

它回答的问题包括：

- 当前仓库管理还有哪些没完善
- 当前产品定义还有哪些没冻结
- 哪些缺口应该先补文档，哪些可以留给后续 task
- 在真实 runtime 接入前，哪些内容必须先收口

本文档不是：

- 正式 ADR
- 直接可执行的编码 task
- 最终产品设计稿

---

## 2. 当前阶段判断

当前仓库已经完成了：

- V1 主线与非目标冻结
- backend 最小正式 contract
- Android 最小控制入口闭环
- `ProductProfile -> LeadAnalysisResult -> AnalysisReport` 的对象流验证
- 真实 runtime 默认方向与产品学习交互基线 decision

当前仓库还没有完成的，不再是“方向是什么”，而是：

> **如何把已定下来的基线写回主文档，并把实现约束做厚。**

---

## 3. 仓库管理层缺口

### 3.1 主文档尚未完全吸收最新 decision

当前已经新增：

- `docs/adr/ADR-002-v1-runtime-and-product-learning-baseline.md`

但以下主文档还未完全把这些结论写回：

- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/architecture/system-context.md`
- `docs/architecture/clients/mobile-information-architecture.md`
- `docs/product/overview.md`

这会导致 decision 已经成立，但方向层与方案层文档仍保留旧的不确定表述。

### 3.2 runtime 方案层文档仍偏空

当前：

- `docs/architecture/runtime/README.md` 仍是占位状态

在真实 runtime 接入前，至少还需要：

- LangGraph 接入边界说明
- runtime state 形态
- graph 与 formal object writeback 的关系
- 错误与最小可观测模型

### 3.3 roadmap 仍过于粗略

当前 `docs/product/roadmap.md` 还不足以支撑长时自治开发。

至少需要能回答：

- 当前处于哪个 phase
- 本 phase 的 exit criteria
- 下一个 phase 依赖什么
- 哪些内容是 stop condition

### 3.4 handoff 纪律尚未完全稳定

仓库已经建立 handoff 机制，但实际执行上仍出现过：

- task 已完成但 handoff 缺失
- 验证已做但 handoff 未记录

如果后续继续 24 小时自治开发，这会直接影响可追溯性。

### 3.5 agent 本地配置文件策略未定

当前工作区仍存在：

- `.claude/settings.json`

它目前既不是正式仓库资产，也没有明确忽略策略。  
这会污染工作区状态判断，并让自动开发中的“脏工作区”识别变得不可靠。

### 3.6 branch discipline 规则已写，但执行还不稳定

根 `AGENTS.md` 已明确：

- 不把 `main` 当 scratchpad
- 长时自治开发应在工作分支上推进

但实际提交纪律仍需继续固化，否则后续 phase 审计和回滚成本会上升。

---

## 4. 产品层缺口

### 4.1 产品学习交互基线尚未写回 PRD 主体

当前已通过 ADR 冻结：

- 聊天优先
- 结构化摘要辅助
- 阶段门控确认

但 PRD 主文尚未把这一点写成正式产品基线。

### 4.2 最低完整度门槛尚未变成正式对象规则

当前已明确最低完整度要求：

- `name`
- `one_line_description`
- 至少一条 `target_customers`
- 至少一条 `typical_use_cases`
- 至少一条 `pain_points_solved`
- 至少一条 `core_advantages`

但当前还没有正式定义：

- backend 如何判断 `ready_for_confirmation`
- 缺失字段列表如何与 `ProductProfile.missing_fields` 对齐

### 4.3 产品学习阶段对象仍未完全冻结

当前正式对象主线已经明确，但当真实 product learning runtime 接入时，仍需决定：

- 是否需要显式 `ProductLearningRun`
- 是否只复用现有 `AgentRun`
- 产品学习中的中间状态是否只停留在 runtime state，而不新增正式对象

这会影响 API、状态页和 handoff 设计。

### 4.4 页面状态叙事还不够厚

当前 mobile IA 已定义页面骨架，但还没有把以下状态转移写透：

- `collecting`
- `ready_for_confirmation`
- `confirmed`
- `analysis_running`
- `report_ready`

用户在首页、历史页、产品学习页之间如何感知这些状态，仍需补清。

### 4.5 分析结果页与报告页仍偏 contract-first

当前页面已经能读正式详情，但更偏“能展示结构化数据”，还不是最终产品表达。

后续仍需补：

- 字段优先级
- 页面主次层级
- 用户真正关心的阅读路径

---

## 5. 实现前置缺口

### 5.1 真实 runtime 需要先遵守当前最小 lifecycle

当前已实现的 `AgentRun` 生命周期只有：

- `queued`
- `running`
- `succeeded`
- `failed`

在 dedicated lifecycle task 之前，不应擅自引入：

- `waiting_for_user`
- `paused`
- `resumable`
- queue worker orchestration

### 5.2 runtime 仍必须是执行层，不是 product truth layer

当前 writeback ownership 仍在：

- `backend/api/services.py`

因此，真实 runtime 接入时必须继续遵守：

- runtime 输出 draft payload
- backend 校验并写回正式对象
- runtime 不直接落正式业务表

### 5.3 product learning runtime 应晚于 analysis/report runtime

当前最合理顺序仍然是：

1. 先完成产品学习交互基线冻结与回写
2. 先把 `lead_analysis` / `report_generation` 从 stub 切到真实 runtime
3. 再进入 product learning runtime

原因很简单：

- analysis/report 已有正式 API 主路径
- 它们更容易先验证 runtime boundary
- product learning 仍涉及更多交互、对象与生命周期决定

---

## 6. 当前建议的收口顺序

### P0：把方向层与方案层文档吸收最新基线

先补：

- PRD
- system-context
- mobile information architecture
- runtime architecture docs

### P1：把 runtime 方案层补厚

至少补：

- LangGraph runtime architecture spec
- 最小 state / node / writeback 边界
- 错误与验证边界

### P2：再进入真实 runtime task

顺序建议：

1. `task_v1_product_learning_interaction_baseline.md`
2. `task_v1_real_runtime_integration_phase1.md`
3. product learning runtime follow-up task

### P3：最后补产品表达层收口

包括：

- 首页状态叙事
- 分析结果页字段层级
- 报告页最终表达

---

## 7. 当前不建议现在就做的事

当前不建议因为要接入 LangGraph，就顺手做以下事情：

- `SQLite -> Postgres`
- `Langfuse` 正式接入
- `MCP` 全面引入
- 长期记忆系统
- 完整 chat client 重写
- 完整工作台或 CRM 扩展

这些都属于不同层级的 follow-up，而不是当前 V1 runtime 接入的前置条件。

---

## 8. 推荐下一步

1. 先把 ADR-002 的结论写回 PRD / system-context / mobile IA
2. 使用 `docs/architecture/runtime/langgraph-runtime-architecture.md` 作为后续 runtime 实现事实源
3. 再由执行 agent 推进 `task_v1_product_learning_interaction_baseline.md`
4. 之后再执行 `task_v1_real_runtime_integration_phase1.md`
