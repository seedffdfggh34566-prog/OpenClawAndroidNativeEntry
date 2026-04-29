# Handoff: V2.1 Sales Workspace Answer Quality And Device Bugfix

日期：2026-04-29

## Changed

- Backend LLM runtime：
  - transient `TokenHubClientError` 增加一次请求级 retry。
  - runtime metadata 增加 `llm_request_attempts`。
  - prompt 明确禁止用户可见回复泄露 schema / runtime / internal ids。
  - product profile update 在已有产品/服务描述时补最小 draft fallback。
- Backend API formatter：
  - 统一格式化 LLM assistant message。
  - 悬空“请补充以下内容”会补具体中文缺失项。
  - 清洗 `patch_operations`、`revision_id`、`workspace_goal`、`blocked_capabilities`、`ContextPack` 等内部术语。
- Android workspace：
  - Settings 面板上移到 transcript 前，点击后可直接看到“回复模式”。
  - Settings 增加 dev/test “开发测试工作区 ID” selector，使用现有 create/get workspace flow。
  - 发送消息改成先创建/保留 user message，再运行 Sales Agent；LLM 失败时保留 user bubble。
  - LLM unavailable/timeout 显示“重试”，重试复用同一个 message id，不重复创建用户消息。

## Files Touched

- `backend/runtime/sales_workspace_chat_turn_llm.py`
- `backend/api/sales_workspace.py`
- `backend/tests/test_sales_workspace_chat_first_llm_runtime.py`
- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/SalesWorkspaceBackendClient.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/navigation/OpenClawNavHost.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/workspace/SalesWorkspaceScreen.kt`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/tasks/task_v2_1_sales_workspace_answer_quality_and_device_bugfix.md`
- `docs/delivery/handoffs/handoff_2026_04_29_v2_1_sales_workspace_answer_quality_and_device_bugfix.md`

## Validation

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_runtime.py -q`
  - passed：`17 passed`
- `./gradlew :app:assembleDebug`
  - passed
- `./gradlew :app:lintDebug`
  - passed
- `git diff --check`
  - passed
- Device smoke on `f3b59f04`
  - `adb reverse tcp:8013 tcp:8013` succeeded
  - backend `/health` returned `{"status":"ok"}` on `127.0.0.1:8013` in LLM mode
  - `adb install -r app/build/outputs/apk/debug/app-debug.apk` succeeded
  - app launch succeeded
  - Home showed `开始销售工作区`
  - Workspace showed `主对话`、`新对话`、`对 Sales Agent 说`
  - Settings showed `开发测试工作区 ID`、`切换/创建`、`回复模式`、`产品理解`、`找客户建议`
  - ADBKeyboard Chinese smoke succeeded; user bubble appeared immediately and `Sales Agent 正在思考...` showed before assistant return
  - real LLM run returned `run_sales_turn_001 succeeded main real_llm_no_langgraph 1`
  - draft review card showed `可保存到工作区`
  - screenshot: `/tmp/openclaw_answer_quality_bugfix/workspace_settings_and_draft.png`

## Known Limits

- Dev/test workspace selector is intentionally scoped to local testing; it is not a formal multi-workspace product surface.
- No backend schema, migration, formal endpoint, V2.2 search/contact, CRM, streaming, abort, inject, or formal LangGraph work was added.
- Real LLM smoke still depends on valid local backend environment and device connectivity; deterministic fallback must not be used to claim real LLM acceptance.
- If TokenHub or provider remains unavailable after retry, the API still returns `llm_runtime_unavailable`; Android keeps the user message and offers retry.
- The device smoke kept the local backend running on `127.0.0.1:8013` for manual follow-up testing.

## Recommended Next Step

- Run device smoke with real backend:
  - `adb reverse tcp:8013 tcp:8013`
  - install debug APK
  - launch app
  - open Workspace Settings
  - switch/create a deep-test workspace
  - verify one real LLM send/retry path and inspect diagnostics.

## Stop Condition

No stop condition triggered by this implementation. Stop after validation and handoff; do not auto-open another package.
