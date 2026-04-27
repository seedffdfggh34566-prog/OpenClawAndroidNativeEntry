# Handoff: V2.1 Product Profile Extraction Runtime

日期：2026-04-27

## Summary

Expanded deterministic chat-first product profile extraction from the single FactoryOps path to the 5 Chinese V2.1 acceptance samples.

## Changed

- Added deterministic product profile payload selection for:
  - industrial equipment maintenance software
  - local enterprise training service
  - SME finance/tax SaaS
  - industrial park leasing /招商运营 service
  - manufacturing outsourcing / assembly service
- Preserved Draft Review and Kernel writeback boundary.
- Added parameterized backend tests for all 5 samples.

## Validation

```bash
PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
git diff --check
```

Result:

- `12 passed, 1 skipped`
- Postgres-specific chat-first verification skipped because `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` was not set.

## Boundaries

- No real LLM.
- No LangGraph.
- No V2.2 search / ContactPoint / CRM.
- No Android changes.
- No direct formal workspace writes by Runtime.

## Next

Proceed to `task_v2_1_lead_direction_adjustment_runtime.md`.
