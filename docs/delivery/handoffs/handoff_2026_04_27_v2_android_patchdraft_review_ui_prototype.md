# Handoff: V2 Android PatchDraft Review UI Prototype

日期：2026-04-27

## Summary

本次在 PR #11 的 PatchDraft review gate backend prototype 合入后，补齐 Android Workspace 页面的最小人工审阅 UI。

Android 现在可以：

- 读取固定 prototype workspace：`ws_demo`
- 基于当前 workspace version 请求 Runtime PatchDraft preview
- 展示 draft / patch / preview ranking / `would_mutate=false`
- 将已审阅的 `patch_draft` raw JSON 原样回传 backend apply endpoint
- apply 成功后刷新 workspace、ranking、projection 和 ContextPack

## Files Changed

- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/SalesWorkspaceBackendClient.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/SalesWorkspaceBackendModels.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/SalesWorkspaceBackendJsonParser.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/navigation/OpenClawNavHost.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/workspace/SalesWorkspaceScreen.kt`
- `docs/delivery/tasks/task_v2_android_patchdraft_review_ui_prototype.md`
- `docs/delivery/tasks/_active.md`
- `README.md`
- `docs/README.md`
- `docs/delivery/README.md`

## Validation

- `PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py -q`
  - 24 passed
- `PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests -q`
  - 71 passed
- `./gradlew :app:assembleDebug`
  - passed
- `./gradlew :app:lintDebug`
  - passed
- Backend smoke with JSON store on `127.0.0.1:8013`
  - seed `ws_demo` to version 3
  - preview returned `cand_runtime_001` as preview rank #1
  - preview did not mutate workspace; workspace stayed version 3
  - apply changed workspace to version 4
  - ranking board and ContextPack returned `cand_runtime_001` first
- Device smoke
  - `adb devices` detected `f3b59f04`
  - `adb reverse tcp:8013 tcp:8013`
  - installed and launched `app-debug.apk`
  - Workspace page showed version 3 before apply
  - preview UI showed `draft_runtime_v4`, `patch_runtime_v4`, `would_mutate=false`, and `Runtime Draft Co`
  - apply refreshed Workspace page to version 4 and showed `Runtime Draft Co` ranked first

## Known Limits

- Android still targets fixed prototype workspace `ws_demo`。
- Draft is not persisted as a separate review object; Android receives preview and sends the raw `patch_draft` back to apply。
- This is deterministic prototype behavior only；no real LLM、formal LangGraph graph、search/contact/CRM or production persistence was added。
- Android does not construct formal workspace objects or write ranking / Markdown / ContextPack directly。

## Recommended Next Step

Stop automatic implementation here. The next step should be planning-level selection between:

- better Android review UX for multiple draft types
- formal draft persistence / review history
- Runtime / LangGraph integration design
- DB-backed persistence baseline

