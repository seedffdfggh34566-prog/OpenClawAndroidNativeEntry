# Task: V2 Sales Workspace Prototype Demo Runbook

状态：done

更新时间：2026-04-27

## Objective

在 Android PatchDraft review UI prototype 合入后，补齐当前 V2 Sales Workspace prototype 的可复现 demo runbook。

本任务用于把当前已经跑通的端到端闭环固定下来，避免下一步直接跳进 DB、正式 LangGraph、真实 LLM 或更多 Android 写入 UI。

## Scope

- 新增 demo runbook：
  - `docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`
- 同步入口文档：
  - `README.md`
  - `docs/README.md`
  - `docs/how-to/README.md`
  - `docs/delivery/README.md`
  - `docs/delivery/tasks/_active.md`
- 新增 handoff：
  - `docs/delivery/handoffs/handoff_2026_04_27_v2_sales_workspace_prototype_demo_runbook.md`

## Out Of Scope

- 不改 backend code。
- 不改 Android code。
- 不新增 API route。
- 不实现 DB migration。
- 不接真实 LLM / LangGraph / search / CRM。
- 不开放新的 implementation queue。

## Result

已新增 runbook，覆盖：

- JSON file store backend startup
- `ws_demo` seed
- backend preview / apply smoke
- Android install / launch / `adb reverse`
- Android Workspace 页面 version 3 -> preview -> apply -> version 4 的检查步骤
- 应记录的 evidence
- 常见失败处理

## Validation

- `rg "sales-workspace-prototype-demo-runbook.md" README.md docs`
- `rg "Runtime Draft Co|would_mutate=false|adb reverse tcp:8013 tcp:8013|workspace version" docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`
- `git diff --check`

