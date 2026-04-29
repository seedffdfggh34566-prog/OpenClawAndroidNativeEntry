# V2.1 Android Real User Smoke Bugfix Handoff

Date: 2026-04-28

## Scope

Human-authorized real-device smoke for the Android Sales Workspace chat surface. This was treated as bugfix work inside the current V2.1 Android Sales Workspace experience boundary.

## Changed

- Clarified Android first-use 404 handling when backend is reachable but `ws_demo` does not exist.
- Updated Home copy so the primary entry no longer presents the workspace path under a misleading `V1` headline.
- Polished Draft Review terminal state copy after apply so an applied review is shown as already written, not stale/expired.
- Reworded deterministic assistant draft summary from raw `Draft Review` wording to user-facing `可审阅更新`.

## Real Device Smoke

- Device was connected through adb and backend reverse was active: `adb reverse tcp:8013 tcp:8013`.
- Backend was running on `127.0.0.1:8013` with dev diagnostics enabled.
- Installed debug APK and launched `com.openclaw.android.nativeentry/.MainActivity`.
- Verified Home shows `AI 销售助手` and `开始销售工作区`.
- Verified missing default workspace now shows `默认销售工作区尚未创建` with a clear create path.
- Created default workspace from Android.
- Created a named thread: `OPC 客户验证`.
- Entered Chinese smoke text with ADBKeyboard and sent it.
- Verified composer clears after send, user message appears in transcript, Sales Agent reply appears, and Draft Review appears as `可审阅更新`.
- Accepted and wrote the update; workspace moved to `v1`, and card showed `更新建议状态：已写入`, `写入结果：已写入`, and `这条更新已写入工作区`.

## Known Limits

- Smoke used ADBKeyboard for Chinese input; original device IME should be restored after testing if needed.
- Backend session was in-memory for this smoke, so restarting backend resets `ws_demo`.
- This does not claim V2.1 product completion; it is device smoke evidence and bugfix handoff only.

## Next Step

Continue manual testing with the backend left running, or repeat the same path after switching back to the device's normal IME.

## Follow-up Bugfix: LLM Reply Completeness

Additional user feedback found that a real LLM `draft_summary` could say "请补充以下内容" without listing the actual fields. The root cause was backend output assembly: LLM returned `missing_fields`, but `_assistant_message_for_llm_output` only appended `clarifying_questions` for `clarifying_question` messages.

Changes:

- `draft_summary` assistant messages now append user-readable Chinese missing-field prompts.
- `draft_summary` messages now state that the saveable workspace update is below and does not change the formal workspace before write.
- The LLM prompt now requires a complete standalone Chinese answer and forbids dangling "以下内容" wording.
- Android now labels the attachment as `可保存到工作区`, explains the write boundary, and keeps update details folded by default.

Validation:

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_runtime.py -q` passed: `11 passed`.
- `./gradlew :app:assembleDebug` passed.
- Debug APK installed on real device.
- Real LLM backend restarted with `OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=llm` and `OPENCLAW_BACKEND_SALES_AGENT_LLM_PROMPT_VERSION=sales_agent_turn_llm_v1`.
- Real-device smoke sent `你好` and then `产品是 sales agent。它能够帮助中小企业主找到客户，它是一种 agent，能否全自动挖掘客户`; Sales Agent returned concrete follow-up questions instead of a dangling "以下内容".
- Screenshot evidence: `/tmp/openclaw_llm_reply_bugfix.png`.

Known limits:

- The smoke used ADBKeyboard for Chinese input and restored `com.baidu.input_oppo/.ImeService` after testing.
- The backend remains local/in-memory for manual testing; restarting it recreates `ws_demo`.

## Follow-up Bugfix: Lead Direction As Customer-Finding Advice

User feedback clarified that `获客方向` should behave like a customer-finding execution advisor, not a field-collection mode.

Changes:

- Reframed `lead_direction_update` prompt semantics around `找客户建议`: who to prioritize, why, how to find them, screening signals, channels/keywords, and directions to avoid.
- Added backend normalization so actionable `lead_direction_update` turns still generate a reviewable `upsert_lead_direction_version` draft when the LLM tries to only ask questions.
- Kept the write boundary unchanged: drafts are auto-created when patch operations exist, but formal workspace mutation still requires `写入`.
- Rewrote assistant copy when a draft already exists but the LLM says "如果你确认，我可以输出草稿", replacing it with a clear "已整理成下方可保存到工作区的更新".
- Updated Android mode labels and welcome copy from `获客方向` / `产品+方向` to user-facing `找客户建议` / `产品+找客户`.

Validation:

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_runtime.py -q` passed: `14 passed`.
- `./gradlew :app:assembleDebug` passed.
- `adb install -r app/build/outputs/apk/debug/app-debug.apk` passed.
- `git diff --check` passed.
- Real LLM backend was restarted with `OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=llm`, `OPENCLAW_BACKEND_SALES_AGENT_LLM_PROMPT_VERSION=sales_agent_turn_llm_v1`, and dev diagnostics enabled.
- Deep device smoke used ADBKeyboard, then restored `com.baidu.input_oppo/.ImeService`.

Real-device scenario:

- Created thread `拓客AI 找客户验证`.
- Sent `你好`, then product context: `产品是拓客AI，帮助1-20人的小企业老板自动找客户，包含线索搜索、批量触达、跟进提醒。`
- Switched to `找客户建议`.
- Sent `我的客户是什么？我现在应该怎么找第一批客户？`
- Sales Agent gave concrete target customers, priority scenarios, screening signals, channels, and missing items, then auto-showed `可保存到工作区`.
- Before write, workspace stayed `v0`; after `采纳` + `写入`, workspace moved to `v1`.
- Continued with `我没有行业方向，你直接建议` and `给我第一周怎么做`; both returned actionable advice and auto-created saveable drafts.

Known limits / bugs found:

- First `你好` response still exposes internal wording like `message_type 标记为 product_profile_update`; this is user-facing copy polish, not fixed in this scope.
- The folded settings panel compresses transcript while open; the user must tap `收起` to restore the full chat viewport.
- LLM content quality is improved but still variable; it can mention internal names like `lead_direction_version`. Backend now rewrites the most harmful "if you confirm I can output draft" case.
- Backend was restarted after the smoke to load the latest bugfix; the local in-memory `ws_demo` was recreated for manual testing.
