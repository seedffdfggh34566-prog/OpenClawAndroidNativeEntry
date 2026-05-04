# Runtime Architecture

更新时间：2026-04-29

当前 V3 runtime 入口优先看：

- `../v3/memory-native-sales-agent.md`
- `langgraph-letta-style-sales-agent-memory.md`
- `../backend/backend-agent-stack-phased-adoption.md`

V3 runtime 方向：

- LangGraph / LangChain 是优先自研 runtime 路线。
- Product Sales Agent runtime memory 可以保存 observed / inferred / hypothesis / confirmed / rejected / superseded。
- Letta-style memory blocks、archival memory、memory tools 和 compaction 是主要参考。
- Runtime memory 是开放认知层；formal business objects 仍由 backend governance 裁决。

历史参考：

- `v2-1-llm-runtime-boundary.md`：V2.1 explicit-flag LLM prototype boundary。
- `sales-workspace-chat-first-llm-runtime-contract.md` 在 `docs/reference/api/` 下，是 V2.1 `real_llm_no_langgraph` contract。
- `langgraph-runtime-architecture.md`：V1/V2.1 draft-runtime 背景，不是 V3 memory runtime contract。
- `openclaw-context-management-reference.md` / `hermes-context-management-reference.md`：外部项目参考。
