# Handoff: V2.1 LLM Sales Agent Turn Backend Prototype

日期：2026-04-28

## Changed

- 新增 Tencent TokenHub LLM sales-agent-turn runtime module。
- 扩展 chat-first endpoint，在 `OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=llm` 时调用 LLM runtime。
- 新增 LLM runtime fake-client tests。

## Result

LLM mode 可以生成：

- `clarifying_question` assistant message，无 Draft Review。
- `workspace_question` assistant message，无 Draft Review。
- `draft_summary` + `WorkspacePatchDraftReview`，仍需人工 accept/apply。

Default deterministic mode 不变。

## Validation

- `backend/tests/test_sales_workspace_chat_first_llm_runtime.py`
- `backend/tests/test_sales_workspace_chat_first_api.py`
- `git diff --check`

## Limitations

- fake-client tests 已覆盖主要行为。
- live Tencent TokenHub smoke 在下一 task 执行。

## Next Step

执行 `task_v2_1_llm_eval_acceptance_examples.md`。
