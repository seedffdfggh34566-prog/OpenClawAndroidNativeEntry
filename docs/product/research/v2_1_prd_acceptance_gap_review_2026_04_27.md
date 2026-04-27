# V2.1 PRD Acceptance Gap Review

日期：2026-04-27

## 1. Conclusion

当前不能按 PRD success criteria 宣称完整 V2.1 completed。

当前可宣称：

- **V2.1 workspace/kernel engineering baseline completed**
- **V2.1 deterministic chat-first demo flow completed**

当前不可宣称：

- **V2.1 conversational product experience completed**
- **V2.1 Product Sales Agent prototype completed**

原因是当前实现已经打通 ConversationMessage、AgentRun、ContextPack、WorkspacePatchDraft、Draft Review、WorkspacePatch、ProductProfileRevision / LeadDirectionVersion 和 Android 可见闭环，但 Product Sales Agent 仍是 deterministic prototype，没有满足 PRD 中主动追问、解释型回答和多中文业务样例验收要求。

## 2. PRD Acceptance Traceability

| PRD success criterion | Status | Current evidence | Gap |
|---|---|---|---|
| 用户能通过一句自然语言启动一个 `SalesWorkspace` | partial | `POST /sales-workspaces` 可创建 workspace；Android 可加载固定 `ws_demo` 并提交 chat-first turn。 | Android 仍依赖已存在 workspace；尚未定义用户一句话自动初始化 workspace lifecycle。 |
| Product Sales Agent 能主动提出 3 到 5 个关键追问 | missing | schema / contract 支持 `clarifying_question`。 | backend 目前没有主动追问策略、测试或 Android 验收；assistant message 主要是固定 draft summary。 |
| 系统能形成第一版产品理解 | partial | chat-first product turn 可生成 `WorkspacePatchDraft`，apply 后写入 `ProductProfileRevision`；真机验收显示 version 1 可见。 | 当前 product profile 字段由 deterministic 固定逻辑生成，不是真正从用户自然语言抽取。 |
| 系统能形成第一版获客方向 | partial | lead direction turn 可生成并 apply `LeadDirectionVersion`；真机验收显示 version 2 可见。 | 当前获客方向由 deterministic 固定逻辑生成，缺少多业务样例验证。 |
| 用户能通过对话调整获客方向 | partial | `lead_direction_update` message type 可生成新的 direction version。 | 缺少自然语言纠正 / 排除行业 / 限定地区 / 调整规模的多轮样例和断言。 |
| 系统能把调整沉淀为结构化版本 | partial | `LeadDirectionVersion`、WorkspacePatch 和 WorkspaceCommit 已存在。 | 需要验证用户纠正后的字段来自当前 message，并记录 source message refs / change reason。 |
| 系统能生成当前 workspace 的 Markdown projection | done | Markdown projection 已由 structured workspace state 生成；projection 不 parse-back。 | 无阻塞缺口。 |
| 系统能生成面向当前任务的 ContextPack | done | `sales_agent_turn` ContextPack 和 research ContextPack 均已实现；trace persistence 已建表。 | 后续应确保解释型回答也使用 ContextPack。 |
| Product Sales Agent 能解释当前推荐方向的原因 | missing | contract / design 中有 `workspace_question` / explanation 语义。 | backend 当前仅返回固定“解释当前 workspace 状态”文案，没有基于 ProductProfileRevision / LeadDirectionVersion 生成解释。 |
| 对话、AgentRun、WorkspacePatch 和正式对象变更可追溯 | partial | ConversationMessage、AgentRun、ContextPack、Draft Review、PatchCommit、formal objects 已有 persistence path。 | 需要补端到端 trace assertions：AgentRun output refs 指向 assistant message、draft review、patch commit 和 changed object refs。 |
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

The next V2.1 work should stay backend-first and deterministic-first:

1. Add active clarifying questions for incomplete product / direction inputs.
2. Add workspace explanation answers grounded in current structured objects.
3. Expand deterministic product profile extraction beyond one fixed FactoryOps AI path.
4. Expand deterministic lead direction adjustment beyond one fixed East China manufacturing path.
5. Add 5 Chinese business acceptance examples and use them as implementation tests.
6. Add traceability assertions for AgentRun output refs, Draft Review apply, WorkspaceCommit, and formal object changes.

## 5. Non-goals

- Do not start V2.2 search / evidence / ContactPoint implementation.
- Do not add CRM, automatic outreach, or contact scraping.
- Do not require real LLM or formal LangGraph to complete the next deterministic V2.1 acceptance gate.
- Do not claim full V2.1 completed until all PRD success criteria are `done` or explicitly re-scoped by product docs.
