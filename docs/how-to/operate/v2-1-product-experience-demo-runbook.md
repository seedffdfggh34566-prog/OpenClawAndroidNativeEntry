# V2.1 Product Experience Demo Runbook

更新时间：2026-04-28

## 1. Purpose

本 runbook 用于复现 V2.1 product experience：

```text
Postgres backend
-> Android Workspace
-> 用户 chat-first 输入产品理解
-> backend 创建 ConversationMessage / AgentRun / ContextPack / Draft Review
-> 人工 accept / apply
-> Sales Workspace Kernel 写入 ProductProfileRevision
-> 用户 chat-first 输入获客方向
-> 人工 accept / apply
-> Sales Workspace Kernel 写入 LeadDirectionVersion
-> Android 刷新后看到产品理解和获客方向进入 workspace
```

本 runbook 面向开发者和 Dev Agent，不是产品用户文档。

## 2. Scope

当前 demo 覆盖：

- chat-first 产品理解输入。
- chat-first 获客方向输入。
- `ConversationMessage` trace。
- `AgentRun(run_type=sales_agent_turn)` trace。
- `ContextPack(task_type=sales_agent_turn)` snapshot。
- backend-managed Draft Review。
- Sales Workspace Kernel formal writeback。
- Android Workspace 页面的人工作业入口。

当前 demo 不覆盖：

- 真实 LLM。
- 正式 LangGraph graph。
- search / ContactPoint / CRM。
- 自动触达。
- Android 自由编辑 workspace object。
- production deployment / auth / tenant permission。

## 3. Start Postgres Backend

建议先固定本地 demo 环境变量，后续命令可复用同一条连接串：

```bash
export OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev
export OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND=postgres
export OPENCLAW_BACKEND_DEMO_BASE_URL=http://127.0.0.1:8013
```

```bash
docker compose -f compose.postgres.yml up -d
docker exec openclaw-postgres pg_isready -U openclaw -d openclaw_dev
```

升级 schema：

```bash
backend/.venv/bin/alembic -c alembic.ini upgrade head
```

启动 backend：

```bash
PYTHONPATH=$PWD \
backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
```

健康检查：

```bash
curl http://127.0.0.1:8013/health
```

期望：

```json
{"status":"ok"}
```

## 4. Seed Workspace

### 4.1 Clean workspace choice

`POST /sales-workspaces` is intentionally non-destructive. If `ws_demo` already exists and a clean flow is required, use one of these options:

- choose a new workspace id such as `ws_demo_20260428_001`;
- or reset the local Postgres demo environment before seeding.

For a full local reset, only use this on disposable development data:

```bash
docker compose -f compose.postgres.yml down -v
docker compose -f compose.postgres.yml up -d
docker exec openclaw-postgres pg_isready -U openclaw -d openclaw_dev
backend/.venv/bin/alembic -c alembic.ini upgrade head
```

### 4.2 Seed or create

如果需要从已有候选排序 demo 起步：

```bash
python3 scripts/seed_sales_workspace_demo.py \
  --base-url "$OPENCLAW_BACKEND_DEMO_BASE_URL" \
  --workspace-id ws_demo
```

如果只验证 V2.1 chat-first 产品体验，可以只创建空 workspace：

```bash
curl -X POST http://127.0.0.1:8013/sales-workspaces \
  -H 'Content-Type: application/json' \
  -d '{"workspace_id":"ws_demo","name":"FactoryOps AI Workspace","goal":"Build chat-first V2.1 product experience."}'
```

创建后确认 workspace 可读：

```bash
curl http://127.0.0.1:8013/sales-workspaces/ws_demo
```

## 5. Backend Chat-first Smoke

每轮 smoke 建议使用空 workspace，或者确认当前 `workspace_version` 与请求中的 `base_workspace_version` 一致。

### 5.1 Product understanding

Create user message：

```bash
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/messages \
  -H 'Content-Type: application/json' \
  -d '{"message_type":"product_profile_update","content":"我们做 FactoryOps AI，帮助 100 到 500 人的制造企业协同排产、库存和 ERP。"}'
```

Run Product Sales Agent turn：

```bash
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/agent-runs/sales-agent-turns \
  -H 'Content-Type: application/json' \
  -d '{"message_id":"msg_user_001","base_workspace_version":0,"instruction":"update product profile from chat"}'
```

期望：

- `agent_run.status = succeeded`
- `context_pack.task_type = sales_agent_turn`
- `draft_review.status = previewed`
- `patch_draft.operations[0].type = upsert_product_profile_revision`
- workspace version 仍为 `0`

Accept and apply：

```bash
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/draft-reviews/draft_review_sales_turn_product_profile_update_v1/review \
  -H 'Content-Type: application/json' \
  -d '{"decision":"accept","reviewed_by":"android_demo_user","client":"android"}'

curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/draft-reviews/draft_review_sales_turn_product_profile_update_v1/apply \
  -H 'Content-Type: application/json' \
  -d '{"requested_by":"android_demo_user"}'
```

期望 workspace version 变为 `1`，`current_product_profile_revision_id = ppr_chat_v1`。

确认写入结果：

```bash
curl http://127.0.0.1:8013/sales-workspaces/ws_demo
```

### 5.2 Lead direction

Create user message：

```bash
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/messages \
  -H 'Content-Type: application/json' \
  -d '{"message_type":"lead_direction_update","content":"先找华东地区 100 到 500 人、有 ERP 但排产库存协同弱的制造企业。教育和超大型集团先排除。"}'
```

Run Product Sales Agent turn：

```bash
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/agent-runs/sales-agent-turns \
  -H 'Content-Type: application/json' \
  -d '{"message_id":"msg_user_003","base_workspace_version":1,"instruction":"update lead direction from chat"}'
```

期望：

- `draft_review.status = previewed`
- `patch_draft.operations` 包含 `upsert_lead_direction_version` 和 `set_active_lead_direction`
- workspace version 仍为 `1`

Accept and apply：

```bash
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/draft-reviews/draft_review_sales_turn_lead_direction_update_v2/review \
  -H 'Content-Type: application/json' \
  -d '{"decision":"accept","reviewed_by":"android_demo_user","client":"android"}'

curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/draft-reviews/draft_review_sales_turn_lead_direction_update_v2/apply \
  -H 'Content-Type: application/json' \
  -d '{"requested_by":"android_demo_user"}'
```

期望 workspace version 变为 `2`，`current_lead_direction_version_id = dir_chat_v2`。

确认 trace 可读：

```bash
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/messages
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/agent-runs/run_sales_turn_direction_001
```

## 6. Android Demo

构建：

```bash
./gradlew :app:assembleDebug
```

连接 backend：

```bash
adb devices
adb reverse tcp:8013 tcp:8013
adb reverse --list | grep 'tcp:8013'
```

安装并启动：

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.openclaw.android.nativeentry/.MainActivity
```

人工检查：

1. 打开底部 `Workspace` tab。
2. 点击 `刷新工作区`。如果 workspace 不存在，先按 P2 之后的 Android onboarding 创建默认 workspace。
3. 在 `Chat-first Workspace Turn` 输入产品理解。
4. 选择 `产品理解`，点击 `提交 chat-first turn`。
5. 确认页面显示 `AgentRun`、assistant summary 和 Draft Review ID。
6. 点击 `接受 Draft Review`。
7. 点击 `按 Review ID 应用`。
8. 刷新后确认当前产品理解已出现。
9. 输入获客方向，选择 `获客方向`，重复 accept / apply。
10. 刷新后确认当前获客方向已出现。

## 7. Validation Commands

```bash
backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
./gradlew :app:assembleDebug
./gradlew :app:lintDebug
git diff --check
```

如果只验证 runbook 文档改动，最低验证为：

```bash
git diff --check
```

## 8. Expected Evidence

handoff 或 PR description 应记录：

- backend health check result。
- product chat turn 生成 `draft_review_sales_turn_product_profile_update_v1`。
- product apply 后 workspace version `0 -> 1`。
- lead direction chat turn 生成 `draft_review_sales_turn_lead_direction_update_v2`。
- lead direction apply 后 workspace version `1 -> 2`。
- Android build / lint 是否通过。
- `adb devices` 是否有设备。
- 是否完成手动 Android UI flow。

## 9. Troubleshooting

- `workspace_already_exists`：当前 workspace 已存在。使用新 workspace id，或只在 disposable dev data 上执行 `docker compose -f compose.postgres.yml down -v` 后重建。
- `workspace_version_conflict`：请求中的 `base_workspace_version` 与当前 workspace 不一致。先 `GET /sales-workspaces/ws_demo`，再用返回的 `workspace_version` 重跑 turn。
- Android 显示连接失败：确认 backend 监听 `127.0.0.1:8013`，并确认 `adb reverse tcp:8013 tcp:8013` 已生效。
- Draft Review 无法 apply：确认 review status 是 `reviewed`，且 `base_workspace_version` 仍等于当前 workspace version。
- Postgres tests skipped：确认 `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` 已设置，并且 Alembic 已升级到 head。
