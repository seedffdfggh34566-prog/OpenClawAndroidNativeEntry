# V2.1 Sales Workspace memory decision pipeline

Status: done

Date: 2026-04-29

## Objective

Implement a testable V2.1 runtime memory decision pipeline without introducing LangGraph:

`Response LLM -> MemoryEvaluator LLM -> backend deterministic gate -> WorkspacePatchDraft/apply-or-review`.

The goal is to stop runtime suggestions, fallback text, debug phrases, and low-confidence inferred lead directions from polluting formal Sales Workspace memory while still allowing user-supported facts, corrections, and constraints to be persisted.

## Scope

- Add a structured `MemoryDecision` / `MemoryProposal` model for the second LLM pass.
- Add a backend deterministic write gate for evidence, conflict, forbidden text, field permission, and write-level checks.
- Keep the formal write boundary as `WorkspacePatchDraft -> DraftReview/apply record -> WorkspacePatch -> Sales Workspace Kernel`.
- Route auto-apply only when backend gate accepts user-supported facts or corrections.
- Route LLM-inferred direction advice, execution plans, fallback/default values, and conflicting/low-confidence updates to preview or reject.
- Preserve existing product `product_name` / `one_liner` unless the memory proposal explicitly uses `replace` or `correct`.
- Support lead direction positive/excluded list cleanup and simple canonical conflict removal.

## Out of scope

- No LangGraph implementation.
- No MCP implementation.
- No V2.2 search, ContactPoint, CRM, company-list, contact scraping, or auto-outreach.
- No DB migration or new run lifecycle state.
- No Android UI rewrite.
- No product milestone completion claim.

## Key files

- `backend/runtime/sales_workspace_chat_turn_llm.py`
- `backend/runtime/sales_workspace_memory_decision.py`
- `backend/api/sales_workspace.py`
- `backend/sales_workspace/chat_first.py`
- `backend/tests/test_sales_workspace_chat_first_llm_runtime.py`
- `backend/tests/test_sales_workspace_memory_decision_pipeline.py`
- `docs/delivery/handoffs/handoff_2026_04_29_v2_1_sales_workspace_memory_decision_pipeline.md`

## Validation

- Passed: `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_memory_decision_pipeline.py backend/tests/test_sales_workspace_chat_first_llm_runtime.py -q`
- Passed: `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py backend/tests/test_sales_workspace_diagnostics_inspector.py -q`
- Passed: `backend/.venv/bin/python -m pytest backend/tests -q` (`126 passed, 18 skipped`; skips require Postgres verify URL or live Tencent TokenHub smoke env)
- Passed: `git diff --check`

## Outcome

- Done. First-pass LLM now produces the user-facing answer only; formal workspace memory is proposed by a separate MemoryEvaluator pass.
- Done. Runtime no longer inserts fallback product or lead-direction patch operations just because the first-pass LLM omitted them.
- Done. Backend gate rejects fallback/default/debug content and downgrades LLM-inferred lead direction advice to review instead of formal auto-write.
- Done. Product scalar memory is protected from accidental overwrite unless the proposal is explicitly corrective/replacing.
- Done. Lead direction correction can supersede old positive targets and clean positive/excluded conflicts.

## Known limits

- The second pass is still a Python runtime pipeline, not a graph runtime.
- MemoryEvaluator quality depends on model compliance, but backend gate remains the final write-level guard.
- Review-required drafts are materialized and previewed, but not automatically applied by the chat-first route.
- Android device smoke was not required for this backend-focused task unless a real-device LLM run is separately requested.

## Stop conditions

No stop condition triggered. The task stayed inside V2.1 chat-first backend runtime and formal workspace write-boundary constraints.
