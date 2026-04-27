# Handoff: V2.1 Lead Direction Adjustment Runtime

日期：2026-04-27

## Summary

Expanded deterministic chat-first lead direction adjustment so Chinese user instructions can update acquisition direction through Draft Review and Kernel writeback.

## Changed

- Added deterministic extraction for priority industries, target customer types, regions, company sizes, priority constraints, excluded industries, and excluded customer types.
- Added source message marker in `change_reason`.
- Added backend test coverage for a Chinese adjustment request: excluding education, prioritizing East China manufacturing SMEs, and requiring ERP / weak scheduling-inventory coordination.

## Validation

```bash
PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
git diff --check
```

Result:

- `13 passed, 1 skipped`
- Postgres-specific chat-first verification skipped because `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` was not set.

## Boundaries

- No search.
- No concrete company candidate generation.
- No ContactPoint.
- No Android changes.
- No direct formal workspace writes by Runtime.

## Next

Proceed to `task_v2_1_conversation_acceptance_e2e.md`.
