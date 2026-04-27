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

---

## 9. 2026-04-27 Addendum：允许定义 Draft Review contract

V2 Sales Workspace prototype demo 已完成并通过 clean demo verification：

- Runtime 生成 deterministic `WorkspacePatchDraft`。
- Android 预览并显式 apply。
- Backend materialize `WorkspacePatch` 后由 Sales Workspace Kernel 正式写回。
- apply 后 workspace version 从 3 变为 4，`cand_runtime_001` 排名第一。

当前 prototype 的薄弱点是：previewed draft 只存在于 Android UI state / request body 中，没有 backend-managed review object。

因此允许定义 Draft persistence / review history contract：

- 新增 contract 文档：`docs/reference/api/sales-workspace-draft-review-contract.md`。
- 定义 `WorkspacePatchDraftReview` 作为 backend-managed review object 语义。
- 定义 draft lifecycle：`previewed`、`reviewed`、`applied`、`rejected`、`expired`。
- 明确 Android 未来推荐提交 `draft_review_id` 执行 apply。
- 明确 Runtime / Product Sales Agent execution layer 仍只产出 `WorkspacePatchDraft`。
- 明确 Sales Workspace Kernel 仍是 formal workspace writeback owner。

该 addendum 不推翻本 ADR 的 persistence decision：

- 不实现 backend route。
- 不新增 SQLAlchemy ORM。
- 不新增 Alembic migration。
- 不改变 SQLite / Postgres / production persistence baseline。
- JSON file store 仍只允许作为 prototype demo continuity，不是正式 persistence baseline。

若后续要实现 draft review object，应先刷新 persistence decision 或创建单独 persistence task。

---

## 10. 2026-04-27 Addendum：允许 Draft Review routes prototype

Draft review contract 已完成后，用户明确开放一个单独的 prototype implementation task：

- `docs/delivery/tasks/task_v2_sales_workspace_draft_review_routes_prototype.md`

因此允许实现 backend-managed Draft Review routes prototype：

- `POST /sales-workspaces/{workspace_id}/draft-reviews`
- `GET /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}`
- `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/review`
- `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/apply`
- `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/reject`

允许范围：

- 使用 app-local in-memory draft review store。
- 在显式设置 `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR` 时，使用 JSON file-backed draft review store 支撑本地 prototype continuity。
- 后端负责 materialize `WorkspacePatch` 并通过 Sales Workspace Kernel apply。
- Runtime / Product Sales Agent execution layer 仍只产出 `WorkspacePatchDraft`。

该 addendum 不推翻本 ADR 的 persistence decision：

- 不新增 SQLAlchemy ORM。
- 不新增 Alembic migration。
- 不改变 SQLite / Postgres / production persistence baseline。
- 不开放正式 LangGraph graph。
- 不接真实 LLM、search、contact 或 CRM。
- 不新增 Android UI 或 Android workspace write path。

---

## 11. 2026-04-27 Addendum：Post Review-ID Flow persistence decision refresh

Android Draft Review ID flow prototype 已完成后，V2 prototype 已打通当前核心人工审阅写回闭环：

```text
Android 人工审阅入口
-> backend-managed WorkspacePatchDraftReview
-> explicit accept / reject
-> apply by draft_review_id
-> Sales Workspace Kernel formal writeback
-> ranking / projection / ContextPack refresh
```

因此本 ADR 需要刷新后续 persistence 判断。

当前结论：

- JSON file store 继续定位为 prototype continuity，不升级为正式 persistence baseline。
- SQLite / Alembic 可作为本地过渡方案继续保留讨论，但不作为下一阶段推荐默认。
- 如果 V2 继续向 MVP 推进，下一步应进入正式 persistence baseline design，并优先评估 Postgres / Alembic。
- 当前仍不开放 DB migration、SQLAlchemy model、backend route 变更、Android UI 扩展、正式 LangGraph、真实 LLM、search、contact 或 CRM。

方案比较：

- JSON file store：
  - 优点是最快、已可支撑本地 demo 复现和 backend 重启 continuity。
  - 缺点是不能可靠支撑并发、审阅历史、数据一致性、多用户、权限或长期业务数据。
  - 结论是继续作为 prototype store，不作为 MVP persistence baseline。
- SQLite / Alembic：
  - 优点是本地简单，且与 V1 当前 SQLite baseline 接近。
  - 缺点是如果 V2 目标是服务化、多用户和长期 workspace 记录，SQLite 可能只是短期过渡并带来二次迁移成本。
  - 结论是可以作为备选，但不推荐作为默认下一步。
- Postgres / Alembic：
  - 优点是更接近正式服务端 persistence baseline，适合 workspace、draft review lifecycle、audit trail、未来多用户和后续 runtime integration。
  - 缺点是引入环境、部署、测试和 migration discipline 成本。
  - 结论是下一阶段 design task 的优先评估方向。

下一步只开放：

- `docs/delivery/tasks/task_v2_sales_workspace_persistence_baseline_design.md`

继续 blocked / planned：

- Draft Review persistence schema implementation。
- backend DB migration。
- persistence-backed Sales Workspace API。
- formal Runtime / LangGraph integration。
- Android review history / broader UX expansion。
