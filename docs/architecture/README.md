# Architecture Docs

更新时间：2026-04-26

当前架构层文档用于说明系统分层、仓库结构和 Android / backend / runtime / data / workspace 关系。

优先阅读：

- `workspace/`
- `system-context.md`
- `repository-layout.md`
- `backend/`
- `runtime/`
- `clients/`
- `data/`

当前 V2 架构主入口：

- `workspace/workspace-object-model.md`
- `workspace/sales-workspace-kernel.md`
- `workspace/sales-workspace-persistence-baseline.md`
- `workspace/sales-workspace-persistence-schema.md`
- `workspace/workspace-kernel-v0-scope.md`
- `workspace/markdown-projection.md`
- `workspace/context-pack-compiler.md`

当前 V2 架构基准：

- `SalesWorkspace` 是 V2 根对象。
- Sales Workspace Kernel 是当前技术主线。
- 结构化 workspace state 是主真相。
- Markdown 是 projection，不是唯一主存。
- ContextPack 从结构化 state 编译。
- V2 MVP persistence baseline 采用 Postgres / Alembic；JSON file store 只作为 prototype continuity。
- V2 Sales Workspace persistence schema design 已完成；下一步仍不自动开放 Alembic migration。
- LangGraph 后续只作为 runtime execution layer。

当前与客户端边界直接相关的重点文档包括：

- `clients/mobile-information-architecture.md`
- `clients/android-client-implementation-constraints.md`

当前与后端 / runtime 演进直接相关的重点文档包括：

- `backend/backend-agent-stack-phased-adoption.md`
- `runtime/v2-1-chat-first-runtime-design.md`
- `runtime/openclaw-context-management-reference.md`
- `runtime/hermes-context-management-reference.md`
- `runtime/langgraph-runtime-architecture.md`

注意：`runtime/langgraph-runtime-architecture.md` 仍包含 2026-04-25 session-first runtime 草案内容；当前 V2 workspace-native 边界以 `workspace/` 文档和 `_active.md` 为准。
