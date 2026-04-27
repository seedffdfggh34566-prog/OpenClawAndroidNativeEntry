# Handoff: V2.1 Product Experience Task Queue Planning

日期：2026-04-27

## Summary

本次把 V2.1 product experience 从两个后续 task 扩展为一组可长线程顺序推进的任务队列。

结论：可以在后续一轮长线程中按顺序执行多于两个 task，但应先从 docs/examples 和 trace persistence 开始，再进入 backend prototype、Android UI、demo runbook 和 closeout。

## Proposed Long-thread Queue

1. `task_v2_1_chat_first_runtime_contract_examples.md`
2. `task_v2_1_chat_first_runtime_trace_persistence_schema_design.md`
3. `task_v2_1_chat_first_runtime_trace_persistence_migration_v0.md`
4. `task_v2_1_chat_first_runtime_backend_prototype.md`
5. `task_v2_1_android_chat_first_workspace_ui_prototype.md`
6. `task_v2_1_product_experience_demo_runbook.md`
7. `task_v2_1_product_experience_closeout.md`

## Default Assumptions

- Product direction does not change.
- Chat-first scope remains V2.1 product understanding and lead direction iteration.
- Runtime remains deterministic / prototype until a separate LLM task opens.
- Postgres / Alembic remains V2 MVP persistence baseline.
- Android remains the control and review entry, not the formal truth layer.
- V2.2 evidence / search / ContactPoint remains blocked.

## Known Risks

- Backend prototype may reveal schema details that require small schema design adjustments.
- Android device-level verification depends on available `adb` device.
- Full V2.1 closeout should not claim real LLM or V2.2 research support.

## Recommended Next Step

After PR #26 is merged, open the long-thread queue starting with:

- `task_v2_1_chat_first_runtime_contract_examples.md`
