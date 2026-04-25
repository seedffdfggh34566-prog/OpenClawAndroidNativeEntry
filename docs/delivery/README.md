# 任务目录说明

更新时间：2026-04-25

## 1. 目录定位

本目录用于承载当前项目的正式任务文档。

任务文档的作用不是重复 PRD 或 spec，而是把已经明确的方向拆成可以独立执行、独立验证、独立交接的小闭环。

---

## 2. 当前阶段说明

当前项目已经完成：

- AI 销售助手 V1 demo-ready release candidate / learning milestone closeout。
- V1 demo runbook 与 evidence pack。
- V2 PRD Draft v0.2。
- V2 lead research data model Draft v0.1。
- V2 planning baseline update。
- V2 conversational sales agent definition update。

当前项目处于：

> **V2 对话式专属销售 agent planning baseline 阶段**

当前阶段重点是冻结 V2.1 对话式销售 agent、数据、runtime 边界和后端 contract；V2.2 再恢复搜索边界、联系方式边界和 lead research 实现讨论。不自动进入实现。

---

## 3. 当前任务状态

当前正式任务队列：

- Current task：暂无
- Next queued tasks：尚未排定

最近完成：

- `task_v2_planning_baseline_update.md`
- `task_v2_conversational_sales_agent_definition_update.md`
- `task_v1_closeout.md`
- `task_v1_demo_runbook_and_evidence_pack.md`

执行层不应继续自动追加 V1 功能，也不应在未排入 `_active.md` 的情况下创建 V2 后端、Android、数据库 migration、搜索 provider 或 API 实现任务。

---

## 4. 当前任务状态总览

| 任务 | 目标 | 当前状态 |
|---|---|---|
| `task_v1_demo_runbook_and_evidence_pack.md` | 固化可重复 demo 流程并收集真机证据包 | `done` |
| `task_v1_closeout.md` | 将 V1 收口为 demo baseline / learning milestone，并停止继续追加 V1 功能 | `done` |
| `task_v2_planning_baseline_update.md` | 将仓库入口、ADR、roadmap 和 active task 状态对齐到 V2 planning baseline | `done` |
| `task_v2_conversational_sales_agent_definition_update.md` | 将 V2 定义调整为对话式专属销售 agent prototype，并后置 lead research | `done` |

更早的 V1 已完成任务仍可在 `docs/delivery/tasks/` 中按文件名查阅。

---

## 5. 使用规则

执行正式任务前，应至少完成以下动作：

1. 阅读仓库根目录 `AGENTS.md`
2. 阅读 `docs/README.md`
3. 阅读 `docs/delivery/tasks/_active.md`
4. 阅读本目录下对应 task 文档
5. 阅读 task 引用的 PRD / spec / decision 文档
6. 仅在 task 范围内实施最小改动
7. 完成后更新 task 状态并补充 handoff

---

## 6. 历史 handoff 说明

`docs/delivery/handoffs/` 中历史 handoff 只反映当时状态，不作为当前正式路径或当前默认导航依据。

当前正式入口仍以：

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/delivery/tasks/_active.md`

为准。

---

## 7. 当前默认原则

- 优先做 V2.1 对话式销售 agent 定义，不抢跑实现。
- 优先冻结会话、消息、产品画像版本、获客方向版本和 `sales_agent_turn_graph` 边界。
- V2.2 再冻结搜索来源证据、联系方式和 lead research 数据对象边界。
- Android 端仍只做控制入口，不抢后端主存职责。
- Backend services 仍负责正式对象写回裁决。
- Runtime / agent 只产出 draft payload、工具结果和中间推理。
- 若对象模型、页面结构与代码现实冲突，先更新 task / spec，再动实现。
