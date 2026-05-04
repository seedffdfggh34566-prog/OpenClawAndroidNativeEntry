# V2.1 context defect device deep test after memory pipeline

Status: done

Date: 2026-04-29

## Objective

Run a real-device LLM context defect test after the V2.1 Sales Workspace memory decision pipeline landed.

The test must use two different user styles, with at least 12 Sales Agent turns per style, and focus on why the current LLM context system still feels unsatisfactory.

## Scope

- Start a temporary local backend with real LLM runtime enabled.
- Connect a physical Android device through `adb reverse tcp:8013 tcp:8013`.
- Launch the Android app on device and collect device evidence.
- Execute two 12-turn Sales Agent conversations against the same backend used by the device session.
- Inspect assistant replies, MemoryEvaluator decisions, backend deterministic gate decisions, draft review state, and final formal workspace state.
- Record context engineering defects and recommended fixes in a handoff report.

## Out of scope

- No backend or Android implementation changes.
- No LangGraph implementation.
- No V2.2 search/contact/company-list implementation.
- No DB migration.
- No milestone completion claim.

## Key files

- `docs/delivery/handoffs/handoff_2026_04_29_v2_1_context_defect_device_deep_test_memory_pipeline.md`
- `/tmp/openclaw_context_defect_device/context_defect_run_results.json`
- `/tmp/openclaw_context_defect_device/traces/`
- `/tmp/openclaw_context_defect_device/android_workspace_screen.png`

## Validation

- Passed: `./gradlew :app:assembleDebug`
- Passed: `adb devices` detected `f3b59f04`.
- Passed: backend `/health` returned `{"status":"ok"}` on `127.0.0.1:8013`.
- Passed: `adb reverse tcp:8013 tcp:8013`.
- Passed: Android debug APK installed and launched.
- Completed: two user styles, 12 Sales Agent turns each, 24 real LLM turns total.
- Captured: 24 LLM trace files.

## Outcome

Done. The test found severe context/memory defects after the memory decision pipeline:

- formal workspace memory barely accumulates across turns;
- lead direction never becomes formal memory in either 12-turn scenario;
- MemoryEvaluator output often uses non-canonical fields that backend gate discards;
- assistant replies treat conversation facts as "confirmed" even when formal workspace state has not changed;
- review-required drafts are not productively surfaced in the main chat path;
- two LLM calls per turn create long mobile-facing latency.

## Stop conditions

No product direction stop condition was triggered. The result is evidence for follow-up planning, not a product-stage closeout.
