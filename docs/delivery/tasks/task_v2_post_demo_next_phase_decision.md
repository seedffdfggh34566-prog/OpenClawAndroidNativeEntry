# Task: V2 Post-Demo Next Phase Decision

状态：done

更新时间：2026-04-27

## Objective

在 V2 Sales Workspace prototype demo runbook 合入 `main` 并完成一次 clean demo verification 后，冻结下一阶段推荐方向。

本任务只做规划决策，不实现新代码、不开放新的自动 implementation queue。

## Current Baseline

已完成并验证的闭环：

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

Clean demo verification 已完成：

- backend health check passed
- `ws_demo` seeded to version 3
- backend preview returned `cand_runtime_001` as preview rank #1
- preview did not mutate workspace; workspace stayed version 3
- backend apply changed workspace to version 4
- ranking board and ContextPack returned `cand_runtime_001` first
- Android build passed
- `adb devices` detected `f3b59f04`
- `adb reverse tcp:8013 tcp:8013`
- Android app installed and launched
- Android Workspace page showed version 3 before apply
- Android preview showed `draft_runtime_v4`, `patch_runtime_v4`, `would_mutate=false`, and `Runtime Draft Co`
- Android apply refreshed Workspace page to version 4 and showed `Runtime Draft Co` ranked first

## Decision

下一阶段推荐方向：

> **先定义 Draft persistence / review history contract，不直接进入 DB、LangGraph、真实 LLM 或 Android UX 扩展。**

推荐新任务名：

```text
docs/delivery/tasks/task_v2_sales_workspace_draft_review_contract.md
```

该任务应是 docs / contract first，目标是定义：

- `WorkspacePatchDraft` 是否成为 backend 可持久化 review object。
- draft lifecycle：`previewed`、`reviewed`、`applied`、`rejected`、`expired`。
- review metadata：reviewer、reviewed_at、instruction、source runtime metadata。
- apply result：materialized patch id、workspace version、failure reason。
- version conflict / stale draft 语义。
- Android 是否只引用 draft id，还是继续回传 raw draft。
- JSON store prototype 是否足够支持下一轮 demo，或是否需要刷新 persistence decision。

## Options Considered

### 1. Draft persistence / review history contract

优点：

- 直接补齐当前 prototype 最薄弱的边界。
- 让 preview / review / apply 从临时 UI 状态走向可审计对象。
- 为后续 DB decision 和 Runtime integration 提供稳定输入。

结论：

> 作为下一阶段首选。

### 2. Runtime / LangGraph integration design

优点：

- 能更快接近真实 Product Sales Agent 执行流。

风险：

- 如果 draft review object 未定义，LangGraph 输出会缺少稳定落点。
- 容易让 Runtime 被误当成 formal truth layer。

结论：

> 放在 draft review contract 之后。

### 3. DB-backed persistence decision refresh

优点：

- 可以开始解决长期状态保存、多设备和审计历史问题。

风险：

- 若 draft lifecycle 未定义，DB schema 容易过早锁死。

结论：

> draft review contract 完成后再刷新 persistence decision。

### 4. Android review UX expansion

优点：

- 可以改善演示体验。

风险：

- 当前 Android 已能完成闭环，继续扩 UI 会绕开更关键的 backend review model。

结论：

> 暂不作为下一阶段首选。

## Non-Goals

本决策不开放：

- backend code changes
- new FastAPI route
- DB migration
- SQLAlchemy ORM
- formal LangGraph graph
- real LLM / search / contact / CRM
- Android write UI expansion
- production persistence baseline

## Validation

- Clean demo verification completed against current `main` after PR #13 merge。
- `git diff --check`
- `rg "Draft persistence|draft lifecycle|task_v2_sales_workspace_draft_review_contract" docs/delivery docs/README.md README.md`

