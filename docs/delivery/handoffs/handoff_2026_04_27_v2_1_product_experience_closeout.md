# Handoff: V2.1 Product Experience Closeout

日期：2026-04-27

## 1. Changed

- Closed out V2.1 product experience prototype.
- Updated entry docs to stop saying V2.1 product experience is incomplete.
- Kept `_active.md` at no automatically queued implementation task.
- Kept V2.2 evidence/search/contact implementation blocked.

## 2. Files

- `README.md`
- `docs/README.md`
- `docs/delivery/README.md`
- `docs/delivery/tasks/_active.md`
- `docs/product/overview.md`
- `docs/product/roadmap.md`
- `docs/delivery/tasks/task_v2_1_product_experience_closeout.md`

## 3. Validation

Passed / planned final closeout validation:

```bash
rg "V2.1 product experience prototype completed|task_v2_1_product_experience_closeout.md|V2.2.*blocked" README.md docs
git diff --check
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/alembic -c alembic.ini upgrade head
OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v21_final.sqlite backend/.venv/bin/alembic -c alembic.ini upgrade head
backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py backend/tests/test_sales_workspace_draft_reviews_api.py backend/tests/test_sales_workspace_chat_first_api.py -q
OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_repository.py backend/tests/test_sales_workspace_api_postgres_store.py backend/tests/test_sales_workspace_draft_reviews_postgres_store.py backend/tests/test_sales_workspace_chat_first_api.py -q
backend/.venv/bin/python -m pytest backend/tests -q
./gradlew :app:assembleDebug
./gradlew :app:lintDebug
```

Backend smoke passed against local Postgres backend:

```text
health: {"status":"ok"}
workspace_id: ws_v21_smoke
product_draft_review: draft_review_sales_turn_product_profile_update_v1
direction_draft_review: draft_review_sales_turn_lead_direction_update_v2
final_workspace_version: 2
```

## 4. Limits

- Closeout / docs only.
- No V2.2 implementation, real LLM, search provider, ContactPoint, CRM, formal LangGraph, Android review history, or DB hardening.

## 5. Next

Recommended next planning task: V2.2 evidence/search/contact boundary design. It should be docs-only first.
