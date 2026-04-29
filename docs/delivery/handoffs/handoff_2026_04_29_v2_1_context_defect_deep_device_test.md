# Handoff: V2.1 Sales Workspace context defect deep device test

Date: 2026-04-29

## Summary

This was a test-and-record pass only. No product code was changed.

The test ran 3 distinct user styles, 12 Sales Agent turns each, against a real LLM backend with JSON store and diagnostics enabled. The main finding is that the recent memory/autowrite fix improved persistence, but the context system is still not good enough because formal workspace cards are now too easily polluted by low-quality fallback content and append-only merge behavior.

Evidence root:

- `/tmp/openclaw_context_defect_device_tests/summary.json`
- `/tmp/openclaw_context_defect_device_tests/ws_ctx_01_impatient_sales_agent/`
- `/tmp/openclaw_context_defect_device_tests/ws_ctx_02_corrective_training/`
- `/tmp/openclaw_context_defect_device_tests/ws_ctx_03_structured_saas/`

Backend environment used:

- real LLM runtime: `OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=llm`
- prompt version: `sales_agent_turn_llm_v1`
- JSON store: `/tmp/openclaw_context_defect_device_tests/store`
- diagnostics enabled: `/dev/sales-workspaces/{workspace_id}/diagnostics`

Device evidence:

- Device detected: `f3b59f04`
- APK installed and launched.
- `adb reverse tcp:8013 tcp:8013` configured.
- Screenshots captured under each case directory, including `round_01.png`, `round_03.png`, `round_06.png`, `round_09.png`, `round_12.png`.
- Additional final workspace screenshots: `final_android_workspace.png`.

## Case Results

### Case 1: impatient early founder

Workspace: `ws_ctx_01_impatient_sales_agent`  
Main thread: `拓客AI第一批客户`  
Secondary thread: `价格影响`

| Round | Mode | Version | Result summary | Context observation |
| --- | --- | ---: | --- | --- |
| 1 | 产品理解 | 1 | Product profile created for 拓客AI, 1-20 person老板, auto-written. | First-turn ContextPack correctly had no prior product baseline; script heuristic marked this as P1, but this is not a real defect. |
| 2 | 找客户建议 | 2 | Gave target customer suggestions instead of only asking questions. | Product baseline was referenced. |
| 3 | 找客户建议 | 3 | Suggested lawyers/accounting/dental as first batch. | Useful, but starts narrowing direction aggressively. |
| 4 | 找客户建议 | 4 | Gave first-week daily actions. | Direction enriched. |
| 5 | 产品理解 | 5 | Added price 3000-8000 and features. | Product card preserved earlier positioning and added features. |
| 6 | 找客户建议 | 6 | Correctly accepted “no telemarketing”. | Direction added no-phone-sales constraint. |
| 7 | 找客户建议 | 7 | Listed excluded directions. | Exclusion memory persisted. |
| 8 | 解释当前判断 | 7 | Read-only answer; version unchanged. | Correct non-mutating behavior. |
| 9 | 解释当前判断 | 7 | Summarized remembered product/direction accurately. | No obvious thread pollution. |
| 10 | 找客户建议 | 8 | Gave next-day execution path. | Direction updated again. |
| 11 | 价格线程解释 | 8 | Discussed 399/month pricing in secondary thread. | Read-only; did not write pricing into formal card. |
| 12 | 主线程解释 | 8 | Returned main product/direction without price-thread pollution. | Thread boundary looked correct. |

Final formal state:

- Product card is mostly correct: product name, one-liner, target customer, price/features are preserved.
- Lead direction is usable but noisy: it accumulated duplicate and fallback-style items such as `B2B 服务商` / `B2B服务商`, and generic fallback industries.

### Case 2: corrective traditional service owner

Workspace: `ws_ctx_02_corrective_training`  
Main thread: `本地培训获客修正`  
Secondary thread: `异地扩张`

| Round | Mode | Version | Result summary | Context observation |
| --- | --- | ---: | --- | --- |
| 1 | 产品理解 | 1 | Created local sales-management training product card. | First-turn no prior baseline is expected. |
| 2 | 产品理解 | 2 | Added Suzhou / 50km / 2-5万. | Product constraints captured. |
| 3 | 找客户建议 | 3 | Initially recommended larger enterprise sales teams. | Not necessarily wrong before correction, but set up later contradiction. |
| 4 | 找客户建议 | 4 | User corrected: no large enterprise / no bidding. | New direction appended but old large-enterprise items remained. |
| 5 | 找客户建议 | 5 | User corrected: not HR, find owner. | New老板 preference appended but old培训负责人 / HR-adjacent targets remained. |
| 6 | 找客户建议 | 6 | Suggested channels to find owners. | Useful output. |
| 7 | 产品理解 | 7 | User said referrals limited, wants new customers. | Product one-liner degraded to this supplemental note. |
| 8 | 找客户建议 | 8 | Consolidated corrections. | Still mixed with old direction entries. |
| 9 | 解释当前判断 | 8 | Correctly explained Suzhou/local/owner. | Answer quality good despite polluted formal direction. |
| 10 | 找客户建议 | 9 | Listed customers not to find. | Direction now includes exclusions, but still contains previous contradictory positive targets. |
| 11 | 异地线程解释 | 9 | Discussed Shanghai expansion. | Read-only thread did not mutate formal workspace. |
| 12 | 主线程解释 | 9 | Remembered local constraints, price, no large enterprises. | User-facing answer was good; formal card still polluted. |

Final formal state defects:

- Product one-liner became `补充：老客户转介绍有限，主要想拓新客户。`, replacing the real product positioning. This is a P1 memory degradation.
- Lead direction still contains earlier positive targets like `年营收亿元以上的企业`, `销售团队20人以上`, and training负责人 variants even after the user corrected against large enterprises and HR.

### Case 3: analytical SaaS founder

Workspace: `ws_ctx_03_structured_saas`  
Thread: `财税SaaS客户分层`

| Round | Mode | Version | Result summary | Context observation |
| --- | --- | ---: | --- | --- |
| 1 | 产品+找客户 | 1 | Product and lead direction both created. | Auto-write worked. |
| 2 | 解释当前判断 | 1 | Confirmed both product and direction existed. | Read-only, version unchanged. |
| 3 | 找客户建议 | 2 | Gave customer tiers. | Direction enriched. |
| 4 | 找客户建议 | 3 | Compared老板/财务负责人/代账公司. | Useful. |
| 5 | 找客户建议 | 4 | Gave screening signals. | Useful. |
| 6 | 产品理解 | 5 | Added “no bank flow integration, invoice/manual only”. | Constraint captured. |
| 7 | 产品理解 | 6 | Preserved cashflow/tax risk positioning while updating constraints. | Good product merge behavior. |
| 8 | 解释当前判断 | 6 | Explained why not large ERP customers. | Good answer and read-only. |
| 9 | 找客户建议 | 7 | Asked for target list/contact/channel before giving first-week script. | P2 answer-quality defect: user requested execution plan, but assistant reverted to prerequisites. |
| 10 | 解释当前判断 | 7 | Explained from formal cards. | Mostly good. |
| 11 | 解释当前判断 | 7 | Product positioning answer was accurate. | Good. |
| 12 | 解释当前判断 | 7 | Claimed ContextPack and formal cards are completely consistent. | P2: the claim is too strong; formal direction is polluted by generic fallback entries. |

Final formal state defects:

- Product card is strong and preserved the bank-flow limitation correctly.
- Lead direction contains generic fallback pollution: `本地生活服务`, `B2B 服务商`, `小型制造或贸易公司`, `1-20 人小企业老板`, which do not match the 20-200 person财税 SaaS context.
- `change_reason` contains developer/runtime phrasing: `LLM output omitted lead direction operation; backend kept a reviewable customer-finding draft...`

## Defects

| ID | Severity | Evidence | Expected | Actual | Likely root cause |
| --- | --- | --- | --- | --- | --- |
| CTX-001 | P1 | Case 2 final product card | Supplemental product info should enrich constraints/value props without replacing the product one-liner. | Product one-liner became `补充：老客户转介绍有限，主要想拓新客户。` | Merge guard is too shallow for scalar fields; it cannot distinguish “new fact” from “replacement summary”. |
| CTX-002 | P1 | Case 2 final direction | User corrections should retire or mark contradicted old targets. | Direction still includes large-enterprise and HR/training负责人-style targets after corrections. | Append-only list merge has no replace/remove/contradiction model. |
| CTX-003 | P1 | Case 1 and Case 3 final direction cards | Backend fallback should be neutral and derived from user facts. | Generic fallback industries and customer types were written into formal lead direction. | `_fallback_direction_operation` is too opinionated and auto-write turns fallback guesses into formal memory. |
| CTX-004 | P1 | Case 3 final direction `change_reason` | Formal business card should not contain runtime/debug wording. | `LLM output omitted... backend kept...` entered formal direction. | Fallback/debug reason is stored as formal `change_reason`. |
| CTX-005 | P1 | Case 3 round 9 | “Give me first-week script” should produce an execution plan or remain read-only. | Assistant mostly asked for prerequisites and still auto-wrote a draft. | Auto-write has no quality gate; lead fallback can mutate even when response quality is weak. |
| CTX-006 | P2 | Case 1 final direction | Direction lists should be normalized and deduplicated. | Duplicates/variants such as `B2B 服务商` and `B2B服务商`, `1-20 人` and `1-20人` accumulated. | List merge lacks normalization/canonicalization. |
| CTX-007 | P2 | Case 3 round 12 | If asked to check consistency, assistant should not overclaim if formal card contains fallback noise. | It claimed ContextPack and formal cards were completely consistent. | LLM has no diagnostics comparison tool and no rule to report uncertainty. |
| UI-001 | P3 | `/tmp/openclaw_context_defect_device_tests/ws_ctx_*/final_android_workspace.png` | Dev workspace selector should reliably switch to target test workspace for device evidence. | Attempts to switch via adb were unreliable; screenshots remained on the current app workspace/thread view. | Android dev/test selector is usable manually but brittle under adb automation; screenshot evidence is real-device but not always case-specific. |

## Context System Analysis

The current biggest problem is no longer “ContextPack is too thin” in the narrow sense. The latest ContextPack usually contains the current formal product and lead direction after the first turn. The deeper issue is that the formal cards themselves are being polluted, and once polluted they become the next turn’s context baseline.

Specific architecture weaknesses:

1. Formal memory has only append/replace primitives, not correction semantics.
   - When a user says “不是 HR，是老板本人”, the system appends老板本人 but does not retire HR/training负责人.
   - When a user says “不找大企业”, old large-enterprise targets remain in positive target lists.

2. Auto-write lacks quality thresholds.
   - A weak answer or fallback operation can become formal memory immediately.
   - The system needs a distinction between “safe factual enrichment” and “speculative direction guess”.

3. Fallback operations are too product-opinionated.
   - Generic fallback lead directions are useful for demos but harmful as formal memory.
   - Fallbacks should either be neutral pending constraints or not auto-write.

4. Scalar merge is unsafe.
   - Product one-liner is treated as replaceable by any later product update.
   - The system needs field-level source intent: correction, enrichment, constraint, or replacement.

5. Diagnostics and runtime answer are disconnected.
   - The assistant can claim consistency even when diagnostics show formal card pollution.
   - A future diagnostics-aware consistency check should be deterministic, not LLM-only.

## Recommended Next Fix Plan

Do not just increase recent message count again. The next bugfix should focus on memory semantics:

1. Add patch operation intent or backend-inferred intent:
   - `enrich`, `correct`, `replace`, `exclude`, `constraint_only`.
2. Add contradiction handling for direction lists:
   - explicit corrections move old values to `excluded_*` or remove them from positive lists.
3. Make fallback operations non-mutating by default:
   - fallback may answer the user, but should not auto-write unless derived from concrete user facts.
4. Add safe scalar merge rules:
   - `one_liner` and `product_name` should only replace existing values on explicit correction.
   - supplemental notes should go to constraints or value props.
5. Add an auto-write quality gate:
   - do not apply if output mostly asks prerequisites, contains generic fallback defaults, or has internal/runtime reason text.
6. Add deterministic diagnostics assertions:
   - context pack current card must equal current formal card at source version.
   - no generic fallback defaults in formal cards unless user stated them.
   - no internal runtime phrases in formal business fields.

## Validation

- `curl http://127.0.0.1:8013/health`: passed.
- `adb devices`: detected `f3b59f04`.
- `adb reverse tcp:8013 tcp:8013`: passed.
- `adb install -r app/build/outputs/apk/debug/app-debug.apk`: passed.
- `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity`: passed.
- 36 Sales Agent turns executed with real LLM.
- 3 final diagnostics snapshots saved.
- 15 round screenshots plus 3 final Android screenshots saved under `/tmp/openclaw_context_defect_device_tests`.

## Known Limits

- The dialogue turns were driven through backend chat-first endpoints while the Android app was installed, launched, and screenshot on device. This gave reliable conversation/diagnostics evidence, but not every user message was typed through the Android composer.
- Android workspace selector screenshots were unreliable under adb automation; manual use may still work.
- No code fixes were made in this task by design.
- This evidence does not claim V2.1 completion.
