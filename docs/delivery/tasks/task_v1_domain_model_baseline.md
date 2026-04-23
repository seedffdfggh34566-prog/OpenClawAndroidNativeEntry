# Task：V1 领域对象与状态基线

更新时间：2026-04-21

## 1. 任务定位

- 任务名称：V1 领域对象与状态基线
- 建议路径：`docs/delivery/tasks/task_v1_domain_model_baseline.md`
- 当前状态：`done`
- 优先级：P0

本任务用于把 AI 销售助手 V1 的正式业务对象与状态关系先定义清楚，为后续页面骨架、后端 API contract 和 agent 执行边界提供统一事实源。

---

## 2. 任务目标

完成一份可指导后续实现的对象基线说明，至少覆盖以下正式对象：

- `ProductProfile`
- `LeadAnalysisResult`
- `AnalysisReport`
- `AgentRun`

同时明确：

- 每个对象的职责和权威性
- 对象之间的引用关系
- V1 最小状态流转
- 哪些数据属于正式对象，哪些只属于中间运行上下文

---

## 3. 当前背景

当前 PRD 和架构文档已经明确：

- 手机端不是权威主存
- 本地服务器承载正式后端
- OpenClaw 只承担 runtime / execution layer
- 正式结果必须沉淀为业务对象，而不是停留在聊天会话中

但当前仓库还没有一份足够具体、可直接用于后续 task 的领域对象基线文档。

这会导致后续问题：

- 页面字段和后端字段容易各自发散
- Agent 输出结构不容易收口
- Android 端入口重构缺少统一对象锚点

---

## 4. 范围

本任务 In Scope：

- 新建或补充 `docs/reference/` 下的领域对象基线说明
- 定义 V1 正式对象的最小字段分组
- 定义对象生命周期和最小状态集合
- 定义对象之间的引用方式
- 定义 Agent 输出到正式对象的落档边界

本任务 Out of Scope：

- 正式数据库 schema
- 具体 ORM 选型
- 完整 API 实现
- Android UI 改造
- 联系人、CRM、自动触达等扩展对象

---

## 5. 涉及文件

高概率涉及：

- `docs/architecture/system-context.md`
- `docs/reference/` 下新增领域对象 spec
- `docs/delivery/tasks/task_v1_domain_model_baseline.md`
- `docs/delivery/handoffs/` 下对应 handoff

参考文件：

- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/adr/ADR-001-backend-deployment-baseline.md`

---

## 6. 产出要求

至少产出以下内容：

1. V1 正式对象清单
2. 每个对象的职责说明
3. 每个对象的建议字段分组
4. 对象状态枚举及含义
5. 对象关系图或文字说明
6. Agent runtime 与正式对象之间的写回规则

---

## 7. 验收标准

满足以下条件可认为完成：

1. 后续任务能够明确引用该对象定义，不再需要重复解释对象含义
2. 可以据此继续拆 API contract task
3. 可以据此继续拆 Android 信息架构和页面骨架 task
4. 文档没有越权把 V1 扩大到 CRM / 联系方式 / 自动触达

---

## 8. 推荐执行顺序

建议执行顺序：

1. 回顾 PRD 和现有 runtime/data spec
2. 新增领域对象基线文档
3. 将对象定义回链到现有 spec
4. 更新本 task 状态
5. 写 handoff

---

## 9. 风险与注意事项

- 不要直接把聊天会话结构当成正式对象
- 不要提前引入大型 CRM 字段体系
- 不要为了“未来扩展”把 V1 字段做得过重
- 状态设计优先可执行、可解释，不追求一次性完美

---

## 10. 下一步衔接

本任务完成后，优先衔接：

1. `task_v1_information_architecture.md`
2. `task_v1_android_control_shell_refactor.md`

---

## 11. 实际产出

本次已完成以下产出：

1. 新增 `docs/reference/schemas/v1-domain-model-baseline.md`
2. 回链并收口 `docs/architecture/system-context.md`
3. 同步更新当前 task 状态与结果记录
4. 新增 handoff 文档用于后续承接

本次冻结的 V1 正式对象为：

- `ProductProfile`
- `LeadAnalysisResult`
- `AnalysisReport`
- `AgentRun`

本次同时明确：

- 聊天会话不是正式业务对象
- `ProductProfileDraft`、`LeadAnalysisResultDraft`、`AnalysisReportDraft` 是正式对象的草稿形态，不是新的正式对象类型
- `Lead`、`LeadResearchSnapshot`、CRM 扩展对象不进入本任务冻结范围

---

## 12. 本次定稿边界

本次明确采用以下边界：

- 正式对象负责业务真相与结果沉淀
- `AgentRun` 负责执行记录，不承担业务真相
- runtime 只返回结构化草稿形态与中间信息
- 产品后端负责校验、写回、赋予状态与版本

本次未扩展到：

- Android UI 重构
- 后端 API 实现
- 数据库 schema
- ORM 选型
- CRM、联系人库、自动触达对象

---

## 13. 已做验证

本次已完成以下验证：

1. 对照 `docs/product/overview.md`、`docs/product/prd/ai_sales_assistant_v1_prd.md`、`docs/architecture/system-context.md`、`docs/adr/ADR-001-backend-deployment-baseline.md`，确认未改变既有产品含义
2. 检查新基线文档已被现有架构 spec 正确引用
3. 检查 `Draft` 表述已统一为草稿形态，而非新增正式对象类型
4. 检查 `Lead`、`LeadResearchSnapshot` 已不再作为 V1 核心正式对象冻结

---

## 14. 实际结果说明

当前该任务已满足原验收目标：

1. 已形成可供后续信息架构、Android 壳层重构、API contract 引用的领域对象基线文档
2. 已明确区分正式对象、中间运行态和 runtime 层职责
3. 未越权扩展到 CRM、联系人库或自动触达系统
