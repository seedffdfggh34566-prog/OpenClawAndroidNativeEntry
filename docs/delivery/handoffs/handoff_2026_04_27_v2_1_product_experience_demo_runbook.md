# Handoff: V2.1 Product Experience Demo Runbook

日期：2026-04-27

## 1. Changed

- Added a V2.1 product experience demo runbook.
- Documented Postgres backend startup, migration, chat-first product input, chat-first lead direction input, Draft Review accept/apply, and Android UI demo steps.

## 2. Files

- `docs/how-to/operate/v2-1-product-experience-demo-runbook.md`
- `docs/how-to/README.md`
- `docs/delivery/tasks/task_v2_1_product_experience_demo_runbook.md`

## 3. Validation

Planned validation:

```bash
rg "v2-1-product-experience-demo-runbook.md|ProductProfileRevision|LeadDirectionVersion|ConversationMessage|AgentRun" docs/how-to docs/delivery
git diff --check
```

## 4. Limits

- Runbook only.
- No new product capability, real LLM, search, ContactPoint, CRM, or deployment work.

## 5. Next

Proceed to `task_v2_1_product_experience_closeout.md`.
