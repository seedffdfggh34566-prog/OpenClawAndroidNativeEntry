# Handoff: V2.1 Sales Workspace memory decision pipeline

Date: 2026-04-29

## Changed

- `backend/runtime/sales_workspace_memory_decision.py`
  - Added `MemoryDecision`, `MemoryProposal`, source evidence, gate result, and patch build models.
  - Added MemoryEvaluator prompt construction and JSON parsing.
  - Added backend deterministic gate checks for user quote evidence, forbidden/debug text, placeholder values, field merge semantics, and lead-direction conflicts.
  - Produces `WorkspacePatchDraft` only after accepted memory proposals.
- `backend/runtime/sales_workspace_chat_turn_llm.py`
  - Split the runtime into first-pass user-facing response and second-pass MemoryEvaluator decision.
  - Removed first-pass fallback patch insertion as the formal memory source.
  - Records `memory_decision` and `memory_gate` metadata in the agent run.
- `backend/api/sales_workspace.py`
  - Applies patch drafts only when `memory_gate.decision == auto_apply`.
  - Keeps `review_required` drafts as previewed draft reviews without mutating formal workspace state.
  - Sanitizes assistant copy so rejected/no-draft turns do not claim memory was saved.
- `backend/tests/test_sales_workspace_memory_decision_pipeline.py`
  - Added gate-level regression coverage for user-supported product constraints, inferred direction review, forbidden/debug rejection, and correction cleanup.
- `backend/tests/test_sales_workspace_chat_first_llm_runtime.py`
  - Updated LLM runtime tests for the two-pass memory pipeline, new draft IDs, review-required lead advice, and response/evaluator call counts.

## Validation

- Passed: `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_memory_decision_pipeline.py backend/tests/test_sales_workspace_chat_first_llm_runtime.py -q`
- Passed: `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py backend/tests/test_sales_workspace_diagnostics_inspector.py -q`
- Passed: `backend/.venv/bin/python -m pytest backend/tests -q` (`126 passed, 18 skipped`; skips require Postgres verify URL or live Tencent TokenHub smoke env)
- Passed: `git diff --check`

## Known limits

- LangGraph remains intentionally deferred. This task implements a plain Python pipeline with the same conceptual stages.
- Backend gate is deterministic and conservative; ambiguous or inferred memory should preview or reject rather than silently write.
- No new database schema, Android UI, V2.2 source-evidence search, ContactPoint, CRM, or outreach capability was added.
- `backend/sales_workspace/chat_first.py` is part of the trace/context boundary for this pipeline, but this task did not require schema changes there.

## Recommended next step

Run a real-device LLM smoke if product validation is needed: send a product fact, a correction such as "不找大企业 / 不是 HR / 找老板", and an execution-plan request, then confirm assistant replies are visible and formal workspace cards are not polluted by fallback industries or debug text.
