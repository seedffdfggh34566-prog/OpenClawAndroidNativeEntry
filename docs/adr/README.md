# ADR Docs

更新时间：2026-04-27

当前目录用于承载关键架构与部署决策记录。

建议命名方式：

- `ADR-001-...`
- `ADR-002-...`
- `ADR-003-...`

当前 V2 planning baseline 决策入口：

- `ADR-007-v2-sales-workspace-persistence-decision.md`：当前 persistence decision。V2 MVP persistence baseline 已冻结为 Postgres / Alembic；JSON file store 仍是 prototype continuity；下一项只开放 Postgres dev environment baseline，不直接实现 Sales Workspace schema migration 或 persistence-backed API。
- `ADR-006-v2-conversational-sales-agent-baseline.md`：当前 V2 workspace-native sales agent baseline。文件名保留 historical slug，但正文已升级为 Sales Workspace / Sales Workspace Kernel 方向。
- `ADR-005-v2-lead-research-scope-and-search-boundary.md`：V2.2 search、source evidence、contact boundary guardrail。其搜索和联系方式边界继续有效，但具体对象应后续对齐 `ResearchRound`、`CompanyCandidate`、`CandidateRankingBoard`。

当前 V1 baseline 决策入口：

- `ADR-001-backend-deployment-baseline.md`
- `ADR-002-v1-runtime-and-product-learning-baseline.md`
- `ADR-003-v1-product-learning-runtime-boundary.md`
- `ADR-004-v1-product-learning-iteration-contract.md`
