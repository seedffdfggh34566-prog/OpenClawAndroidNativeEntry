# Handoff: V2 Post-Demo Next Phase Decision

日期：2026-04-27

## Summary

PR #13 已合并，V2 Sales Workspace prototype demo runbook 已进入 `main`。

本次按 runbook 做了一次 clean demo verification，并新增 post-demo 下一阶段决策：

> 下一阶段应先定义 Draft persistence / review history contract，不直接进入 DB、正式 LangGraph、真实 LLM 或 Android UX 扩展。

## Clean Demo Verification

- Backend health check passed。
- `ws_demo` seeded to version 3。
- Backend preview returned `cand_runtime_001` as preview rank #1。
- Preview did not mutate workspace；workspace stayed version 3。
- Backend apply changed workspace to version 4。
- Ranking board and ContextPack returned `cand_runtime_001` first。
- `./gradlew :app:assembleDebug` passed。
- `adb devices` detected `f3b59f04`。
- `adb reverse tcp:8013 tcp:8013` succeeded。
- Android app installed and launched。
- Android Workspace page showed version 3 before apply。
- Android preview showed `draft_runtime_v4`, `patch_runtime_v4`, `would_mutate=false`, and `Runtime Draft Co`。
- Android apply refreshed Workspace page to version 4 and showed `Runtime Draft Co` ranked first。

## Files Changed

- `docs/delivery/tasks/task_v2_post_demo_next_phase_decision.md`
- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_contract.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`
- `docs/README.md`
- `README.md`

## Decision

Recommended next task:

- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_contract.md`

Why:

- Current prototype stores previewed draft only in Android UI state。
- A real product needs review history, stale draft handling, apply result, reviewer metadata, and auditability。
- Defining draft review contract first gives DB persistence and Runtime / LangGraph integration a stable target。

## Still Blocked

- DB-backed persistence implementation。
- SQLAlchemy / Alembic / SQLite schema。
- Formal LangGraph graph。
- Real LLM / search / contact / CRM。
- Additional Android write UI。
- Production persistence baseline。

## Recommended Next Step

If continuing, execute `task_v2_sales_workspace_draft_review_contract.md` as a docs / contract task first。

Do not implement backend routes or DB schema until that contract is complete and persistence decision is refreshed if needed。

