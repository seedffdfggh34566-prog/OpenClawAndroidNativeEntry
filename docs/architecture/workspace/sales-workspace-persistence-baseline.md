# Sales Workspace Persistence Baseline

更新时间：2026-04-27

## 1. Purpose

本文档定义 V2 Sales Workspace 从 prototype continuity 进入 MVP-ready persistence 的正式 baseline。

它只定义 persistence 方向、对象边界和后续任务前置条件，不实现数据库 schema、migration、backend route、Android UI 或 Runtime / LangGraph。

---

## 2. Baseline Decision

V2 Sales Workspace MVP persistence baseline 采用：

> **Postgres / Alembic**

结论：

- Postgres 是 V2 MVP 的正式服务端 persistence baseline。
- Alembic 继续作为 migration 管理工具。
- SQLite 不作为 V2 Sales Workspace runtime fallback。
- JSON file store 只保留为 prototype / demo continuity，不承诺正式数据兼容或迁移。
- 本地 Postgres dev environment 需要单独 task 落地，优先 Docker Compose。
- 本文档不开放 DB migration 或 SQLAlchemy model implementation。

---

## 3. Route Comparison

### 3.1 JSON file store

定位：

- prototype continuity
- local demo replay
- contract smoke support

不作为：

- 正式 persistence baseline
- audit history store
- multi-workspace / multi-user data store
- production migration source of truth

原因：

- 缺少并发控制。
- 缺少可靠 transaction / constraint / index。
- 不适合 Draft Review lifecycle audit。
- 不适合长期 workspace 数据。

### 3.2 SQLite / Alembic

定位：

- 继续支持既有 V1 / test / legacy backend baseline。
- 可作为某些 backend tests 的临时数据库。

不作为：

- V2 Sales Workspace runtime fallback。
- V2 MVP 推荐 baseline。

原因：

- V2 已出现 Draft Review lifecycle、audit history、future multi-workspace 和 future runtime writeback。
- 如果同时承诺 SQLite / Postgres，会增加 schema、migration 和测试矩阵成本。
- SQLite 对未来服务化、多用户、并发写入不是理想默认。

### 3.3 Postgres / Alembic

定位：

- V2 MVP persistence baseline。
- formal workspace truth store。
- Draft Review audit history store。
- future Runtime / LangGraph integration 的稳定写回基础。

原因：

- 更适合长期 workspace 记录。
- 更适合 lifecycle event log、audit trail、version conflict 和 future multi-workspace。
- 与后续服务端部署、多用户、权限和 observability 演进更一致。

---

## 4. Persisted Object Boundary

下列对象属于正式持久化候选边界：

- `Workspace`
- `WorkspacePatch`
- write commit record
- `ProductProfileRevision`
- `LeadDirection`
- `LeadCandidate`
- `ResearchSource`
- `ResearchObservation`
- `WorkspacePatchDraftReview`
- Draft Review event log

最小原则：

- 所有正式对象必须归属 `workspace_id`。
- 所有正式写回必须可追溯到 patch / commit / review 来源。
- `base_workspace_version` 与 write conflict 语义必须保留。
- Runtime / Product Sales Agent execution layer 不能直接写 formal objects。
- Sales Workspace Kernel 仍是 formal writeback owner。

---

## 5. Draft Review Audit

Draft Review 需要长期 audit history，不只保留最新状态。

MVP persistence design 应至少覆盖：

- draft created / previewed
- accepted / rejected
- applied
- expired
- failed apply
- reviewer metadata
- runtime metadata
- base workspace version
- materialized patch id
- resulting workspace version
- failure reason / error code

推荐建模方向：

- `workspace_patch_draft_reviews` 保存当前 review object 状态。
- `workspace_patch_draft_review_events` 保存 lifecycle transition log。

具体表结构、字段类型和 migration revision 不在本文档实现；后续由 schema task 决定。

---

## 6. Derived Outputs

以下对象不是 formal primary store：

- `RankingBoard`
- Markdown projection
- `ContextPack`

原则：

- 必须能从结构化 workspace state 重新生成。
- 可以在后续性能或 UX 需要时增加 cache / snapshot，但 cache 不能成为唯一主真相。
- Markdown projection 不支持 parse-back。
- ContextPack 不读取 Markdown、LangGraph checkpoint 或 SDK session 作为主存。

---

## 7. Workspace / User Boundary

V2 MVP persistence baseline 必须支持 multi-workspace：

- schema design 必须以 `workspace_id` 为核心归属边界。
- 不能只围绕固定 `ws_demo` 设计。

V2 MVP persistence baseline 暂不实现完整 multi-user / permission / tenant isolation。

允许预留 metadata 概念：

- `owner_user_id`
- `created_by`
- `reviewed_by`
- `tenant_id`

这些字段是否落入首版 schema，由后续 schema design task 决定。即使预留，也不得在本阶段实现 auth、RBAC 或 tenant isolation。

---

## 8. Follow-up Gates

当前下一步只开放：

- `docs/delivery/tasks/task_v2_postgres_dev_environment_baseline.md`

后续仍需单独 task 才能开放：

- Sales Workspace persistence schema design。
- Postgres dev environment implementation。
- SQLAlchemy model implementation。
- Alembic migration。
- persistence-backed Sales Workspace API。
- Android review history。
- formal Runtime / LangGraph integration。

---

## 9. Explicit Non-goals

本文档不开放：

- backend code change。
- SQLAlchemy ORM。
- Alembic migration。
- SQLite schema change。
- Postgres runtime cutover。
- FastAPI route change。
- Android change。
- LangGraph / LLM / search / CRM / contact integration。
