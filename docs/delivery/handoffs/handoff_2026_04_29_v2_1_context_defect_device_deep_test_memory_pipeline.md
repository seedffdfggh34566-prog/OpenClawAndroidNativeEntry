# Handoff: V2.1 context defect device deep test after memory pipeline

Date: 2026-04-29

## Purpose

This report records a real-device deep test focused on LLM context defects after the V2.1 memory decision pipeline implementation.

The goal was not to prove the happy path. The goal was to stress the context system with realistic repeated dialogue and identify why the current context engineering still feels unreliable.

## Environment

- Branch: `codex/v2-1-memory-decision-pipeline`
- Commit under test: `5022e5d feat: add sales workspace memory decision pipeline`
- Device: `adb devices` detected `f3b59f04`
- Android app: debug APK built, installed, and launched
- Backend: temporary local backend on `127.0.0.1:8013`
- Device bridge: `adb reverse tcp:8013 tcp:8013`
- Runtime mode: real LLM (`OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=llm`)
- LLM model setting: `minimax-m2.5`
- Store: temporary SQLite + JSON store under `/tmp/openclaw_context_defect_device/`
- Secrets: `backend/.env` was only checked for presence / git-ignore status; contents were not printed or summarized.

Evidence files:

- Raw structured run results: `/tmp/openclaw_context_defect_device/context_defect_run_results.json`
- LLM traces: `/tmp/openclaw_context_defect_device/traces/` (`24` trace files)
- Device screenshot: `/tmp/openclaw_context_defect_device/android_workspace_screen.png`

## Device Flow Note

The Android app was installed and launched successfully, and the backend bridge was active. The visible Sales Workspace page loaded.

However, direct `adb input` / AdbKeyboard text injection did not focus the Compose chat input on this device. Because this test was focused on LLM context defects rather than Android input mechanics, the 24 Sales Agent turns were executed through the same backend API used by the device session, then verified through backend state and traces. This is a device-connected backend/runtime test, not a claim that all 24 messages were typed through the UI.

This input-focus issue is itself worth a separate Android testability follow-up, but it is not the core context defect reported here.

## Test Design

Two different user styles were used.

### Persona A: structured B2B founder

Style: structured, step-by-step, repeatedly correcting product and lead assumptions.

Workspace: `ws_ctx_structured_device`

Turns:

| # | message type | user intent |
|---|---|---|
| 1 | `product_profile_update` | define factory equipment inspection / maintenance SaaS |
| 2 | `product_profile_update` | add constraint: old-customer referral is limited |
| 3 | `lead_direction_update` | target Yangtze River Delta 50-300 person discrete manufacturers; exclude large groups and state-owned companies |
| 4 | `lead_direction_update` | correct decision maker: not procurement / HR; target production lead or owner |
| 5 | `workspace_question` | ask what is actually remembered |
| 6 | `lead_direction_update` | refine owner vs production-lead priority; exclude listed companies |
| 7 | `product_profile_update` | add price and data import constraints |
| 8 | `lead_direction_update` | explicitly reject fallback sectors like local services / B2B service providers |
| 9 | `lead_direction_update` | ask for first-week execution plan without changing formal profile |
| 10 | `product_profile_update` | correct: not hardware, not outsourced maintenance; software system |
| 11 | `workspace_question` | ask current customer profile and conflicts |
| 12 | `mixed_product_and_direction_update` | final narrowed target and product name |

### Persona B: messy small-team owner

Style: casual, vague, jumps between ideas, then corrects earlier statements.

Workspace: `ws_ctx_messy_device`

Turns:

| # | message type | user intent |
|---|---|---|
| 1 | `product_profile_update` | vague AI for small-company owners to find customers |
| 2 | `lead_direction_update` | target small businesses where owner manages sales |
| 3 | `product_profile_update` | correct: not CRM; organize leads and remind follow-up |
| 4 | `lead_direction_update` | exclude real estate and education/training |
| 5 | `workspace_question` | ask why those customers were suggested |
| 6 | `lead_direction_update` | switch to Shenzhen cross-border e-commerce sellers |
| 7 | `product_profile_update` | add price and target user: owner, not sales team |
| 8 | `lead_direction_update` | correct role: not HR / marketing director; owner or partner |
| 9 | `lead_direction_update` | ask tomorrow's search plan without saving keywords |
| 10 | `lead_direction_update` | reject B2B service provider as formal industry |
| 11 | `product_profile_update` | add core pain point: scattered leads in WeChat / Excel / forms |
| 12 | `workspace_question` | ask final remembered product and customer memory |

## High-Level Result

| Persona | real LLM turns | auto apply | review required | reject | read-only workspace questions | final workspace version | final product | final lead direction |
|---|---:|---:|---:|---:|---:|---:|---|---|
| Structured B2B founder | 12 | 1 | 1 | 8 | 2 | 1 | partial / malformed | missing |
| Messy small-team owner | 12 | 2 | 1 | 7 | 2 | 2 | partial / malformed | missing |

The strongest finding: after 24 turns, **no formal lead direction existed in either workspace**.

This is not a minor answer quality issue. It means the Product Sales Agent can spend many turns discussing target customers while the formal Sales Workspace Kernel still has no lead-direction object.

## Observed Defects

### 1. MemoryEvaluator field names drift away from backend schema

The MemoryEvaluator often emitted plausible but non-canonical fields:

- `industry_served`
- `target_user_roles`
- `core_value_proposition`
- `product_category`
- `target_region`
- `company_size`
- `industry_focus`
- `excluded_account_types`
- `target_decision_maker`
- `exclude_buyer_persona`
- `target_roles`
- `product_type`
- `pricing`
- `functional_requirements`

The backend gate only knows formal fields such as:

- product: `product_name`, `one_liner`, `target_customers`, `target_industries`, `pain_points`, `value_props`, `constraints`
- lead direction: `priority_industries`, `target_customer_types`, `regions`, `company_sizes`, `priority_constraints`, `excluded_industries`, `excluded_customer_types`

Because there is no alias mapping or strict evaluator schema, many valid user facts are silently discarded and then rejected as `empty_product_profile_update` or `empty_lead_direction_update`.

Concrete examples:

- Structured turn 3: user clearly said "长三角 50-300 人的离散制造厂，不要大集团，也不要国企"; evaluator emitted `target_region`, `company_size`, `industry_focus`, `excluded_account_types`; backend rejected with `empty_lead_direction_update`.
- Structured turn 4: user clearly corrected buyer roles; evaluator emitted `target_decision_maker` and `exclude_buyer_persona`; backend rejected with `empty_lead_direction_update`.
- Messy turn 6: user clearly targeted "深圳跨境电商卖家，5-30 人团队"; evaluator emitted `target_customers`, `target_industries`, `target_regions`, `pain_points`; backend rejected with `empty_lead_direction_update`.

Root cause: the evaluator is free-form even though the gate is schema-specific.

### 2. The gate is conservative, but not productively deterministic

The deterministic gate currently blocks many writes, but it does not give the runtime a repair path.

Examples:

- Unsupported but semantically obvious fields are discarded instead of translated or sent through a structured repair prompt.
- `empty_*_update` tells us the gate rejected the result, but does not preserve enough user-supported facts for the next turn.
- The result is "safe" in the narrow sense that bad data does not write, but product quality suffers because good data also does not write.

This is why "backend deterministic gate" must not just be a reject filter. It also needs canonicalization, alias translation, and actionable rejection semantics.

### 3. `risk_flags` are untyped and cause good first-turn facts to miss auto-apply

Structured turn 1 was a clear product fact:

> 工厂设备点检和维保 SaaS，帮离散制造厂减少停机时间，主要给生产负责人和老板看。

The evaluator produced a product proposal, but added risk flags like "产品阶段不明确" and "目标客户规模未明确". Backend downgraded it to `review_required`, so no formal product profile was applied.

This is the wrong semantics. Missing secondary details should become `missing_fields` or `constraints`, not a write-blocking risk for the facts that are already explicit.

Root cause: `risk_flags` mixes "unsafe to write" with "profile still incomplete".

### 4. Review-required drafts do not help the next context turn

In both personas, turn 1 generated a previewed product profile draft, but because it was not applied, the formal workspace stayed at version 0.

Effects:

- Later turns had no formal product baseline.
- ContextPack could include conversation history, but `current_product_profile_revision` remained absent.
- The user had no effective chat-first path to apply the review-required draft.

This creates a context dead zone: the system produces a "maybe memory" object, but the next LLM turn cannot rely on it as formal memory.

### 5. Assistant language and formal memory diverge

The first LLM response often says things like "已确认", "我理解", or "这个我记下了", even when the backend gate later rejects the memory proposal.

Examples:

- Structured turn 11 answered with "当前已确认的客户画像", but formal workspace had no lead direction.
- Messy turn 10 said "这个我记下了" about not writing B2B service providers as industry, but backend gate rejected the turn and formal lead direction was still absent.

The current sanitizer only catches explicit phrases such as "沉淀到工作区" / "写入工作区". It does not catch softer but still misleading phrases such as "我记下了" or "已确认".

Root cause: response generation happens before memory gating, and the final assistant message is not reconciled with gate outcome.

### 6. Conversation memory and formal workspace memory are becoming two truths

The assistant can use previous conversation text to produce coherent answers, but the formal workspace does not reflect those facts.

This creates contradictory behavior:

- Workspace question can truthfully say "formal workspace has no saved lead direction".
- Later answers still talk as if a detailed customer profile is confirmed, because the transcript includes earlier turns.

The product then feels context-aware in language but context-unsafe in state. This is worse than a simple memory miss because it erodes user trust: the system seems to remember, but the durable workspace does not.

### 7. Lead direction is effectively impossible to persist in realistic dialogue

Across 18 lead-direction turns in the two personas, the final formal lead direction was missing in both workspaces.

Lead direction failed for multiple reasons:

- evaluator field aliases did not match backend schema;
- source evidence sometimes included previous messages and assistant messages;
- execution-plan turns correctly rejected, but no stable prior lead direction existed to protect;
- corrections used fields such as `target_roles` instead of `target_customer_types`.

This means the current V2.1 memory pipeline is much better at not polluting lead direction than at creating or correcting lead direction.

### 8. Current-message-only evidence is too strict for multi-turn corrections

Structured turn 6 referenced multiple prior user facts. The evaluator included source evidence from turns 3, 4, and 6. Backend rejected the whole proposal with `source_evidence_wrong_message`.

The current rule "source evidence must come from this turn's user message" is safe for single-turn writeback but weak for real conversation. Corrections often depend on prior facts:

- "不是 HR，是老板" depends on knowing HR was previously considered.
- "不要把 B2B 服务商写进去" depends on a previous assistant suggestion.
- "最终先验证苏州和无锡..." supersedes a prior broader region.

The gate needs per-field provenance that can reference current user text and previous user text from the context pack, while still rejecting assistant-only inference as formal user fact.

### 9. Product profile writes are partial and sometimes malformed

Final structured workspace product:

- `product_name`: `待确认产品或服务`
- `one_liner`: "客单价大概 3-8 万一年，需要能导入微信和 Excel 里的维修记录。"
- lists mostly empty

Final messy workspace product:

- `product_name`: `待确认产品或服务`
- `one_liner`: "不是 CRM，别记成 CRM，是把销售线索整理起来，提醒我跟进。"
- `pain_points`: one later pain point
- target customers / industries empty

The system preserved safety but failed to build a usable product card. The product card is not a durable summary of the conversation; it is a fragment from whichever turn happened to pass the gate.

### 10. Two LLM calls per turn create mobile-facing latency

Observed trace durations for selected turns:

- Structured turn 1: about 31 seconds.
- Structured turn 3: about 56 seconds.
- Structured turn 7: about 35 seconds.
- Messy turn 2: about 34 seconds.

This latency is noticeable on a real device. It may be acceptable for deep reasoning, but not for every chat turn if the app should feel responsive.

The pipeline needs a policy for when to skip MemoryEvaluator, run it asynchronously, or use a lighter model / deterministic extractor for low-risk turns.

## Why Context Engineering Feels Unsatisfactory

The core issue is not only model intelligence.

The system currently has four poorly aligned layers:

1. **Response LLM** speaks as if it has conversation memory.
2. **MemoryEvaluator LLM** proposes memory with flexible, non-canonical fields.
3. **Backend gate** expects strict formal fields and current-turn evidence.
4. **Formal workspace** only changes after accepted `WorkspacePatchDraft`.

Because the layers disagree, the user experiences inconsistent memory:

- the assistant appears to understand;
- the evaluator proposes something adjacent but not schema-valid;
- the gate rejects it;
- formal workspace remains stale;
- next assistant turn relies on transcript instead of durable memory;
- user sees "context" in language but not in product state.

This is why the current system feels worse than expected despite adding a MemoryEvaluator. The pipeline added safety but did not yet add a reliable semantic bridge between dialogue and durable workspace objects.

## Recommendations

### P0: constrain MemoryEvaluator output to backend field enums

Do not let MemoryEvaluator invent field names.

Recommended change:

- define per-object field enums in `MemoryProposal`;
- reject evaluator JSON with unsupported fields at parse time;
- retry once with a schema repair prompt;
- add tests for common aliases.

### P0: add a canonicalization / alias layer before gate

Map common evaluator/user concepts into formal fields:

- `target_region`, `target_regions`, `region` -> `regions`
- `company_size`, `target_scale` -> `company_sizes`
- `industry_focus`, `industry`, `target_industries` -> `priority_industries` or product `target_industries` depending object type
- `target_decision_maker`, `target_roles`, `buyer_persona` -> `target_customer_types`
- `excluded_account_types`, `exclude_buyer_persona` -> `excluded_customer_types`
- `pricing`, `price` -> product `constraints` until a formal price field exists
- `product_type`, `product_category` -> product `constraints` or a future formal field
- `functional_requirements` -> product `value_props` or `constraints`

Without this, the gate will remain safe but mostly non-functional.

### P0: separate write-blocking risk from missing-info advisory

Use separate fields:

- `write_risk_flags`: conflict, assistant-only inference, unsupported source, privacy risk, fallback/default/debug phrase.
- `missing_fields`: profile incompleteness that should not block explicit facts.

Clear product facts should auto-apply even if product stage, target scale, or deployment detail is missing.

### P0: allow previous user evidence with explicit provenance rules

Current-turn-only evidence is too strict.

Recommended rule:

- auto-apply may use current user message evidence;
- corrections may reference previous user message IDs from the same thread if those messages are present in ContextPack;
- assistant message evidence can support "assistant suggested this before", but cannot become a user fact;
- each field update should carry its own source evidence.

### P0: reconcile final assistant copy after gate outcome

After memory gate:

- if `auto_apply`: assistant may say saved / updated.
- if `review_required`: assistant must say proposed for review, not remembered.
- if `reject`: assistant must avoid "记下了", "已确认", "当前已确认画像" unless referring explicitly to conversation-only understanding.

This likely needs a final deterministic copy filter or a short post-gate response rewrite step.

### P1: make review-required drafts useful in the chat flow

If turn 1 creates a review-required product draft, the next turn should not behave as if nothing exists.

Options:

- surface review/apply in Android main chat;
- allow a "pending memory" context section clearly labeled as not formal;
- auto-apply partial fields that pass the gate while reviewing only risky fields;
- split one proposal into accepted field updates and review-only field updates.

### P1: add device-derived regression tests

Add backend tests for the observed real-device failures:

- product fact with extra missing fields still auto-applies canonical product fields;
- "长三角 50-300 人离散制造厂，不要大集团/国企" creates lead direction;
- "不是 HR，是老板/生产负责人" maps to target/excluded customer types;
- "不要把 B2B 服务商写进方向" adds exclusion or cleanup;
- mixed final product + direction update maps both product and lead direction.

### P1: reconsider when the second LLM call runs

The two-call runtime is useful for safety, but expensive.

Possible policy:

- run MemoryEvaluator only for message types that may mutate workspace;
- skip it for pure execution-plan requests unless the user explicitly says "记住/改成/不要再";
- use a smaller/faster model or deterministic extractor for obvious field updates;
- consider async memory evaluation when immediate UX matters.

### P2: LangGraph can help orchestration, but it is not the missing core

This test does not prove that LangGraph is required.

LangGraph could help if it enforces:

- typed node boundaries;
- repair loops for invalid MemoryDecision output;
- explicit state transitions for response, evaluation, gate, review, and apply;
- observability of where memory failed.

But simply moving the current logic into LangGraph would not fix the root issues. The root issues are schema alignment, provenance, field-level partial acceptance, and post-gate assistant copy reconciliation.

## Suggested Next Implementation Task

Create a focused task:

`V2.1 Sales Workspace MemoryDecision schema canonicalization and field-level gate repair`

Scope:

- strict MemoryEvaluator field enums;
- alias/canonicalization map;
- field-level accepted/review/rejected split;
- previous-user source evidence support;
- post-gate assistant copy reconciliation;
- regression tests based on this device report.

Do not introduce LangGraph until this deterministic semantic bridge is stable.

## Validation Summary

- Android build: passed.
- Device detected: passed.
- App installed/launched: passed.
- Backend health: passed.
- `adb reverse`: passed.
- Real LLM turns: completed 24 / 24.
- LLM traces captured: 24.
- Android logcat: no relevant OpenClaw fatal crash found in the captured tail; unrelated vendor camera log noise appeared.

## Known Limits

- The 24 turns were sent through backend API because direct adb text injection did not focus the Compose input field on this device.
- This report did not run Android connected tests.
- This report did not read or print LLM secrets.
- This report did not modify backend or Android implementation.
