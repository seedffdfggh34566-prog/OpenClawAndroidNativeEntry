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
| 用户无需理解 workspace，可通过轻量入口“开始销售工作区”进入聊天 | missing | V2 PRD §11 success criteria; PRD §6.1 chat-first entrance | 历史代码证据曾指向 Android start button、default workspace create-or-enter handling、chat submit；backend 仍有 `POST /sales-workspaces` 和 sales-agent-turn route | 历史 `./gradlew :app:assembleDebug`、adb install/start、backend targeted tests 只能说明局部实现和安装启动；未形成用户可见聊天入口证据 | P2 Android onboarding handoff; lightweight start entry polish handoff; 2026-04-28 product decision; 2026-04-28 human acceptance feedback: Android app 未看到聊天入口 | Android product entry 在当前人工验收下不成立。必须恢复首屏或明确导航路径上的“开始销售工作区”入口，点击后可见聊天输入，并补充可复现 evidence。 | high |
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
| Android 仍是主控制入口 | partial | V2 PRD §6.1 / §7 | `SalesWorkspaceScreen.kt`, backend client/parser/model | recorded Android assemble and device acceptance; current human acceptance says chat entry is not visible in app | Android chat-first UI, onboarding, history handoffs; 2026-04-28 human feedback | Android app 作为主控制入口不能只存在于代码或历史截图；当前必须能被用户直接看到并进入聊天。 | high |
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
| Android workspace demo path | `partial` | `missing / product entry` | 历史 onboarding/history 和 lightweight start button polish 只保留为实现尝试证据；人工验收反馈推翻 product-entry done 结论 | 用户在 Android app 上未看到聊天入口；必须重新开放 V2.1 Android chat-first product entry recovery。 |
| Tencent TokenHub LLM runtime prototype | `partial` | `done / prototype` | Fake-client and live smoke recorded | Done only as explicit dev flag prototype; not production. |
| V2.1 product milestone | `partial / gap_closure_open` at initial review | `partial / android_chat_entry_missing` | Product decision weakens one-sentence startup into lightweight start button entry, but current Android human acceptance shows the entry is not visible | V2.1 remains not implemented at product-experience level until Android chat entry recovery is completed and accepted. |

---

## 7. Milestone Status Recommendation

Recommended milestone status：

> **V2.1 product milestone remains partial / android_chat_entry_missing. V2.1 is not implemented at product-experience level until the Android app visibly exposes the chat-first Sales Workspace entry.**

Rationale：

- Most V2.1 backend, persistence, runtime prototype, Android demo, trace, and validation criteria are implemented.
- Product decision on 2026-04-28 weakens the original “one-sentence workspace start” wording into a lightweight “开始销售工作区” entry button.
- The prior conclusion that Android flow has a usable productized “开始销售工作区” entry is superseded by 2026-04-28 human acceptance feedback: the Android app did not show a chat entry.
- This is a V2.1 product entry blocker, not a V2.2 feature.

Required follow-up before status upgrade：

- Open a V2.1-only Android chat-first product entry recovery package.
- Do not evaluate milestone completion again until the user-visible Android entry and representative chat path are restored.

Human decision needed：

- No product decision is needed to recover the current V2.1 Android entry; the desired product shape remains lightweight button “开始销售工作区” followed by chat.
- Human decision is required if implementation needs new API, migration, auth, multi-workspace, or product scope change.

---

## 8. Explicit Non-Goals

- Do not implement V2.2 search / ContactPoint / CRM.
- Do not open formal LangGraph.
- Do not treat LLM prototype as production-ready Product Sales Agent.
- Do not change PRD / ADR meaning.
- Do not close V2.1 product milestone from task / handoff evidence alone; any status change requires Status / Planning review.

---

## 9. Known Limits

- Android assemble was rerun for the addendum task and passed, but that validation is insufficient because current human acceptance did not find the chat entry in the app.
- Postgres live verification was not rerun during this docs-only review; recorded P5 evidence was used.
- Live Tencent TokenHub smoke was not rerun.
- Current worktree already contains planning-layer docs changes; this review treats them as the active baseline.
- Device click-level Workspace smoke was not completed because adb restored the app to a historical `分析报告` detail page; install/start evidence was collected. This is now treated as a product-entry gap, not a non-blocking limitation.

---

## 10. Recommended Next Package

- Open `docs/delivery/packages/package_v2_1_android_chat_entry_recovery.md`.
- Current implementation task should recover Android chat-first entry and representative demo path before any milestone status upgrade.

---

## 11. Addendum: Lightweight Start Entry Polish Evidence

更新时间：2026-04-28

本 addendum 只记录当前 lightweight entry polish task 的 evidence，不单独宣称 V2.1 product milestone 完成。

| Item | Status | Evidence | Notes |
|---|---|---|---|
| 入口按钮产品化为“开始销售工作区” | partial | `SalesWorkspaceScreen.kt` | 代码/文案证据存在，但当前人工验收未在 Android app 看到聊天入口。 |
| 点击后创建或进入默认 `ws_demo` | partial | `OpenClawApp.kt` | 代码证据存在；需要从用户可见入口开始复验。 |
| 进入后展示 chat-first 输入 | missing | `SalesWorkspaceScreen.kt`, `OpenClawApp.kt` | 当前人工验收反馈为 Android app 未看到聊天入口。 |
| 已加载 workspace 的 chat submit 不回退 | partial | `OpenClawApp.kt` | 后端和 app state 代码证据存在；产品路径不可见时不能作为 done。 |
| Android build validation | done | `./gradlew :app:assembleDebug` | 通过；保留既有 AGP/compileSdk warning 和 `LocalLifecycleOwner` deprecation warning。 |
| Device smoke | partial | `adb devices`, `adb install -r`, `adb shell am start`, `uiautomator dump` | 设备 `f3b59f04` 可安装并启动；设备恢复在历史 `分析报告` 内页，未自动完成 Workspace 页点击级 smoke。 |

Updated recommendation：

- Lightweight product entry polish 只有代码和 build/install evidence，不足以证明用户可见产品入口成立。
- 当前 addendum 结论修正为：V2.1 Android chat-first entry missing。
- V2.1 product milestone 不得升级；必须先执行 V2.1 Android chat-first product entry recovery package。
