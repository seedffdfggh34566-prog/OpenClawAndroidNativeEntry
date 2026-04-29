# V2.1 Sales Workspace memory merge and auto-write bugfix

Status: done

Date: 2026-04-29

## Objective

Fix the Sales Workspace memory regression where later customer-finding questions can overwrite an already-clear product profile with placeholder values such as "待确认".

The chat-first turn should now treat the current formal product profile and lead direction as the memory baseline, merge useful new information into those cards, and automatically persist valid V2.1 product / lead-direction updates.

## Scope

- Thicken chat-first `ContextPack` with full current product profile / lead direction and more same-thread message history.
- Add backend merge guard before materializing LLM patch drafts.
- Auto-apply valid chat-first product / lead-direction patch drafts to the formal workspace.
- Keep `WorkspacePatchDraftReview` as an audit record with `status=applied`.
- Refresh Android workspace snapshot after a successful chat turn.
- Change the Android main transcript attachment from "可保存到工作区" to "已沉淀到工作区" when the backend auto-applied the update.

## Out of scope

- No new backend API.
- No schema or migration change.
- No V2.2 search, ContactPoint, CRM, auto-outreach, or formal LangGraph implementation.
- No PRD, roadmap, project status, or milestone review update.

## Validation

- Passed: `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_runtime.py -q`
- Passed: `./gradlew :app:assembleDebug`
- Passed: `./gradlew :app:lintDebug`
- Passed: `git diff --check`
- Passed light device smoke: installed and launched debug APK; UIAutomator confirmed Home entry and Workspace composer.

## Outcome

- Done. Backend now auto-applies valid chat-first product / lead-direction updates and preserves old confirmed card fields when LLM output contains unknown or placeholder values.
- Done. `lead_direction_update` no longer accepts opportunistic product profile replacement operations from the LLM, preventing "how do I find customers" turns from degrading product memory.
- Done. Android refreshes the workspace snapshot after successful turns and displays applied updates as "已沉淀到工作区".

## Stop conditions

No stop condition triggered. The change stayed inside the V2.1 chat-first Sales Workspace bugfix boundary.
