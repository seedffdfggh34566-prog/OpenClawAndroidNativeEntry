# ADR-007：V2 Sales Workspace persistence decision

- 状态：Accepted
- 日期：2026-04-27
- 关联任务：`docs/delivery/tasks/task_v2_sales_workspace_persistence_decision.md`

---

## 1. 背景

Sales Workspace Kernel backend-only v0 已完成，已验证：

- Pydantic object model。
- in-memory / JSON fixture store。
- WorkspacePatch apply。
- deterministic candidate ranking。
- Markdown projection。
- ContextPack compiler。
- pytest e2e。

API contract v0 也已冻结：

- `docs/reference/api/sales-workspace-kernel-v0-contract.md`

当前需要决策：是否进入 SQLite / Alembic persistence，是否开放 backend API implementation。

---

## 2. 决策

当前采用：

> **延后 persistence-backed backend API implementation；不进入 SQLite / Alembic；不开放正式 API route。**

同时明确：

- `in-memory / JSON fixture` 仅作为 prototype / contract validation 支撑。
- `in-memory / JSON fixture` 不是正式 persistence baseline。
- persistence-backed backend API implementation 继续 blocked。
- SQLite / Alembic migration 继续 blocked。
- 下一步应先补 contract fixture examples / state transition examples，而不是 route / DB。

---

## 3. 方案比较

## 3.1 in-memory / JSON fixture 先行

优点：

- 已经有实现基础。
- 适合继续验证 WorkspacePatch、ranking、projection、ContextPack 的状态变化。
- 适合补 API contract examples 和 state transition examples。
- 不会过早锁死数据库 schema。

缺点：

- 不是正式业务持久化。
- 不能支撑多进程、多设备或长期用户数据。
- 若直接暴露为 API persistence，容易给后续迁移制造隐性 contract。

结论：

> 可继续用于 prototype / contract validation，但不能作为正式 API persistence baseline。

## 3.2 SQLite / Alembic 先行

优点：

- 与 V1 当前 backend persistence baseline 一致。
- 可以较早验证 API 与数据库写入。
- 为 Android read-only view 提供可重复状态。

缺点：

- 目前会过早锁死 `SalesWorkspace`、`WorkspacePatch`、ranking board、projection、ContextPack 的 ORM / migration 形态。
- 当前还缺少 contract fixture examples 与 state transition examples。
- 容易把 backend-only v0 prototype 推进成 DB schema 任务。

结论：

> 当前过早，不进入 SQLite / Alembic。

## 3.3 延后 API / DB

优点：

- 避免在对象模型、API usage、Android read-only shape 未经过 examples 验证前进入 route 或 migration。
- 保持 Sales Workspace Kernel 的结构化边界清晰。
- 给后续 API implementation 和 DB schema 留出更稳定输入。

缺点：

- Android read-only view 和 Runtime integration 继续等待。
- 在 no-DB prototype 开放前，短期没有可调用 API。

结论：

> 当前采用。

---

## 4. 后续开放条件

开放 backend API implementation 前，至少需要完成：

1. 一组 contract fixture examples，覆盖：
   - workspace create。
   - patch apply。
   - ranking board。
   - Markdown projection。
   - ContextPack。
   - version conflict。
   - validation error。
2. 一组 state transition examples，说明：
   - 初始 workspace。
   - 产品理解写入。
   - 获客方向写入。
   - 第一轮 candidate / observation 写入。
   - 第二轮 candidate 超过第一轮候选。
3. 明确 API v0 首版是否接受无 DB mock store。
4. 如果仍需要真实持久化，再单独创建 DB schema / migration task。

---

## 5. 当前仍禁止

除非后续新 task 明确开放，否则不实现：

- persistence-backed FastAPI endpoint。
- SQLAlchemy ORM。
- Alembic migration。
- SQLite schema change。
- Postgres / pgvector。
- Android UI。
- Runtime / LangGraph integration。
- LLM / search provider。

---

## 6. 影响

- `task_v2_sales_workspace_backend_api_v0.md` 作为 persistence-backed API 继续 blocked。
- `task_v2_android_workspace_readonly_view.md` 继续 blocked。
- `task_v2_sales_workspace_runtime_patchdraft_integration.md` 继续 blocked。
- contract fixture examples / state transition examples 已在 addendum 前置任务中完成。

---

## 7. 2026-04-27 Addendum：允许 no-DB API prototype

contract fixture examples / state transition examples 已完成：

- `docs/reference/api/sales-workspace-kernel-v0-examples.md`
- `docs/reference/api/examples/sales_workspace_kernel_v0/`

因此允许实现一个最小 no-DB FastAPI prototype，用于验证 API contract 可调用性：

- 使用 app-local `InMemoryWorkspaceStore`。
- 不使用 SQLAlchemy ORM。
- 不新增 Alembic migration。
- 不承诺正式 persistence baseline。
- 不开放 Android UI、Runtime / LangGraph、LLM、search 或 CRM。

该 addendum 不推翻本 ADR 的 persistence decision：正式 persistence 仍未冻结，DB-backed API 仍需单独任务。

---

## 8. 2026-04-27 Addendum：允许 prototype JSON file store

no-DB FastAPI prototype 和 Android read-only workspace demo 已完成后，`ws_demo` 仍存在一个开发体验问题：backend 进程重启后 app-local in-memory state 会丢失，需要重复 seed。

因此允许补一个可选的 JSON file store prototype：

- 仅在显式设置 `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR` 时启用。
- 未设置该环境变量时，默认仍是 app-local `InMemoryWorkspaceStore`。
- JSON file store 只服务本地 demo continuity 与 contract smoke。
- 每个 workspace 保存为一个 JSON 文件，backend 可跨进程重启 lazy load。
- 不新增或扩展 API endpoint。
- 不使用 SQLAlchemy ORM。
- 不新增 Alembic migration。
- 不改变正式 persistence baseline。
- 不开放 Android write path、Runtime / LangGraph、LLM、search 或 CRM。

该 addendum 不推翻本 ADR 的 persistence decision：正式 DB-backed API、SQLite / Alembic 或 Postgres 仍需单独任务和决策。
