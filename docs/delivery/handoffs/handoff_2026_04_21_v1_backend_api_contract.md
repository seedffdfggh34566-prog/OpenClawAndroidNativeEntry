# 阶段性交接：V1 后端最小 API contract

更新时间：2026-04-21

## 1. 本次改了什么

本次围绕“V1 后端最小 API contract”任务完成了一个文档闭环：

- 新增 `docs/delivery/tasks/task_v1_backend_api_contract.md`
- 新增 `docs/reference/api/backend-v1-minimum-contract.md`
- 更新 `docs/delivery/README.md`

新 spec 明确冻结了 6 个最小接口：

- `POST /product-profiles`
- `GET /product-profiles/{id}`
- `POST /analysis-runs`
- `GET /analysis-runs/{id}`
- `GET /reports/{id}`
- `GET /history`

同时明确了：

- 正式对象状态与 `AgentRun` 状态的分离
- `POST /analysis-runs` 统一承接分析与报告生成
- `/history` 使用首页聚合返回形状
- runtime 草稿输出与正式对象 API 的边界

---

## 2. 为什么这么定

当前对象基线、信息架构和 Android 壳层都已经冻结，但后端最小服务边界还没有单独收口。

因此本次采用“最小接口集合 + 首页聚合 history + 统一 analysis-runs 入口”的方式，原因是：

- 这能直接服务现有 Android 壳层页面
- 能避免过早扩展成完整 REST 平台
- 能把 `AgentRun` 状态、对象状态和 runtime 草稿边界分开

本次特别固定了两个高影响决策：

1. `POST /analysis-runs` 用一个统一入口，通过 `run_type` 区分 `lead_analysis` 和 `report_generation`
2. `GET /history` 先服务首页和 History 页，不设计通用时间线、搜索和分页

---

## 3. 本次验证了什么

本次已完成以下验证：

1. 对照项目总览、PRD、runtime/data spec、领域对象基线和信息架构，确认 contract 与当前 V1 边界一致
2. 检查 spec 中已完整覆盖约定的 6 个接口
3. 检查 `draft / confirmed / published / superseded` 与现有对象状态基线一致
4. 检查 `failed / cancelled / retry` 只体现在 `AgentRun`
5. 检查 task、README 和 handoff 已同步

---

## 4. 已知限制

本次没有做以下内容：

- 没有实现后端接口
- 没有进入数据库 schema
- 没有给出 ORM 选型
- 没有覆盖鉴权方案
- 没有扩展搜索、分页和完整 CRUD
- 没有补 `LeadAnalysisResult` 详情读取接口

因此，当前产出是“后端最小 API contract 文档”，不是可运行后端服务。

---

## 5. 推荐下一步

推荐下一步从以下两个方向中选择其一：

1. 进入真实后端最小实现线程
2. 做 Android 壳层与最小 mock contract 的对接线程

如果继续保持低 blast radius，优先建议先做 mock contract 或后端最小实现，不要同时扩展更多接口。
