# Task: V2.1 Demo Reproducibility Hardening

更新时间：2026-04-28

## 1. 任务定位

- 任务名称：V2.1 Demo Reproducibility Hardening
- 建议路径：`docs/delivery/tasks/task_v2_1_demo_reproducibility_hardening.md`
- 当前状态：`done`
- 优先级：P1
- 任务类型：`delivery`
- 是否属于 delivery package：`yes`
- 所属 package：`V2.1 Implementation Continuation`

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 当前 task 内部 steps 是否允许连续执行：`yes`
- 完成后是否允许自动进入下游任务：`yes`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：
  1. `docs/delivery/tasks/task_v2_1_android_workspace_onboarding.md`
- 自动继续条件：
  - 只补强 V2.1 demo 复现文档和 smoke 步骤。
  - 不新增 backend / Android 功能。
- 停止条件：
  - 需要新增 API、migration、search/contact 或 formal LangGraph。

---

## 2. 任务目标

补强 V2.1 product experience demo runbook，使开发者能更稳定地复现 backend health、workspace seed/reset、chat-first product/direction smoke、Android adb reverse 和常见失败排查。

---

## 3. 范围

In Scope：

- 更新 `docs/how-to/operate/v2-1-product-experience-demo-runbook.md`。
- 创建本任务 handoff。
- 更新 `_active.md` 和 package 状态衔接。

Out of Scope：

- 新增 backend API。
- 修改 Android UI。
- 修改 runtime / LLM 行为。
- 执行 V2.2 search / contact。

---

## 4. 实际产出

- 新增 `docs/delivery/packages/package_v2_1_implementation_continuation.md`。
- 补强 V2.1 demo runbook 的 workspace reset、health check、smoke 和 troubleshooting。
- 新增 handoff：`docs/delivery/handoffs/handoff_2026_04_28_v2_1_demo_reproducibility_hardening.md`。
- `_active.md` 当前任务衔接到 P2 Android onboarding。

---

## 5. 已做验证

- `git diff --check`

---

## 6. 实际结果说明

本任务仅修改 docs，不修改 backend / Android 代码。V2.2 implementation 继续 blocked。
