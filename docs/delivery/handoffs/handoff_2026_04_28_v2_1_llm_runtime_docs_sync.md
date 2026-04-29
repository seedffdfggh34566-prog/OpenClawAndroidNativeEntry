# Handoff: V2.1 LLM Runtime Docs Sync

日期：2026-04-28

## Changed

- 更新 `docs/README.md`、`docs/delivery/README.md`、`docs/reference/README.md`、`docs/how-to/README.md`、`docs/architecture/runtime/README.md`。
- 新增 `task_v2_1_llm_runtime_docs_sync.md`。

## Result

V2.1 LLM runtime prototype 入口已同步。

关键入口：

- `docs/architecture/runtime/v2-1-llm-runtime-boundary.md`
- `docs/reference/api/sales-workspace-chat-first-llm-runtime-contract.md`
- `docs/how-to/operate/v2-1-llm-runtime-dev-runbook.md`
- `docs/product/research/v2_1_llm_sales_agent_eval_2026_04_28.md`

## Validation

- docs rg check。
- `git diff --check`。

## Limitations

- LLM runtime 仍是 explicit dev flag prototype。
- 正式 LangGraph 与 V2.2 search/contact 仍 blocked。

## Next Step

执行 V2.1 LLM runtime closeout。
