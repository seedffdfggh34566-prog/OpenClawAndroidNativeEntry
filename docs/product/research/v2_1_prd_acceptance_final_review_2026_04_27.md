# V2.1 PRD Acceptance Final Review

日期：2026-04-27

## 1. Conclusion

当前可按 PRD acceptance traceability 宣称：

- **V2.1 workspace/kernel engineering baseline completed**
- **V2.1 conversational backend acceptance completed**
- **V2.1 conversational product experience prototype completed**

该结论的限定条件：

- 这是 deterministic prototype acceptance，不是正式 LLM / LangGraph product intelligence。
- Android 仍依赖已存在的 backend workspace；workspace 自动创建 / onboarding 不作为本次 V2.1 prototype blocker。
- V2.2 evidence/search/ContactPoint、CRM、自动触达和真实联网研究仍未开放。

## 2. PRD Acceptance Traceability

| PRD success criterion | Status | Evidence | Remaining limitation |
|---|---|---|---|
| 用户能通过 chat-first 输入进入 Sales Workspace flow | done | Android Workspace 页面可输入 chat-first turn；真机证据 `04_clarifying_questions_visible.png`、`05_product_draft_review_previewed.png`、`07_direction_draft_review_previewed.png`。 | Android 自动创建 workspace 未做，仍由 runbook / backend 创建 `ws_demo`。 |
| Product Sales Agent 能主动提出 3 到 5 个关键追问 | done | Backend tests 覆盖 `clarifying_question`；真机证据显示 5 个中文追问，且本轮不生成 patch draft、不写 workspace。 | Deterministic prototype，不是真实 LLM 追问。 |
| 系统能形成第一版产品理解 | done | Product turn 生成 `draft_review_sales_turn_product_profile_update_v1`；accept/apply 后 Android 显示 version 1 与 `FactoryOps AI`。 | Deterministic extraction；真实语义理解后续再接 LLM。 |
| 系统能形成第一版获客方向 | done | Direction turn 生成 `draft_review_sales_turn_lead_direction_update_v2`；accept/apply 后 Android 显示制造业、华东、中小企业、排除教育、已有 ERP。 | Deterministic extraction；不含真实搜索候选。 |
| 用户能通过对话调整获客方向 | done | 中文方向输入“优先华东制造企业，中小企业优先，排除教育行业，已有ERP。”生成新的 `LeadDirectionVersion:dir_chat_v2`。 | 更复杂多轮方向协商仍是后续 polish。 |
| 系统能把调整沉淀为结构化版本 | done | `GET /sales-workspaces/ws_demo` 确认 `current_product_profile_revision_id=ppr_chat_v1`、`current_lead_direction_version_id=dir_chat_v2`、`workspace_version=2`。 | Android trace browser / history UI 不在本轮。 |
| WorkspacePatch / Draft Review 是正式写回 gate | done | Android 仅创建和审阅 Draft Review；accept/apply 后由 backend Sales Workspace Kernel 写入 formal objects。 | 无阻塞缺口。 |
| 系统能生成 Markdown projection | done | Android 显示 projection 文件；backend projection endpoint 返回 `product/current.md`、`directions/current.md`、`rankings/current.md`。 | Markdown parse-back 仍 out of scope。 |
| 系统能生成 ContextPack | done | Android 显示 `ctx_ws_demo_v2`；backend context-pack endpoint 可读。 | ContextPack 是 runtime input snapshot，不是 formal truth。 |
| Product Sales Agent 能解释当前推荐方向的原因 | done | 真机证据 `12_workspace_explanation_visible.png` 显示解释型回答引用 product、direction、workspace version 和 ContextPack source versions。 | Deterministic explanation，不是真实 LLM 推理。 |
| ConversationMessage / AgentRun / WorkspacePatch / formal object 可追溯 | done | Backend chat-first tests 覆盖 AgentRun refs；device flow 生成 `run_sales_turn_*`、Draft Review、WorkspacePatch apply 和 formal object IDs。 | 完整 Android trace history UI 留给后续。 |
| 重启 / Postgres store 后可恢复当前状态 | done | Postgres store backend recheck 显示 version 2 workspace 可读；真机证据 `13_postgres_store_workspace_version2.png`。 | 生产级 backup / migration hardening 不在 V2.1。 |
| Android 控制入口可完成 V2.1 体验 | done | 真机验证 empty workspace、追问、product Draft Review、product apply、direction Draft Review、direction apply、ContextPack/projection、explanation answer。 | 自动创建 workspace 和完整聊天历史 UI 不在本轮。 |
| 真实 LLM、正式 LangGraph、联网搜索、ContactPoint、CRM | out of scope | PRD 将 search / evidence / ContactPoint 放入 V2.2 或后续；当前 docs 明确 blocked。 | 需要后续 V2.2 task 单独开放。 |

## 3. Evidence References

- PRD source: `docs/product/prd/ai_sales_assistant_v2_prd.md`
- Gap review: `docs/product/research/v2_1_prd_acceptance_gap_review_2026_04_27.md`
- Backend tests: `backend/tests/test_sales_workspace_chat_first_api.py`
- Android UI: `app/src/main/java/com/openclaw/android/nativeentry/ui/workspace/SalesWorkspaceScreen.kt`
- Device acceptance task: `docs/delivery/tasks/task_v2_1_product_experience_device_acceptance.md`
- Device evidence: `docs/delivery/evidence/v2_1_product_experience_device_acceptance/`

## 4. Final Gate

V2.1 can now be closed as:

> **V2.1 conversational product experience prototype completed.**

Do not broaden that sentence to mean:

- real LLM completed
- formal LangGraph completed
- V2.2 search / evidence / ContactPoint completed
- CRM or automatic outreach completed
- production SaaS completed

## 5. Recommended Next Step

Close the V2.1 product experience prototype in entry docs and `_active.md`.

After that, the next milestone should be V2.2 docs-level planning only. V2.2 implementation must remain blocked until a new PRD / ADR / task gate explicitly opens it.
