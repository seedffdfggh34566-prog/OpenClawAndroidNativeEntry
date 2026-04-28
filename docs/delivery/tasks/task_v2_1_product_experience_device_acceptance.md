# Task: V2.1 Product Experience Device Acceptance

状态：done

更新时间：2026-04-27

## Objective

在真实 Android 设备上验收 V2.1 product experience prototype，确认 Android 控制入口可以展示并操作：

- empty workspace
- clarifying questions
- product profile Draft Review
- product apply 后的 `ProductProfileRevision`
- lead direction Draft Review
- direction apply 后的 active `LeadDirectionVersion`
- ContextPack / Markdown projection
- workspace explanation answer

## Scope

- 使用真机 `f3b59f04 device`。
- 使用现有 backend routes，不新增 API。
- 使用 Postgres / Alembic backend 和 `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND=postgres` 复验当前 workspace。
- 使用现有 Workspace 页面，不改导航、不改 Manifest。
- 使用 `ws_demo` 空 workspace 起步。
- 通过 Android 发起 chat-first turn、Draft Review accept / apply。

## Out Of Scope

- 不接真实 LLM。
- 不接正式 LangGraph。
- 不做 V2.2 search / ContactPoint / CRM。
- 不实现 Android 自动创建 workspace。
- 不验证生产级多用户、权限或发布流程。

## Device Evidence

证据目录：

`docs/delivery/evidence/v2_1_product_experience_device_acceptance/`

截图：

- `02_workspace_empty_version0.png`：空 workspace version 0，产品画像 / 获客方向 / 候选排序为空。
- `04_clarifying_questions_visible.png`：不足输入返回 5 个中文追问，不生成 patch draft。
- `05_product_draft_review_previewed.png`：产品理解 turn 生成 Draft Review。
- `06_product_applied_version1.png`：产品理解 apply 后 workspace version 1，`FactoryOps AI` 可见。
- `07_direction_draft_review_previewed.png`：获客方向 turn 生成 Draft Review。
- `09_direction_applied_details.png`：获客方向 apply 后 active direction 可见，包含制造业、华东、中小企业、排除教育。
- `10_context_pack_projection.png`：ContextPack 与 Markdown projection 可见。
- `12_workspace_explanation_visible.png`：解释型回答基于当前 product / direction / ContextPack source versions。
- `13_postgres_store_workspace_version2.png`：切换到 Postgres store backend 后，Android 仍可读取 version 2 workspace / explanation 状态。

## Outcome

真机端到端验收通过。

已验证链路：

```text
chat-first input
-> ConversationMessage
-> AgentRun
-> ContextPack
-> WorkspacePatchDraft
-> Draft Review
-> explicit accept/apply
-> WorkspacePatch
-> ProductProfileRevision / LeadDirectionVersion
-> Android visible
```

同时验证：

- `clarifying_question` turn 不生成 Draft Review，不 mutate workspace。
- `workspace_question` turn 返回解释型回答，不 mutate workspace。
- apply 后 workspace version 从 `0 -> 1 -> 2` 连续递增。
- projection / ContextPack 在 version 2 可读。

## Validation

```bash
PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
PYTHONPATH=$PWD backend/.venv/bin/alembic -c alembic.ini upgrade head
docker compose -f compose.postgres.yml up -d
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev PYTHONPATH=$PWD backend/.venv/bin/alembic -c alembic.ini upgrade head
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND=postgres PYTHONPATH=$PWD backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
curl http://127.0.0.1:8013/health
adb devices
adb reverse tcp:8013 tcp:8013
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.openclaw.android.nativeentry/.MainActivity
adb exec-out screencap -p
```

Backend endpoint confirmation:

```bash
curl http://127.0.0.1:8013/sales-workspaces/ws_demo
curl -X POST http://127.0.0.1:8013/sales-workspaces/ws_demo/context-packs -H 'Content-Type: application/json' -d '{}'
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/projection
```

## Notes

- Android 自动化中文输入使用设备已安装的 `com.android.adbkeyboard/.AdbIME`，验收结束后已恢复原输入法 `com.baidu.input_oppo/.ImeService`。
- 本验收证明 deterministic V2.1 product experience prototype，不证明真实 LLM / LangGraph / search 能力。
