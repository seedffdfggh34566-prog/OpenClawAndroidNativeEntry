# Data Architecture

更新时间：2026-04-26

当前目录用于承载数据库、文件存储、索引和数据主真相相关说明。

当前 V2 workspace-native 对象模型以以下文档为准：

- `../workspace/workspace-object-model.md`
- `../workspace/sales-workspace-kernel.md`
- `../workspace/workspace-kernel-v0-scope.md`

本目录中的 2026-04-25 草案保留为历史和辅助参考：

- `v2-sales-agent-data-model.md`：pre-workspace / session-first 草案，保留 `ConversationMessage`、`ProductProfileRevision`、`LeadDirectionVersion`、`AgentRun(run_type = sales_agent_turn)` 等建模参考；不再作为 V2 根对象路线。
- `v2-lead-research-data-model.md`：V2.2 lead research 子模型草案，保留搜索、来源、候选、联系方式边界参考；对象命名和主路径需要后续对齐 `ResearchRound`、`CompanyCandidate`、`CandidateRankingBoard`。

后续可放：

- SQLite / Postgres 迁移
- 文件与对象存储策略
- 数据生命周期说明
- V2 workspace schema baseline
