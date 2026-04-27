# Task: V2.1 Conversational Implementation Queue

状态：done

更新时间：2026-04-27

## Objective

将 V2.1 PRD gap review、conversational completion scope 和 5 个中文验收样例转成后续实现队列。

## Scope

- 创建 V2.1 conversational product experience implementation task placeholders。
- 只开放第一个 backend-first deterministic implementation task。
- 保持 V2.2 evidence/search/contact、真实 LLM、正式 LangGraph、CRM 和 Android 大改 blocked。

## Outcome

Current task:

- `task_v2_1_clarifying_questions_backend_prototype.md`

Planned / blocked follow-ups:

- `task_v2_1_workspace_explanation_backend_prototype.md`
- `task_v2_1_product_profile_extraction_runtime.md`
- `task_v2_1_lead_direction_adjustment_runtime.md`
- `task_v2_1_conversation_acceptance_e2e.md`
- `task_v2_1_android_conversation_polish.md`

## Validation

```bash
rg "task_v2_1_clarifying_questions_backend_prototype.md|planned / blocked|V2.2" docs/delivery/tasks
git diff --check
```
