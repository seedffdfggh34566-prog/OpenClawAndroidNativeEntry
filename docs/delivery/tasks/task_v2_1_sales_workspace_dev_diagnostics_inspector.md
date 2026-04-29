# Task: V2.1 Sales Workspace Dev Diagnostics Inspector

更新时间：2026-04-28

## 1. 任务定位

- 任务名称：V2.1 Sales Workspace Dev Diagnostics Inspector
- 当前状态：`done`
- 优先级：P1
- 任务类型：`delivery`
- Authorization source：human instruction on 2026-04-28，新增 dev-only read-only Sales Workspace diagnostics inspector。
- 完成后是否允许自动进入下游任务：`no`

## 2. 目标

新增一个仅供开发与调试使用的只读 Sales Workspace diagnostics inspector，让开发者能查看 Sales Workspace 当前沉淀状态、conversation / trace / draft review 关联和基础运行诊断，帮助定位 Android chat surface 与 backend 状态不同步问题。

该任务只提供开发期可视化 / 诊断入口，不改变正式产品体验、正式 workspace 写入路径或 milestone 状态。

## 3. Scope

In scope：

- 新增 dev-only、read-only diagnostics inspector。
- 允许在 backend 增加只读 diagnostics route / response model / service helper。
- 允许读取现有 Sales Workspace、conversation thread、message、agent turn trace、context pack、draft review 和 workspace version 信息。
- 允许返回 developer-facing JSON 或轻量 inspector payload，用于人工排障。
- 允许增加最小 pytest 覆盖，验证 read-only、missing workspace、thread / trace / draft review 关联和不写入 workspace。
- 允许补充 Android / backend 手动 smoke 所需的最小调试说明，前提是仅写入本 task 的 outcome / validation。

Out of scope：

- 正式用户可见产品 UI。
- Android production feature、Android review history、multi-workspace productization。
- 新增写入 API、workspace mutation、draft apply/writeback 行为变化。
- DB schema / Alembic migration。
- auth / tenant / permissions model。
- CRM、V2.2 search / evidence / ContactPoint。
- formal LangGraph、streaming、abort / inject。
- milestone completion claim、PRD / roadmap / project status 更新。
- secrets、token、Authorization header 或 `.env` 内容读取 / 输出。

## 4. Expected files

Likely files, subject to implementation agent review：

- `backend/api/sales_workspace.py`
- `backend/sales_workspace/*`
- `backend/tests/*sales_workspace*`
- this task file

Do not edit product PRD、roadmap、project status、README、milestone review，unless a later human instruction explicitly expands scope.

## 5. Validation

Minimum validation before marking done：

- Run the lightest targeted backend pytest covering the diagnostics inspector.
- Confirm diagnostics route / helper is read-only by asserting workspace version and persisted objects do not change.
- Confirm missing / unknown workspace returns a controlled error or empty diagnostic response as designed.
- Confirm no secret values, `.env` contents, Authorization headers, or provider credentials are exposed.

Optional validation if implementation touches Android-only manual debug access：

- `./gradlew :app:assembleDebug`
- Device smoke showing the production chat path still opens.

## 6. Stop conditions

Stop and return to planning / human decision if the implementation would require:

- DB schema change or migration.
- Any write path, mutation, apply, rollback, repair, or admin operation.
- Production user-facing UI or product navigation change.
- Auth / tenant / permissions model decisions.
- V2.2 search / evidence / ContactPoint implementation.
- formal LangGraph or runtime architecture change.
- Reading, printing, copying, or documenting secret values.
- Updating PRD、roadmap、project status、README、milestone review，or claiming milestone completion.

## 7. Execution Outcome

状态：`done`。

完成内容：

- 新增 dev-only Sales Workspace diagnostics 开关：`OPENCLAW_BACKEND_DEV_SALES_WORKSPACE_DIAGNOSTICS_ENABLED=true`。
- 新增只读 dev routes：
  - `GET /dev/sales-workspace-inspector`
  - `GET /dev/sales-workspaces`
  - `GET /dev/sales-workspaces/{workspace_id}/diagnostics`
- 新增轻量 HTML inspector，可查看 workspace summary、object counts、formal objects、threads / recent messages、agent runs、context packs、draft reviews、projection 和 raw diagnostics JSON。
- Store 层补齐只读 list 方法，覆盖 in-memory、JSON file 和 Postgres-backed stores。
- Diagnostics 读取 thread list 时使用无副作用路径，不创建默认 thread。
- 未新增正式 `/sales-workspaces/*` product endpoint，未新增 schema / migration，未改变 workspace write path。

## 8. Validation

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_diagnostics_inspector.py -q` passed：`3 passed`。
- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_diagnostics_inspector.py backend/tests/test_dev_llm_inspector.py -q` passed：`8 passed`。
- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q` passed：`19 passed, 1 skipped`。
- `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_diag_verify.db backend/.venv/bin/alembic upgrade head` passed。
- Temporary backend smoke on `127.0.0.1:8014` passed:
  - `GET /health` returned `{"status":"ok"}`。
  - `GET /dev/sales-workspace-inspector` returned HTTP 200 HTML。
  - `GET /dev/sales-workspaces` returned HTTP 200 JSON。
- `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` was absent, so optional Postgres diagnostics tests were not run.

## 9. Known Limits

- Diagnostics inspector is local dev-only and disabled by default.
- JSON store can list persisted workspaces and draft reviews across process restart; chat trace remains process-local unless Postgres-backed chat trace store is used.
- The inspector is read-only; it does not provide repair, rollback, apply, review, writeback, auth, tenant, CRM, V2.2 search/contact, or formal LangGraph capabilities.
- This task is backend diagnostics evidence only and does not declare V2.1 milestone completion.

## 10. Handoff

Detailed handoff：`docs/delivery/handoffs/handoff_2026_04_28_v2_1_sales_workspace_dev_diagnostics_inspector.md`。
