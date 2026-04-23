# Task：V1 后端最小实现

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：V1 后端最小实现
- 建议路径：`docs/delivery/tasks/task_v1_backend_minimum_implementation.md`
- 当前状态：`done`
- 优先级：P0

本任务用于在不扩展 V1 范围的前提下，落地 AI 销售助手 V1 的最小正式后端实现。

---

## 2. 任务目标

完成一版可运行、可验证、可继续迭代的最小正式后端，至少满足：

- 存在独立于 Android 的后端目录与服务骨架
- 能承载正式业务对象主真相
- 能提供已冻结的最小 API contract 中的核心读取与写入能力
- 为后续 runtime 接入预留明确边界

---

## 3. 当前背景

当前仓库已经完成：

- V1 领域对象基线
- V1 信息架构
- Android 控制壳层重构
- V1 后端最小 API contract
- 后端优先的仓库与文档对齐

当前尚未完成：

- 正式后端代码实现
- 最小持久化基线
- Android 对真实后端数据的联调

因此，当前最关键的执行缺口已经从“方向与原则”转为“最小正式后端落地”。

---

## 4. 范围

本任务 In Scope：

- 新增独立 `backend/` 目录
- 落地最小服务骨架
- 落地最小配置、日志与健康检查
- 落地最小持久化基线
- 实现最小 API contract 的核心接口
- 为 runtime 接入预留适配边界

本任务 Out of Scope：

- 完整鉴权与账号系统
- CRM / 联系方式 / 自动触达
- 正式云端部署
- 复杂搜索、分页和筛选
- iOS / PC 客户端实现
- 大规模 Android 联调改造

---

## 5. 涉及文件

高概率涉及：

- `backend/` 下新增目录
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/architecture/system-context.md`
- `docs/delivery/tasks/task_v1_backend_minimum_implementation.md`
- `docs/delivery/handoffs/` 下对应 handoff

参考文件：

- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/architecture/repository-layout.md`
- `docs/adr/ADR-001-backend-deployment-baseline.md`

---

## 6. 产出要求

至少产出以下内容：

1. 独立后端目录骨架
2. 最小可运行服务
3. 最小持久化方案
4. API contract 中核心接口的第一版实现
5. 最小验证记录

---

## 7. 验收标准

满足以下条件可认为完成：

1. 后端可独立于 Android 壳层运行
2. 至少能提供正式对象的最小写入和读取能力
3. 至少能提供首页 / 历史所需的聚合读取能力
4. 没有越权扩展到 CRM、自动触达或大规模平台重构

---

## 8. 推荐执行顺序

建议执行顺序：

1. 确认后端语言、框架与最小运行方式
2. 新增 `backend/` 骨架
3. 实现配置、日志、健康检查
4. 实现最小持久化
5. 先实现 `POST /product-profiles`
6. 再实现 `GET /product-profiles/{id}`
7. 再实现 `GET /history`
8. 最后补 `analysis-runs` 与 `reports`
9. 运行最小验证
10. 更新 task 与 handoff

---

## 9. 风险与注意事项

- 不要把本任务扩展成完整平台后端
- 不要让 runtime 直接承担正式对象主真相
- 不要先写一堆未来扩展接口再说
- 若框架选型会显著影响仓库结构，应先补 spec 再做实现

---

## 10. 下一步衔接

本任务完成后，优先继续：

1. Android 壳层最小真实数据对接
2. runtime 与 backend 的正式最小接入

---

## 11. 实际产出

本次已完成以下产出：

1. 新增独立 `backend/` Python 项目骨架
2. 新增 FastAPI 应用入口与健康检查接口
3. 新增 SQLite 持久化基线与 4 个正式对象模型
4. 实现 `POST /product-profiles`
5. 实现 `GET /product-profiles/{id}`
6. 实现 `POST /analysis-runs`
7. 实现 `GET /analysis-runs/{id}`
8. 实现 `GET /reports/{id}`
9. 实现 `GET /history`
10. 新增可替换的 stub runtime 适配层
11. 新增后端测试用例
12. 新增后端实现 handoff，并补充本地运行命令到 runbook

---

## 12. 本次定稿边界

本次明确采用以下边界：

- 后端采用 `Python + FastAPI + Pydantic v2 + SQLAlchemy + SQLite`
- runtime 仅采用可预测的 stub 适配层
- 不实现鉴权、账号、多租户、分页、搜索
- 不改 Android 代码
- 为开发可运行性，允许 stub 在开发模式下接受 `draft` 的 `ProductProfile` 触发 `lead_analysis`

---

## 13. 已做验证

本次已完成以下验证：

1. 运行 `python3 -m venv backend/.venv`
2. 运行 `backend/.venv/bin/pip install -e backend`
3. 运行 `backend/.venv/bin/python -m unittest backend.tests.test_api`
4. 运行 `backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
5. 手工调用 `/health`
6. 手工跑通：
   - 创建 `ProductProfile`
   - 触发 `lead_analysis`
   - 读取 `AgentRun`
   - 触发 `report_generation`
   - 读取 `/history`

---

## 14. 实际结果说明

当前该任务已满足原验收目标：

1. 后端已可独立于 Android 壳层运行
2. 已能承载正式业务对象主真相
3. 已能通过 stub runtime 跑通正式对象写回与首页聚合读取链路
4. 后续可继续进入 Android 最小真实数据对接或真实 runtime 接入
