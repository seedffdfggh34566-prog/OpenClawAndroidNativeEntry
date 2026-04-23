# Task：V1 后端最小 API contract

更新时间：2026-04-21

## 1. 任务定位

- 任务名称：V1 后端最小 API contract
- 建议路径：`docs/delivery/tasks/task_v1_backend_api_contract.md`
- 当前状态：`done`
- 优先级：P2

本任务用于在不进入后端实现的前提下，为 AI 销售助手 V1 冻结最小后端 API contract，给 Android 控制壳层和后续后端实现线程提供统一的服务边界。

---

## 2. 任务目标

完成一份可指导后续实现的最小 API contract 说明，至少覆盖以下接口：

- `POST /product-profiles`
- `GET /product-profiles/{id}`
- `POST /analysis-runs`
- `GET /analysis-runs/{id}`
- `GET /reports/{id}`
- `GET /history`

同时明确：

- 每个接口的职责
- 请求/响应最少字段
- 正式对象状态如何在 API 层表达
- `AgentRun` 如何关联输入对象与输出对象
- 历史与状态如何收口为一等查询能力

---

## 3. 当前背景

当前仓库已完成：

- V1 领域对象与状态基线
- V1 信息架构与入口重定义
- Android 控制入口壳层重构

但后端最小服务边界仍未被单独冻结。

这会导致后续问题：

- Android 壳层只能依赖占位数据，无法明确真实 API 依赖
- 后端实现线程缺少清晰的第一版接口范围
- `ProductProfile`、`LeadAnalysisResult`、`AnalysisReport`、`AgentRun` 的服务承接方式容易发散

---

## 4. 范围

本任务 In Scope：

- 定义 V1 最小 API contract 文档
- 明确正式对象与 `AgentRun` 的最小接口边界
- 明确 `history` 的首页聚合读取结构
- 明确 runtime 草稿写回和正式对象读取的 API 责任分工

本任务 Out of Scope：

- 后端实现
- 数据库 schema
- ORM 选型
- 完整鉴权方案
- CRM / 联系人 / 自动触达
- 部署脚本
- 完整 REST 平台设计

---

## 5. 涉及文件

高概率涉及：

- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/delivery/tasks/task_v1_backend_api_contract.md`
- `docs/delivery/README.md`
- `docs/delivery/handoffs/` 下对应 handoff

参考文件：

- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/architecture/system-context.md`
- `docs/reference/schemas/v1-domain-model-baseline.md`
- `docs/architecture/clients/mobile-information-architecture.md`

---

## 6. 产出要求

至少产出以下内容：

1. 最小接口清单
2. 每个接口的职责说明
3. 请求/响应最少字段
4. 正式对象状态与 `AgentRun` 状态的表达边界
5. 首页和 History 页可直接依赖的聚合读取结构

---

## 7. 验收标准

满足以下条件可认为完成：

1. Android 壳层可以据此开始对接真实数据
2. 后续后端实现线程可以直接以此为最小边界推进
3. 文档没有越权扩展到完整 CRM、复杂工作流平台或完整 REST 平台
4. 历史与状态已被明确为一等查询能力

---

## 8. 推荐执行顺序

建议执行顺序：

1. 回顾现有对象基线、信息架构和 runtime/data spec
2. 新增 API contract spec
3. 更新当前 task 状态与结果记录
4. 更新任务目录总览
5. 写 handoff

---

## 9. 风险与注意事项

- 不要把本任务扩展成后端实现
- 不要把 `/history` 扩展成复杂搜索、分页和筛选平台
- 不要在没有必要的情况下增加完整 CRUD
- 不要把 `AgentRun` 状态机混进正式对象状态
- 若需要保留未来扩展空间，优先通过文档说明，而不是先增加接口

---

## 10. 下一步衔接

本任务完成后，可继续拆分：

1. 后端最小实现线程
2. Android 壳层 mock contract 对接线程
3. ProductProfile / AnalysisResult / Report 真实读写线程

---

## 11. 实际产出

本次已完成以下产出：

1. 新增 `docs/reference/api/backend-v1-minimum-contract.md`
2. 新增当前 task 文档
3. 更新 `docs/delivery/README.md`
4. 新增 handoff 文档

本次冻结的 V1 最小接口范围为：

- `POST /product-profiles`
- `GET /product-profiles/{id}`
- `POST /analysis-runs`
- `GET /analysis-runs/{id}`
- `GET /reports/{id}`
- `GET /history`

同时已明确：

- `POST /analysis-runs` 使用统一入口，通过 `run_type` 区分 `lead_analysis` 和 `report_generation`
- `/history` 采用首页聚合结构，优先服务 Android 首页与 History 页
- 失败、取消、重试只体现在 `AgentRun`，不写入正式对象状态

---

## 12. 本次定稿边界

本次明确采用以下边界：

- 后端是正式对象权威真相
- runtime 只返回草稿形态和执行结果
- Android 依赖正式 API 返回结构，而不是 runtime 私有状态
- 报告生成通过 `POST /analysis-runs` 的 `report_generation` 触发，不单独新增 `POST /reports`

本次未扩展到：

- 后端实现
- 鉴权方案
- 数据库与 ORM
- 搜索、分页、筛选
- CRM / 联系人 / 自动触达对象

---

## 13. 已做验证

本次已完成以下验证：

1. 对照项目总览、PRD、runtime/data spec、领域对象基线和信息架构文档，确认 contract 与既有边界一致
2. 检查 spec 中已覆盖 6 个约定接口
3. 检查状态流转与 `AgentRun` 语义保持分离
4. 检查任务目录总览和 handoff 已同步

---

## 14. 实际结果说明

当前该任务已满足原验收目标：

1. task 文档可直接作为后续执行线程的边界
2. spec 能支撑 UI 壳层开始接真实数据
3. 文档与 handoff 已同步
