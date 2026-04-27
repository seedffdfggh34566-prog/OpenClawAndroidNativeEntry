# V2.1 PRD Acceptance Gap Review

日期：2026-04-27

## 1. Conclusion

当前不能按 PRD success criteria 宣称完整 V2.1 completed。

当前可宣称：

- **V2.1 workspace/kernel engineering baseline completed**
- **V2.1 deterministic chat-first demo flow completed**
- **V2.1 conversational backend acceptance completed**

当前不可宣称：

- **V2.1 conversational product experience completed**
- **V2.1 Product Sales Agent prototype completed**

原因是当前 backend 已覆盖主动追问、解释型回答、产品理解抽取、获客方向调整和 5 个中文业务样例 e2e，但 Android polish / 真机验收仍未覆盖这些新 backend 行为。因此完整 V2.1 conversational product experience 仍不能宣称完成。

## 2. PRD Acceptance Traceability

| PRD success criterion | Status | Current evidence | Gap |
|---|---|---|---|
| 用户能通过一句自然语言启动一个 `SalesWorkspace` | partial | `POST /sales-workspaces` 可创建 workspace；Android 可加载固定 `ws_demo` 并提交 chat-first turn。 | Android 仍依赖已存在 workspace；尚未定义用户一句话自动初始化 workspace lifecycle。 |
| Product Sales Agent 能主动提出 3 到 5 个关键追问 | partial | backend deterministic `clarifying_question` 已实现并测试；不足输入不生成 Draft Review，不 mutate workspace。 | Android polish / 真机验收尚未覆盖追问展示。 |
| 系统能形成第一版产品理解 | partial | backend deterministic extraction 已覆盖 5 个中文业务样例；chat-first product turn 生成 `WorkspacePatchDraft`，apply 后写入 `ProductProfileRevision`。 | Android 尚未覆盖 5 个样例；仍不是真实 LLM。 |
| 系统能形成第一版获客方向 | partial | backend deterministic lead direction draft 可生成并 apply `LeadDirectionVersion`。 | Android 尚未覆盖 5 个样例方向流。 |
| 用户能通过对话调整获客方向 | partial | backend 已支持排除行业、指定地区、指定规模、优先约束等中文调整。 | Android polish / 真机验收尚未覆盖调整流程。 |
| 系统能把调整沉淀为结构化版本 | partial | backend e2e 验证调整写入 `LeadDirectionVersion`、WorkspacePatch 和 WorkspaceCommit，`change_reason` 包含 source message marker。 | 仍需 Android 可见性和更完整 trace browser / history UI。 |
| 系统能生成当前 workspace 的 Markdown projection | done | Markdown projection 已由 structured workspace state 生成；projection 不 parse-back。 | 无阻塞缺口。 |
| 系统能生成面向当前任务的 ContextPack | done | `sales_agent_turn` ContextPack 和 research ContextPack 均已实现；trace persistence 已建表。 | 后续应确保解释型回答也使用 ContextPack。 |
| Product Sales Agent 能解释当前推荐方向的原因 | partial | backend `workspace_question` 已基于 `ProductProfileRevision`、`LeadDirectionVersion` 和 ContextPack source versions 回答。 | Android polish / 真机验收尚未覆盖解释型回答展示。 |
| 对话、AgentRun、WorkspacePatch 和正式对象变更可追溯 | partial | backend e2e 已断言 AgentRun output refs、Draft Review、WorkspaceCommit 和 changed object refs。 | Postgres 重启恢复和 Android trace 可见性仍需单独验收。 |
| Android 控制入口可完成 V2.1 体验 | partial | 真机截图证明 empty workspace、product apply、direction apply 可见。 | Android 尚未验证主动追问、解释型回答和 5 个中文业务样例。 |
| 真实 LLM、正式 LangGraph、联网搜索、ContactPoint、CRM | out of scope | PRD 将搜索、候选公司、联系方式放入 V2.2 或后续。 | 不应作为 V2.1 completion blocker。 |

## 3. Evidence References

- PRD source: `docs/product/prd/ai_sales_assistant_v2_prd.md`
- Runtime design: `docs/architecture/runtime/v2-1-chat-first-runtime-design.md`
- API contract: `docs/reference/api/sales-workspace-chat-first-runtime-contract.md`
- Backend implementation: `backend/api/sales_workspace.py`
- Chat trace models: `backend/sales_workspace/chat_first.py`
- Backend tests: `backend/tests/test_sales_workspace_chat_first_api.py`
- Android UI: `app/src/main/java/com/openclaw/android/nativeentry/ui/workspace/SalesWorkspaceScreen.kt`
- Demo runbook: `docs/how-to/operate/v2-1-product-experience-demo-runbook.md`

## 4. Required V2.1 Completion Work

Backend-first deterministic work completed in this chain:

1. Add active clarifying questions for incomplete product / direction inputs.
2. Add workspace explanation answers grounded in current structured objects.
3. Expand deterministic product profile extraction beyond one fixed FactoryOps AI path.
4. Expand deterministic lead direction adjustment beyond one fixed East China manufacturing path.
5. Add 5 Chinese business acceptance examples and use them as implementation tests.
6. Add traceability assertions for AgentRun output refs, Draft Review apply, WorkspaceCommit, and formal object changes.

Remaining V2.1 product-experience work:

1. Android polish for clarifying questions, explanation answers, Draft Review state, and 5 sample visibility.
2. Device-level acceptance for the new backend conversational behavior.
3. Optional Postgres recovery smoke for the 5-sample backend flow when a Postgres verification URL is available.

## 5. Non-goals

- Do not start V2.2 search / evidence / ContactPoint implementation.
- Do not add CRM, automatic outreach, or contact scraping.
- Do not require real LLM or formal LangGraph to complete the next deterministic V2.1 acceptance gate.
- Do not claim full V2.1 completed until all PRD success criteria are `done` or explicitly re-scoped by product docs.
