# Handoff: V2.1 Android OpenClaw-Style Multi-Thread Chat

日期：2026-04-28

## Changed

- Backend added Sales Workspace conversation threads with default `main` compatibility.
- Backend added thread-scoped message and sales-agent-turn APIs while keeping old endpoints mapped to `main`.
- Android backend DTO/parser/client now supports thread list/create and thread-scoped messages / turns.
- Android Workspace now shows thread switcher, “新对话”, a larger transcript-first chat area, and a fixed bottom composer.
- Temporary backend is running on `127.0.0.1:8013` for manual testing with LLM runtime mode.

## Validation

- Backend targeted tests passed: `21 passed, 1 skipped`.
- Alembic upgrade passed.
- Android debug build passed.
- Device install/start passed.
- UIAutomator confirmed Home entry “开始销售工作区”.
- UIAutomator confirmed Workspace thread switcher, transcript, composer “对 Sales Agent 说”, and send button are visible.
- API smoke confirmed two Chinese threads under `ws_demo` do not share message history.
- Real LLM smoke succeeded on both threads with `real_llm_no_langgraph`.

## Known Limits

- The manual-test backend uses SQLite + JSON store; chat trace is process-local in this mode.
- Android does not yet implement streaming, abort, inject, auth, tenant, CRM, V2.2 search/contact, or formal LangGraph.
- This is task/package evidence, not V2.1 milestone completion.

## Recommended Next Step

Human should manually test the running backend + Android app, especially creating a new thread from the “新对话” button and sending a Chinese message through the device IME.

## Follow-up: Compact Chat UI Bugfix

日期：2026-04-28

Changed：

- `OpenClawApp.kt` now hides global top/bottom chrome only on the Workspace route.
- `SalesWorkspaceScreen.kt` now uses a compact Workspace header, large transcript body, fixed compact composer, folded settings/details panel, lighter message metadata, and Preview mock cases.

Validation：

- `./gradlew :app:assembleDebug` passed.
- `./gradlew :app:lintDebug` passed.
- Device install/start passed on `f3b59f04`.
- UIAutomator confirmed Home entry, Workspace transcript-first layout, “新对话”, composer “对 Sales Agent 说”, folded “回复模式 / 工作区详情”, and thread switching.
- ADBKeyboard Chinese smoke submitted “我们做工业设备维保软件”; Android showed the user message and Sales Agent follow-up in transcript.

Known limits：

- The smoke assistant response was still the existing five-question follow-up; this UI bugfix did not modify backend runtime selection or LLM prompt behavior.
- Settings/details is intentionally folded and capped in height to preserve transcript space.

## Follow-up: Chat Interaction State Bugfix

日期：2026-04-28

Changed：

- `OpenClawApp.kt` now keeps a thread-scoped optimistic user message, clears the composer immediately on send, and keeps applied Draft Review state after writeback.
- `SalesWorkspaceScreen.kt` now merges optimistic/user/assistant messages into transcript, shows a naming dialog before creating a thread, and removes the main-chat “生成可审阅更新” loop.
- No backend API, schema, migration, LLM runtime, search/contact, CRM, or formal LangGraph changes.

Validation：

- `./gradlew :app:assembleDebug` passed.
- `./gradlew :app:lintDebug` passed.
- Device install/start passed on `f3b59f04`.
- UIAutomator confirmed the new thread naming dialog and a created thread titled `OPC 客户验证`.
- ADBKeyboard Chinese smoke confirmed send clears composer immediately, user bubble appears before backend response, and `Sales Agent 正在思考...` is visible.
- Draft Review smoke confirmed accept keeps workspace at v5, apply advances to v6, and the card shows applied terminal state without the “生成可审阅更新” button.

Known limits：

- The developer workspace/kernel/data-store visualization page was not implemented; it should be a separate dev-only read-only diagnostics task.
