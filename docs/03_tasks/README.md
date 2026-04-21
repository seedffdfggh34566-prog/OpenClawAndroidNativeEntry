# 任务目录说明

更新时间：2026-04-21

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
- 后端最小 API contract 已完成文档冻结，但实现尚未开始

因此，当前阶段的重点是：

> 从“方向与原则已明确”推进到“任务可执行、实现可收口”。

---

## 3. 当前推荐执行顺序

建议按以下顺序推进第一批任务：

1. `task_v1_domain_model_baseline.md`
2. `task_v1_information_architecture.md`
3. `task_v1_android_control_shell_refactor.md`

原因如下：

- 先冻结正式对象和状态，避免后续页面与接口各自理解不同
- 再明确手机端的页面结构、入口关系和最小闭环
- 最后在 Android 代码中做小步重构，降低返工成本

---

## 4. 当前任务状态总览

| 任务 | 目标 | 当前状态 |
|---|---|---|
| `task_v1_domain_model_baseline.md` | 定义 V1 正式业务对象与状态流转基线 | `done` |
| `task_v1_information_architecture.md` | 明确手机端 V1 页面结构与核心闭环入口 | `done` |
| `task_v1_android_control_shell_refactor.md` | 将现有 Android 入口重构为 AI 销售助手控制壳层 | `done` |
| `task_v1_backend_api_contract.md` | 冻结 V1 最小后端 API contract 与历史状态查询边界 | `done` |

---

## 5. 使用规则

执行正式任务前，应至少完成以下动作：

1. 阅读仓库根目录 `AGENTS.md`
2. 阅读本目录下对应 task 文档
3. 阅读 task 引用的 PRD / spec / decision 文档
4. 仅在 task 范围内实施最小改动
5. 完成后更新 task 状态并补充 handoff

---

## 6. 当前默认原则

- 优先做小闭环，不做大重构
- 优先把 AI 销售助手 V1 的新主线落成，而不是继续扩展旧 OpenClaw 入口功能
- Android 端当前只做控制入口，不抢后端主存职责
- 若对象模型、页面结构与代码现实冲突，先更新 task / spec，再动实现
