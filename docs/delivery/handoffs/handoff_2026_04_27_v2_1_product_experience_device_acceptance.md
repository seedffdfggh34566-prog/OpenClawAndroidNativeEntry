# Handoff: V2.1 Product Experience Device Acceptance

日期：2026-04-27

## Summary

Completed real-device acceptance for the V2.1 Android product experience prototype on device `f3b59f04`.
The core flow was validated from an empty workspace and the final workspace state was also rechecked with the backend running in Postgres Sales Workspace store mode.

## Changed Files

- `docs/delivery/tasks/task_v2_1_product_experience_device_acceptance.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_1_product_experience_device_acceptance.md`
- `docs/delivery/evidence/v2_1_product_experience_device_acceptance/*.png`

## Evidence

- Empty workspace loaded at version 0.
- Clarifying question turn returned 5 Chinese follow-up questions and did not write workspace state.
- Product turn created `draft_review_sales_turn_product_profile_update_v1`; accept/apply wrote `ProductProfileRevision:ppr_chat_v1`.
- Direction turn created `draft_review_sales_turn_lead_direction_update_v2`; accept/apply wrote `LeadDirectionVersion:dir_chat_v2`.
- Workspace version advanced `0 -> 1 -> 2`.
- Android showed active direction with manufacturing, East China, SME, education exclusion, and ERP constraint.
- ContextPack `ctx_ws_demo_v2` and Markdown projection files were visible.
- Workspace explanation answer referenced the current product profile, lead direction, workspace version, and ContextPack source versions.
- Postgres store backend recheck showed the persisted version 2 workspace remains readable by Android.

## Validation

```bash
PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
# 18 passed, 1 skipped

PYTHONPATH=$PWD backend/.venv/bin/alembic -c alembic.ini upgrade head

docker compose -f compose.postgres.yml up -d
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev PYTHONPATH=$PWD backend/.venv/bin/alembic -c alembic.ini upgrade head
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND=postgres PYTHONPATH=$PWD backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013

curl http://127.0.0.1:8013/health
# {"status":"ok"}

adb devices
# f3b59f04 device

adb reverse tcp:8013 tcp:8013
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.openclaw.android.nativeentry/.MainActivity
```

Backend confirmation:

```bash
curl http://127.0.0.1:8013/sales-workspaces/ws_demo
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/context-packs -H 'Content-Type: application/json' -d '{}'
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/projection
```

## Known Limitations

- This validates deterministic V2.1 product experience prototype behavior.
- It does not validate real LLM, formal LangGraph, V2.2 search, ContactPoint, CRM, production deployment, auth, or multi-user behavior.
- Android still relies on an existing backend workspace; automatic workspace creation remains out of scope.

## Recommended Next Step

Run the final PRD Acceptance Traceability review and, if it matches this evidence, close V2.1 product experience prototype with V2.2 implementation still blocked.
