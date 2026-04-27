# Handoff: V2.1 Chat-first Runtime Design

日期：2026-04-27

## Summary

本次完成 V2.1 product experience 的 chat-first Runtime design。结论是：V2.1 engineering baseline 已完成，但产品体验还需要通过 `ConversationMessage -> AgentRun -> ContextPack -> WorkspacePatchDraft -> DraftReview -> WorkspaceCommit` 闭环补齐。

本轮没有实现 backend route、LangGraph graph、真实 LLM、Android UI、search、ContactPoint 或 CRM。

## Changed

- 新增 `docs/architecture/runtime/v2-1-chat-first-runtime-design.md`。
- 新增 `docs/reference/api/sales-workspace-chat-first-runtime-contract.md`。
- 新增后续 planned / blocked tasks：
  - `task_v2_1_chat_first_runtime_contract_examples.md`
  - `task_v2_1_chat_first_runtime_backend_prototype.md`
- 更新当前 task `task_v2_1_chat_first_runtime_design.md` 为 done。
- 更新 `_active.md`、docs / delivery / architecture / reference 入口。

## Design Outcome

- Runtime 仍只是 execution layer。
- Formal writeback 仍由 backend / Sales Workspace Kernel 裁决。
- ProductProfileRevision 和 LeadDirectionVersion 是 V2.1 chat-first 体验的正式对象目标。
- ContextPack 未来需要支持 `task_type = sales_agent_turn`。
- AgentRun 保持轻量 lifecycle：`queued`、`running`、`succeeded`、`failed`。
- V2.2 evidence / search / ContactPoint 继续 blocked。

## Validation

Actual validation:

- `rg "ConversationMessage|AgentRun|WorkspacePatchDraft|ProductProfileRevision|LeadDirectionVersion" docs/architecture docs/reference docs/delivery`
- `rg "V2.1 product experience|V2.2.*blocked|不接真实 LLM|不实现 LangGraph" docs`
- `git diff --check`

## Known Limitations

- 未实现 chat-first backend API。
- 未持久化 ConversationMessage / AgentRun 的 V2.1 新链路。
- 未实现 `ContextPack(task_type = sales_agent_turn)`。
- 未接真实 LLM 或正式 LangGraph graph。
- 未改 Android chat UI。

## Recommended Next Step

先执行 docs / examples-only：

- `task_v2_1_chat_first_runtime_contract_examples.md`

完成 examples 后，再决定是否开放：

- `task_v2_1_chat_first_runtime_backend_prototype.md`
