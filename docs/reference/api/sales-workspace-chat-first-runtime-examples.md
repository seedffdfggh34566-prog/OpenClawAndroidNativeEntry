# Sales Workspace Chat-first Runtime Examples

更新时间：2026-04-27

## 1. 文档定位

本文档提供 V2.1 chat-first Runtime contract examples，用固定 JSON examples 说明用户消息、`AgentRun`、`ContextPack`、`WorkspacePatchDraft`、Draft Review 和 WorkspaceCommit 的引用链。

这些 examples 用于：

- 验证 V2.1 product experience 的最小 chat-first flow。
- 固定产品理解和获客方向两类 Runtime draft 的 contract shape。
- 支撑后续 trace persistence migration、backend prototype 和 Android chat-first UI。

这些 examples 不是：

- backend route implementation。
- LangGraph graph implementation。
- real LLM output。
- DB fixture。
- Android UI implementation。
- V2.2 search / ContactPoint / CRM contract。

关联文档：

- `docs/reference/api/sales-workspace-chat-first-runtime-contract.md`
- `docs/architecture/runtime/v2-1-chat-first-runtime-design.md`
- `docs/delivery/tasks/task_v2_1_chat_first_runtime_contract_examples.md`

---

## 2. 示例目录

JSON examples 位于：

```text
docs/reference/api/examples/sales_workspace_chat_first_runtime_v2_1/
```

文件：

- `01_product_message.json`
- `02_product_agent_run_response.json`
- `03_lead_direction_message.json`
- `04_lead_direction_agent_run_response.json`
- `05_mixed_patch_draft.json`
- `06_draft_review_accept_apply_trace.json`
- `07_rejected_draft_trace.json`
- `08_out_of_scope_v2_2_response.json`

---

## 3. State Transition

示例使用稳定 workspace：

- workspace：`ws_demo`
- product：`FactoryOps AI`
- user message：`msg_user_product_001`, `msg_user_direction_001`
- agent runs：`run_sales_turn_product_001`, `run_sales_turn_direction_001`
- context packs：`ctx_sales_turn_product_001`, `ctx_sales_turn_direction_001`
- draft reviews：`draft_review_sales_turn_product_001`, `draft_review_sales_turn_direction_001`

最小 V2.1 chat-first flow：

```text
ConversationMessage:user
-> AgentRun(run_type=sales_agent_turn)
-> ContextPack(task_type=sales_agent_turn)
-> WorkspacePatchDraft
-> WorkspacePatchDraftReview
-> human review accept/reject
-> Sales Workspace Kernel apply
-> WorkspaceCommit
-> ConversationMessage:assistant
```

---

## 4. Contract Notes

- `ConversationMessage` 是用户和 assistant 交互记录，不是正式 workspace object。
- `AgentRun` 记录 Runtime execution trace，不替代 Draft Review lifecycle。
- `ContextPack` 是 Runtime 输入快照，不是正式 workspace 主存。
- Runtime 只能产出 `WorkspacePatchDraft`。
- Draft Review 是人工审阅边界。
- Sales Workspace Kernel 仍是正式对象写回裁决层。
- Markdown projection、ranking board、ContextPack 都是 derived output，不支持 parse-back。
- V2.2 evidence / search / ContactPoint 请求必须返回受限说明，不得生成无来源 formal candidate。

---

## 5. Validation

验证命令：

```bash
find docs/reference/api/examples/sales_workspace_chat_first_runtime_v2_1 -name "*.json" -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
rg "sales-workspace-chat-first-runtime-examples.md|sales_workspace_chat_first_runtime_v2_1" docs/reference docs/delivery docs/README.md
rg "ConversationMessage|AgentRun|ContextPack|WorkspacePatchDraft|draft_review_sales_turn" docs/reference/api/sales-workspace-chat-first-runtime-examples.md docs/reference/api/examples/sales_workspace_chat_first_runtime_v2_1
```
