# Architecture Docs

更新时间：2026-04-30

架构层文档用于说明系统分层、runtime、backend governance、Android / data / workspace 关系。

## 当前入口

- `v3/memory-native-sales-agent.md`
- `v3/web-dual-entry-prototype.md`
- `runtime/langgraph-letta-style-sales-agent-memory.md`
- `backend/backend-agent-stack-phased-adoption.md`
- `system-context.md`

## 当前架构基准

- 当前主线是 V3 Memory-native Sales Agent。
- LangGraph / LangChain 是优先 runtime 路线。
- Product Sales Agent runtime memory 可以开放保存推断、假设、策略和纠错。
- Backend / Sales Workspace Kernel 仍治理 formal business objects。
- Web 可作为 V3 双入口原型：`/lab` 用于内部测试，`/workspace` 用于真实销售用户雏形；App 仍是长期主要入口。
- V2 workspace/kernel/runtime 文档保留为 historical validated prototype / reference only。

## 历史参考

- `workspace/`：V2 Sales Workspace / Kernel / persistence asset。
- `runtime/`：V1/V2.1 runtime contract 和参考研究。
- `data/`：V2 early data model drafts。
- `clients/`：Android client constraints。
