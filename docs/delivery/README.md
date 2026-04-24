# 任务目录说明

更新时间：2026-04-23

## 1. 目录定位

本目录用于承载当前项目的正式任务文档。

任务文档的作用不是重复 PRD 或 spec，而是把已经明确的方向拆成可以独立执行、独立验证、独立交接的小闭环。

---

## 2. 当前阶段说明

当前项目已经完成：

- 主线切换到 AI 销售助手 V1
- V1 范围与非目标初步收口
- 本地服务器承载正式后端的部署基线明确
- 文档体系、runbook 和 decision 骨架建立

当前项目尚未完成：

- 第一批正式开发任务的连续推进
- 真实 OpenClaw runtime 与正式后端的最小接入

因此，当前阶段的重点是：

> 从“方向与原则已明确”推进到“任务可执行、实现可收口”。

---

## 3. 当前推荐执行顺序

建议按以下顺序进入下一批任务：

1. AnalysisResult 详情 contract / 页面 follow-up task
2. 真实 OpenClaw runtime 接入 follow-up task
3. 报告导出 / 分享 follow-up task

原因如下：

- 文档结构现已切到新 docs 架构，后续任务应直接按新入口推进
- Android 已完成从占位数据切到真实 `/history` 与对象详情读取
- Android 已完成最小 ProductProfile 创建
- Android 已完成 `lead_analysis` 触发与轮询
- Android 已完成 `report_generation` 触发与轮询
- 当前最有价值的是补齐 AnalysisResult 详情 contract 与页面读取
- runtime 真实接入应在对象读写与详情链路稳定后继续推进

---

## 4. 当前任务状态总览

| 任务 | 目标 | 当前状态 |
|---|---|---|
| `task_v1_domain_model_baseline.md` | 定义 V1 正式业务对象与状态流转基线 | `done` |
| `task_v1_information_architecture.md` | 明确手机端 V1 页面结构与核心闭环入口 | `done` |
| `task_v1_android_control_shell_refactor.md` | 将现有 Android 入口重构为 AI 销售助手控制壳层 | `done` |
| `task_v1_backend_api_contract.md` | 冻结 V1 最小后端 API contract 与历史状态查询边界 | `done` |
| `task_backend_first_repo_and_docs_alignment.md` | 对齐后端优先的仓库理解、docs 入口与 agent 工作流 | `done` |
| `task_docs_structure_migration.md` | 将 docs 从旧编号目录迁移到新 docs 架构 | `done` |
| `task_docs_migration_review_and_old_path_cleanup.md` | 复核 docs 迁移结果并清理旧路径与旧项目叙事残留 | `done` |
| `task_v1_backend_minimum_implementation.md` | 落地 V1 最小正式后端实现 | `done` |
| `task_v1_android_minimum_real_backend_integration.md` | 让 Android 壳层切到真实 `/history`、`ProductProfile` 与报告读取 | `done` |
| `task_v1_android_minimum_product_profile_write_path.md` | 让 Android 壳层创建第一版 ProductProfile 草稿 | `done` |
| `task_v1_android_analysis_run_trigger_poll.md` | 让 Android 壳层触发 lead_analysis 并轮询 AgentRun | `done` |
| `task_v1_android_report_generation_trigger_poll.md` | 让 Android 壳层触发 report_generation 并打开 AnalysisReport | `done` |
| `task_v1_analysis_result_detail_contract.md` | 补齐 AnalysisResult 详情 contract 与页面读取 | `planned` |

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

`docs/delivery/handoffs/` 中 2026-04-23 文档结构迁移前的 handoff，可能仍保留旧目录名或旧阶段表述。

这些内容只反映当时状态，不作为当前正式路径或当前默认导航依据。当前正式入口仍以：

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/delivery/tasks/_active.md`

为准。

---

## 7. 当前默认原则

- 优先做小闭环，不做大重构
- 优先把 AI 销售助手 V1 的新主线落成，而不是继续扩展旧 OpenClaw 入口功能
- Android 端当前只做控制入口，不抢后端主存职责
- 正式后端实现当前优先级高于继续扩展 Android 壳层
- 若对象模型、页面结构与代码现实冲突，先更新 task / spec，再动实现
