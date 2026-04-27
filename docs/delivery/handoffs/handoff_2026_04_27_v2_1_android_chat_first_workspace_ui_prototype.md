# Handoff: V2.1 Android Chat-first Workspace UI Prototype

日期：2026-04-27

## 1. Changed

- Added a minimal chat-first input section to the existing Android Workspace page.
- Added Android client calls for backend `ConversationMessage` creation and `AgentRun(run_type=sales_agent_turn)` execution.
- The generated Draft Review is displayed and then reviewed/applied through existing backend Draft Review routes.
- Android still does not construct formal `WorkspacePatch` objects.

## 2. Files

- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/SalesWorkspaceBackendClient.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/SalesWorkspaceBackendJsonParser.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/SalesWorkspaceBackendModels.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/navigation/OpenClawNavHost.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/workspace/SalesWorkspaceScreen.kt`

## 3. Validation

Passed:

```bash
./gradlew :app:assembleDebug
./gradlew :app:lintDebug
adb devices
```

`adb devices` reported one connected device: `f3b59f04`.

## 4. Limits

- No Manifest, Gradle, navigation structure, Room, Retrofit, Hilt, real LLM, LangGraph, search, ContactPoint, CRM, or Android free-write changes.
- Full hands-on device UI flow should still be covered by the product experience demo runbook.

## 5. Next

Proceed to `task_v2_1_product_experience_demo_runbook.md`.
