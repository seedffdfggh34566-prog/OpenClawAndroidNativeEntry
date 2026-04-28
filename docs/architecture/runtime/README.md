# Runtime Architecture

当前目录用于承载 OpenClaw / agent runtime 的接入与执行层说明。

后续可放：

- runtime 适配边界
- tool 调用约束
- 执行状态与产品对象关系

当前优先阅读：

- `v2-1-chat-first-runtime-design.md`
- `v2-1-llm-runtime-boundary.md`
- `v2-1-chat-first-trace-persistence-schema.md`
- `langgraph-runtime-architecture.md`

当前 runtime 层的关键原则是：

- runtime 是执行层，不是产品主真相层
- 正式对象写回仍由 backend product services 协调
- Phase 1 先替换 `lead_analysis` / `report_generation` 的 stub runtime
- V2.1 chat-first product experience 已有 deterministic runtime prototype；Tencent TokenHub LLM runtime prototype 通过显式 dev flag 启用
- LLM runtime 仍不等于 formal LangGraph，正式写回仍经过 Draft Review 和 Sales Workspace Kernel
