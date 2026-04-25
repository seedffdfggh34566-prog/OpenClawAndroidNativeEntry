# Task：V1 真实 Runtime 接入 Phase 1

更新时间：2026-04-24

## 1. 任务定位

- 任务名称：V1 真实 Runtime 接入 Phase 1
- 建议路径：`docs/delivery/tasks/task_v1_real_runtime_integration_phase1.md`
- 当前状态：`done`
- 优先级：P0

本任务用于在不改变当前正式 API 主语义的前提下，把 `lead_analysis` 与 `report_generation` 从 stub runtime 切换到真实 runtime，验证 V1 的执行层不再只是固定模板回包。

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/task_v1_product_learning_interaction_baseline.md`
- 建议下游任务：
  1. 后续根据产品学习基线单独创建 product learning runtime 接入 task
- 停止条件：
  - 需要改变正式 API 语义或当前 domain model
  - 需要新增数据库基线、部署方式、可观测平台或工具协议基线
  - 需要让 runtime 直接写正式数据库对象
  - runtime 接入要求把后端主干改写成 graph-first architecture

---

## 2. 任务目标

在保持后端主真相边界不变的前提下，实现：

- 为 `lead_analysis` 建立真实 runtime 执行图
- 为 `report_generation` 建立真实 runtime 执行图
- runtime 输出结构化 draft payload，由 backend 校验后写回正式对象
- `AgentRun` 至少具备可观察的执行状态与错误信息

推荐基线选择：

- `LangGraph` 作为当前默认 runtime/orchestration 方案
- `backend/runtime/` 作为唯一 runtime 实现边界

---

## 3. 当前背景

当前仓库已完成：

- 后端最小正式 API
- Android 对象读写与触发链路
- `ProductProfile draft -> confirmed`
- `LeadAnalysisResult` 与 `AnalysisReport` 页面读取

当前仍未完成：

- 真实 runtime 执行
- 真实结构化输出生成
- 失败恢复与执行轨迹回看

现状中 `backend/runtime/adapter.py` 仍为可预测 stub，这使当前 V1 只能验证对象流，不能验证真实 AI 价值闭环。

---

## 4. 范围

本任务 In Scope：

- 在 `backend/runtime/` 内接入真实 runtime 编排
- 将 `lead_analysis` 与 `report_generation` 从 stub 切到真实执行
- 使用 typed payload 将 runtime 输出回传给 backend
- backend 校验后写回 `LeadAnalysisResult` / `AnalysisReport`
- 最小执行日志、错误回传与手动 smoke 验证
- 配套更新 task / handoff / architecture / reference 文档

本任务 Out of Scope：

- 产品学习 runtime 接入
- 新增产品学习聊天 API
- `SQLite -> Postgres` 迁移
- `Langfuse`、`MCP`、`pgvector` 正式接入
- Android 大改版或完整流式 UI
- CRM、联系人抓取、自动触达

---

## 5. 涉及文件

高概率涉及：

- `backend/runtime/adapter.py`
- `backend/runtime/*`
- `backend/api/services.py`
- `backend/api/schemas.py`
- `backend/tests/*`
- `docs/architecture/backend/backend-agent-stack-phased-adoption.md`
- `docs/reference/api/backend-v1-minimum-contract.md`

参考文件：

- `backend/AGENTS.md`
- `docs/architecture/system-context.md`
- `docs/adr/ADR-002-v1-runtime-and-product-learning-baseline.md`

---

## 6. 产出要求

至少应产出：

1. 一份可替代 stub 的真实 runtime 实现
2. 一组明确的 runtime input / output schema
3. backend 校验并写回正式对象的最小闭环
4. 至少一条 analysis 和 report 真实执行 smoke 记录
5. 配套 task、handoff 与边界文档更新

---

## 7. 验收标准

满足以下条件可认为完成：

1. `lead_analysis` 不再返回固定 stub 模板
2. `report_generation` 不再返回固定 stub 模板
3. runtime 不直接写数据库正式对象
4. `backend/api/services.py` 仍是正式写回协调层
5. `backend/.venv/bin/python -m pytest backend/tests` 通过
6. 本地 backend 启动与 `/health` smoke 正常
7. 至少一次手动 API 流验证通过：
   - confirmed `ProductProfile`
   - create `analysis_run`
   - 获取 `LeadAnalysisResult`
   - 触发 `report_generation`
   - 获取 `AnalysisReport`
8. 失败时能在 `AgentRun` 或相关日志中看到可定位的错误信息

---

## 8. 推荐执行顺序

建议执行顺序：

1. 先确认 ADR 与 product learning baseline 已冻结
2. 先为 runtime input / output schema 定形
3. 在 `backend/runtime/` 内实现 `lead_analysis` 图
4. 接入 `report_generation` 图
5. 保持 backend 写回边界不变
6. 跑后端测试、启动 smoke 与最小手动流验证

---

## 9. 风险与注意事项

- 这是 runtime boundary 任务，不要顺手把后端主服务层重写掉
- 不要让 runtime 越过 backend 直接写正式对象
- 不要顺手引入新的 observability、DB 或工具协议基线
- 若需要 `LangGraph` 以外的默认 runtime，必须先回到 decision 文档

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. 基于已冻结交互形态单独创建 product learning runtime 接入 task
2. 评估是否需要独立的 observability follow-up task

---

## 11. 实际产出

- `backend/runtime/adapter.py`：改为 provider abstraction，默认 provider 为 `langgraph`
- `backend/runtime/types.py`：新增 runtime payload 与 state typing
- `backend/runtime/graphs/lead_analysis.py`：新增 lead analysis graph
- `backend/runtime/graphs/report_generation.py`：新增 report generation graph
- `backend/api/services.py`：切到 runtime provider dispatch，但继续在 services 层写回正式对象
- `backend/tests/test_api.py`、`backend/tests/test_services.py`：补运行时验证
- `docs/delivery/handoffs/handoff_2026_04_24_real_runtime_integration_phase1.md`：补交接记录

---

## 12. 本次定稿边界

- Phase 1 只替换 `lead_analysis` / `report_generation` stub，不实现 product learning runtime
- 不新增 lifecycle、DB、observability 或工具协议基线
- 当前 graph 节点先用受控 Python 生成结构化 draft，未接外部 LLM / 搜索

---

## 13. 已做验证

1. `backend/.venv/bin/python -m pytest backend/tests`：`19 passed`
2. `python3 /home/yulin/.codex/skills/backend-local-verify/scripts/run_backend_verify.py --workspace "$PWD" --mode full`：通过
3. 手动 API flow：confirmed profile -> `lead_analysis` -> detail read -> `report_generation` -> report read：通过

---

## 14. 实际结果说明

- `lead_analysis` 与 `report_generation` 已切到 backend-direct LangGraph
- 外部 API 语义保持不变
- `runtime_metadata` 现在包含 provider / graph_name / run_type / trace_id，并在失败时补 `error_type`
