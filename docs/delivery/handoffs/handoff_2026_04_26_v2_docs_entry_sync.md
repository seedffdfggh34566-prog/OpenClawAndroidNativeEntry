# 阶段性交接：V2 docs entry sync

更新时间：2026-04-26

## 1. 本次改了什么

- 同步 `docs/README.md`，将总入口更新为 2026-04-26 workspace-native sales agent / Sales Workspace Kernel baseline。
- 同步 `docs/delivery/README.md`，将当前任务状态更新为 `task_v2_sales_workspace_kernel_backend_only_v0.md`。
- 同步 `docs/product/README.md`，补充 workspace architecture 入口，并弱化 2026-04-25 data model 的入口优先级。
- 同步 `docs/architecture/README.md`，新增 `workspace/` 作为当前 V2 架构主入口。
- 同步 `docs/architecture/data/README.md`，标注 2026-04-25 data model 是 pre-workspace / session-first 参考。
- 同步 `docs/adr/README.md`，明确 ADR-006 是当前 workspace-native baseline，ADR-005 继续作为 V2.2 search/contact guardrail。

## 2. 本次未改什么

- 未修改 V2 PRD 正文。
- 未修改 ADR 正文。
- 未修改 workspace architecture 正文。
- 未修改 `_active.md`。
- 未修改 backend / Android / runtime 代码。

## 3. 验证

- 检查入口层不再保留“Current task：暂无”“尚未创建 V2 implementation queue”等过期导航语句。
- 检查入口层包含当前 workspace architecture 与 kernel v0 task 路径。
- 运行 `git status --short` 检查变更范围。
- 本次为 Markdown-only 文档入口同步，未运行 Android/backend build。

## 4. 已知限制

- `docs/architecture/data/v2-sales-agent-data-model.md` 正文仍是 2026-04-25 pre-workspace 草案。
- `docs/architecture/data/v2-lead-research-data-model.md` 正文仍包含 `LeadResearchResult` 路线，需要后续与 `ResearchRound` / `CandidateRankingBoard` 对齐。
- `docs/architecture/runtime/langgraph-runtime-architecture.md` 正文仍包含 `SalesAgentSession` / `sales_agent_turn_graph` 的旧边界，需要后续单独更新。

## 5. 推荐下一步

继续执行当前任务：

```text
docs/delivery/tasks/task_v2_sales_workspace_kernel_backend_only_v0.md
```

后续如需继续消除正文层漂移，建议单独创建 data/runtime 文档同步任务。
