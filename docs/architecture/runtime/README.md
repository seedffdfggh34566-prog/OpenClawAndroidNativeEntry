# Runtime Architecture

当前目录用于承载 OpenClaw / agent runtime 的接入与执行层说明。

后续可放：

- runtime 适配边界
- tool 调用约束
- 执行状态与产品对象关系

当前优先阅读：

- `langgraph-runtime-architecture.md`

当前 runtime 层的关键原则是：

- runtime 是执行层，不是产品主真相层
- 正式对象写回仍由 backend product services 协调
- Phase 1 先替换 `lead_analysis` / `report_generation` 的 stub runtime
