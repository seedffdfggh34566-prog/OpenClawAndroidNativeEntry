# Handoff: V2 Sales Workspace Prototype Demo Runbook

日期：2026-04-27

## Summary

PR #12 已合并，Android PatchDraft review UI prototype 已进入 `main`。

本次新增 V2 Sales Workspace prototype demo runbook，把当前端到端 prototype 固定为可复现流程：

```text
JSON store backend
-> seed ws_demo
-> Android Workspace reads version 3
-> Runtime PatchDraft preview
-> preview does not mutate workspace
-> Android applies reviewed draft
-> backend kernel writes formal workspace
-> Android refreshes to version 4 with Runtime Draft Co ranked first
```

## Files Changed

- `docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`
- `docs/delivery/tasks/task_v2_sales_workspace_prototype_demo_runbook.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`
- `docs/how-to/README.md`
- `docs/README.md`
- `README.md`

## Validation

- `rg "sales-workspace-prototype-demo-runbook.md" README.md docs`
- `rg "Runtime Draft Co|would_mutate=false|adb reverse tcp:8013 tcp:8013|workspace version" docs/how-to/operate/sales-workspace-prototype-demo-runbook.md`
- `git diff --check`

## Current State

- Current task: none。
- Next queued task: none。
- Android read-only + controlled PatchDraft apply demo is now documented。
- DB-backed persistence, formal LangGraph, real LLM/search/contact/CRM, and additional Android write UI remain blocked unless a future task explicitly opens them。

## Recommended Next Step

Use this runbook once as a clean release-style demo verification after merge.

After that, planning should choose one next direction explicitly:

1. Formal draft persistence / review history。
2. Runtime / LangGraph integration design。
3. DB-backed persistence decision refresh。
4. Android review UX expansion。

