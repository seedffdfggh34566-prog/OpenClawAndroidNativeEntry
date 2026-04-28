# V2.1 Milestone Acceptance Review

更新时间：2026-04-28

## 1. Review Target

- Milestone：V2.1 Sales Workspace Kernel / Chat-first Product Experience
- Review owner：Project Status / Planning Agent
- Review type：docs-only evidence review
- Authorization source：human instruction on 2026-04-28: "PLEASE IMPLEMENT THIS PLAN"

本 review 用于判断 V2.1 是否已经实现。它不开放 V2.2 implementation，不替代 PRD、roadmap、ADR 或 architecture baseline。

---

## 2. Acceptance Sources

| Source | Scope | Notes |
|---|---|---|
| `docs/product/prd/ai_sales_assistant_v2_prd.md` | V2.1 success criteria、in/out of scope、truth-layer rules | Primary PRD source. |
| `docs/product/roadmap.md` | Phase status and V2.1 / V2.2 boundaries | Distinguishes validated prototype path from product milestone. |
| `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md` | Workspace-native sales agent and kernel/runtime boundary | Defines V2.1 object and runtime boundaries. |
| `docs/architecture/workspace/sales-workspace-kernel.md` | Kernel, patch gate, projection, ContextPack | Architecture acceptance source. |
| `docs/architecture/runtime/v2-1-chat-first-runtime-design.md` | ConversationMessage -> AgentRun -> ContextPack -> Draft Review path | Chat-first runtime acceptance source. |
| `docs/architecture/runtime/v2-1-llm-runtime-boundary.md` | Explicit-flag LLM runtime boundary | LLM prototype acceptance source. |

---

## 3. Implementation Evidence Inspected

| Area | Files / directories inspected | Notes |
|---|---|---|
| Backend | `backend/api/sales_workspace.py`, `backend/sales_workspace/*` | Chat-first route, Draft Review, patches, projection, ContextPack, stores. |
| Android | `app/src/main/java/com/openclaw/android/nativeentry/ui/workspace/SalesWorkspaceScreen.kt`, backend client/model/parser files | Workspace UI, create workspace button, chat submit, message history. |
| Runtime | `backend/runtime/sales_workspace_chat_turn_llm.py`, `backend/runtime/llm_client.py` | Explicit-flag Tencent TokenHub prototype path. |
| Persistence / migration | `backend/alembic/versions/20260427_0002_sales_workspace_persistence.py`, `20260427_0003_chat_first_trace_persistence.py`, `backend/sales_workspace/repository.py` | Postgres / Alembic persistence and trace path. |
| API / contract | `docs/reference/api/sales-workspace-chat-first-runtime-contract.md`, `docs/reference/api/sales-workspace-draft-review-contract.md` | Contract evidence used for traceability. |

---

## 4. Validation Evidence

| Validation | Command or evidence source | Result | Notes |
|---|---|---|---|
| Backend targeted tests | `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py backend/tests/test_sales_workspace_chat_first_llm_runtime.py backend/tests/test_sales_workspace_draft_reviews_api.py -q` | `35 passed, 1 skipped in 20.28s` | One Postgres chat-first verification skipped because `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` was not set. |
| Whitespace / patch sanity | `git diff --check` | passed | Ran before this review task. |
| Postgres verification | `handoff_2026_04_28_v2_1_postgres_verification_hardening.md` | recorded `30 passed in 11.97s` | Recorded evidence accepted; not rerun in this task. |
| Android build | `handoff_2026_04_28_v2_1_android_workspace_onboarding.md`, `handoff_2026_04_28_v2_1_trace_message_history_visibility.md` | recorded `./gradlew :app:assembleDebug` passed | Recorded evidence accepted; not rerun in this docs-only review. |
| Device acceptance | `docs/delivery/evidence/v2_1_product_experience_device_acceptance/` and matching handoff | recorded passed | Predates later onboarding/history tasks. |
| LLM live smoke | `docs/product/research/v2_1_llm_sales_agent_eval_2026_04_28.md` | recorded `6 passed in 97.19s` | Explicit dev flag prototype only; not production-ready. |

---

## 5. PRD Acceptance Traceability

Status uses exactly: `done`, `partial`, `missing`, `out of scope`.

| PRD criterion | Status | Acceptance source | Code evidence | Validation evidence | Delivery evidence | Gap | Confidence |
|---|---|---|---|---|---|---|---|
| 用户无需理解 workspace，可通过轻量入口“开始销售工作区”进入聊天 | partial | V2 PRD §11 success criteria; PRD §6.1 chat-first entrance | Android has workspace create button and chat submit; backend has `POST /sales-workspaces` and sales-agent-turn route | Android build evidence for onboarding; backend targeted tests | P2 Android onboarding handoff; this review; 2026-04-28 product decision | Current UI behavior is close, but wording is still technical: button says "创建默认 workspace" instead of "开始销售工作区". This is product entry polish, not an implementation blocker. | high |
| Product Sales Agent 能主动提出 3 到 5 个关键追问 | done | V2 PRD §11; conversation acceptance examples | `backend/api/sales_workspace.py` clarifying question path; LLM runtime path | Backend targeted tests; recorded live LLM smoke | clarifying questions backend task; LLM eval docs | No V2.1 blocker. | high |
| 系统能形成第一版产品理解 | done | V2 PRD §6.1 / §11 | Product profile patch draft and `ProductProfileRevision` writeback path | Backend targeted tests; recorded device evidence | product extraction runtime task; final review evidence | More prompt quality is follow-up, not blocker. | high |
| 系统能形成第一版获客方向 | done | V2 PRD §6.1 / §11 | Lead direction patch draft and `LeadDirectionVersion` writeback path | Backend targeted tests; recorded device evidence | lead direction adjustment task; final review evidence | No V2.1 blocker. | high |
| 用户能通过对话调整获客方向 | done | V2 PRD §6.1 / §11 | Chat-first direction adjustment in backend route | Backend targeted tests cover Chinese constraints | lead direction adjustment and e2e tasks | Complex multi-round negotiation remains polish. | high |
| 系统能把调整沉淀为结构化版本 | done | V2 PRD §6.1 / §8 truth principles | `ProductProfileRevision`, `LeadDirectionVersion`, `WorkspacePatch`, `WorkspaceCommit` | Backend targeted tests; Postgres verification evidence | persistence and e2e tasks | Full visual diff/history is follow-up, not blocker. | high |
| 系统能生成当前 workspace 的 Markdown projection | done | V2 PRD §6.1; workspace kernel architecture | `backend/sales_workspace/projection.py` and projection route | Kernel tests and backend API tests | kernel / projection tasks | Markdown parse-back remains out of scope. | high |
| 系统能生成面向当前任务的 ContextPack | done | V2 PRD §6.1; runtime design | `backend/sales_workspace/chat_first.py`, `context_pack.py` | Backend targeted tests and kernel ContextPack tests | chat-first runtime backend task | ContextPack is derived runtime input, not formal truth. | high |
| Product Sales Agent 能解释当前推荐方向的原因 | done | V2 PRD §6.1 / §11 | workspace question path in `backend/api/sales_workspace.py`; LLM explanation path | Backend targeted tests; recorded live LLM smoke | workspace explanation task; LLM eval docs | No V2.1 blocker. | high |
| 对话、AgentRun、WorkspacePatch 和正式对象变更可追溯 | done | V2 PRD §11; runtime design trace rules | `ConversationMessage`, `SalesAgentTurnRun`, Draft Review, `WorkspaceCommit`, Postgres trace migration | Backend targeted tests; Postgres verification evidence | trace persistence and e2e tasks | Android full trace browser remains follow-up, not blocker. | high |
| 每轮消息应被持久化 | done | V2 PRD §6.1; runtime design | message routes and Postgres chat trace store | Backend targeted tests; Postgres verification evidence | trace message history handoff | No V2.1 blocker. | high |
| Android 仍是主控制入口 | done | V2 PRD §6.1 / §7 | `SalesWorkspaceScreen.kt`, backend client/parser/model | recorded Android assemble and device acceptance | Android chat-first UI, onboarding, history handoffs | Lightweight start button wording is tracked as polish. | medium-high |
| Tencent TokenHub LLM runtime prototype | done | LLM runtime boundary doc | explicit runtime mode and structured output parser | recorded fake-client tests and live smoke | LLM runtime closeout | Done only as explicit dev flag prototype, not production-ready. | medium-high |
| Formal LangGraph, V2.2 search, ContactPoint, CRM, automatic outreach | out of scope | V2 PRD §5.2 / §6.2 / §6.3; ADR-005; roadmap | N/A | N/A | `_active.md` blocked list | Must remain blocked until separate PRD / ADR / task gate. | high |

---

## 6. Capability Matrix Update Recommendation

| Capability | Current status | Recommended status | Evidence summary | Reason |
|---|---|---|---|---|
| Sales Workspace Kernel | `done` | `done` | Code, tests, architecture, API contract | No current V2.1 blocker. |
| Draft Review gate | `done` | `done` | Routes, persistence, tests, Android ID flow | Formal writeback gate exists. |
| Postgres persistence baseline | `done` | `done` | Alembic, repository, P5 verification | Production hardening remains out of scope. |
| Chat-first backend flow | `done` | `done` | Backend route and tests | Backend path satisfies V2.1. |
| Backend 5-sample conversational acceptance | `done` | `done` | Tests and acceptance examples | No blocker. |
| Android workspace demo path | `partial` | `partial` | Onboarding/history implemented and build-verified | Needs lightweight start button wording and entry polish. |
| Tencent TokenHub LLM runtime prototype | `partial` | `done / prototype` | Fake-client and live smoke recorded | Done only as explicit dev flag prototype; not production. |
| V2.1 product milestone | `partial / gap_closure_open` at initial review | `partial / product_entry_polish_open` | Product decision weakens one-sentence startup into lightweight start button entry | Do not mark done until review addendum confirms remaining PRD criteria and entry polish status. |

---

## 7. Milestone Status Recommendation

Recommended milestone status：

> **V2.1 product milestone remains partial; V2.1 lightweight product entry polish is open.**

Rationale：

- Most V2.1 backend, persistence, runtime prototype, Android demo, trace, and validation criteria are implemented.
- Product decision on 2026-04-28 weakens the original “one-sentence workspace start” wording into a lightweight “开始销售工作区” entry button.
- Current Android flow already has default workspace creation and chat-first turn, but wording still exposes the technical `workspace` concept.
- This is a V2.1 product entry polish item, not a V2.1 implementation blocker and not a V2.2 feature.

Required follow-up before status upgrade：

- Complete or re-scope `docs/delivery/tasks/task_v2_1_chat_first_workspace_start_gap_closure.md` as lightweight start button entry polish.
- Refresh this review or add an addendum after validation.

Human decision needed：

- None for the current product entry polish; it is authorized by the current V2.1-only package.
- Human decision is required only if implementation needs new API, migration, auth, multi-workspace, or product scope change.

---

## 8. Explicit Non-Goals

- Do not implement V2.2 search / ContactPoint / CRM.
- Do not open formal LangGraph.
- Do not treat LLM prototype as production-ready Product Sales Agent.
- Do not change PRD / ADR meaning.
- Do not close V2.1 product milestone until lightweight product entry polish is re-reviewed.

---

## 9. Known Limits

- Android assemble was not rerun during this docs-only review; recorded P2/P3 build evidence was used.
- Postgres live verification was not rerun during this docs-only review; recorded P5 evidence was used.
- Live Tencent TokenHub smoke was not rerun.
- Current worktree already contains planning-layer docs changes; this review treats them as the active baseline.

---

## 10. Recommended Next Package

- Package name：continue current `V2.1 Milestone Acceptance And Gap Closure`
- Package type：delivery
- Authorization source needed：already authorized by current human instruction
- Stop conditions：new backend API, migration, provider, V2.2 capability, or product-scope change
