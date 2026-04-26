# 任务目录说明

更新时间：2026-04-26

## 1. 目录定位

本目录用于承载当前项目的正式任务文档。

任务文档的作用不是重复 PRD 或 spec，而是把已经明确的方向拆成可以独立执行、独立验证、独立交接的小闭环。

---

## 2. 当前阶段说明

当前项目已经完成：

- AI 销售助手 V1 demo-ready release candidate / learning milestone closeout。
- V1 demo runbook 与 evidence pack。
- V2 workspace-native sales agent 产品北极星更新。
- V2 Sales Workspace object model 草案。
- V2 Sales Workspace Kernel backend-only v0 设计。

当前项目处于：

> **V2 workspace-native sales agent planning baseline / Sales Workspace Kernel backend-only v0 阶段**

当前阶段重点是先验证 Sales Workspace Kernel 的最小 backend-only 状态机，不自动进入数据库、API、Android、LangGraph、LLM 或搜索实现。

---

## 3. 当前任务状态

当前正式任务队列以 `_active.md` 为准。

当前入口：

- Current task：`task_v2_sales_workspace_kernel_backend_only_v0.md`
- Next queued tasks：暂无自动排定

当前允许执行的范围仅限：

- Pydantic schema
- in-memory / JSON fixture store
- WorkspacePatch apply
- deterministic candidate ranking
- Markdown projection
- ContextPack compiler
- pytest

---

## 4. 当前任务状态总览

| 任务 | 目标 | 当前状态 |
|---|---|---|
| `task_v2_sales_workspace_direction_update.md` | 将 V2 北极星升级为 workspace-native sales agent | `done` |
| `task_v2_workspace_object_model.md` | 定义 Sales Workspace 核心对象模型 | `done` |
| `task_v2_sales_workspace_kernel_backend_only_v0.md` | 实现 Sales Workspace Kernel backend-only v0 | `current` |
| `task_v2_conversational_sales_agent_definition_update.md` | 2026-04-25 旧 V2 定义更新 | `done / superseded by workspace-native direction` |
| `task_v2_planning_baseline_update.md` | 将仓库入口、ADR、roadmap 和 active task 状态对齐到 V2 planning baseline | `done` |
| `task_v1_closeout.md` | 将 V1 收口为 demo baseline / learning milestone，并停止继续追加 V1 功能 | `done` |
| `task_v1_demo_runbook_and_evidence_pack.md` | 固化可重复 demo 流程并收集真机证据包 | `done` |

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

- 优先做 Sales Workspace Kernel，而不是继续扩展 V1 线性报告链路。
- 结构化对象是主真相，Markdown 是 projection，不是唯一主存。
- WorkspacePatch 是 workspace 状态变更入口。
- CandidateRankingBoard 必须由 deterministic ranking 派生，不能由 Product Sales Agent / Runtime draft 直接写入。
- ContextPack 从结构化 workspace state 编译，不读取 Markdown、LangGraph checkpoint 或 SDK session。
- Android 端仍只做控制入口，不抢后端主存职责。
- Backend services / workspace kernel 负责正式对象写回裁决。
- Runtime / Product Sales Agent execution layer 后续只产出 draft payload、工具结果和中间推理。
- 若对象模型、页面结构与代码现实冲突，先更新 task / spec，再动实现。
