# Task: V2 Android Draft Review ID Flow Prototype

状态：done

更新时间：2026-04-27

## Objective

让 Android Workspace 页面从 raw `patch_draft` 回传 apply，切换为 backend-managed `draft_review_id` flow。

目标流程：

```text
读取 workspace
-> Runtime prototype 生成 PatchDraft preview
-> backend 创建 WorkspacePatchDraftReview
-> Android 展示 draft_review_id / status / preview
-> Android 显式 accept 或 reject
-> Android 按 draft_review_id apply
-> backend Sales Workspace Kernel 正式写回
-> Android 刷新 workspace snapshot
```

## Scope

- 扩展 Android `SalesWorkspaceBackendClient`，调用 Draft Review routes。
- 扩展 Android DTO / JSON parser，解析 `draft_review`、preview、review、apply_result。
- 更新 Workspace 页面，展示 Draft Review ID、status、review decision、apply result。
- Apply 只使用 `draft_review_id`，不再调用 raw `patch_draft` apply endpoint。
- Apply 成功后刷新 workspace / ranking / projection / ContextPack。
- 同步入口文档与 handoff。

## Out Of Scope

- 不新增或修改 backend route。
- 不写 SQLAlchemy model、Alembic migration、SQLite schema 或 Postgres persistence。
- 不改 Android Manifest、Gradle、导航结构、Room、Retrofit、Hilt。
- 不让 Android 构造正式 `WorkspacePatch` 或正式 workspace object。
- 不接正式 LangGraph graph。
- 不接真实 LLM / search / contact / CRM。
- 不实现 Android 自由编辑 workspace。

## Result

已完成：

- Android client 新增 Draft Review create / review / reject / apply by id 调用。
- Android parser 新增 `WorkspacePatchDraftReview` response 解析。
- Workspace 页面改为显示 backend-managed Draft Review 状态。
- Android apply 改为调用 `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/apply`。
- 删除 Android 对 `/runtime/patch-drafts/prototype/apply` 的直接调用。

## Validation Criteria

- Backend draft review tests pass。
- Android `:app:assembleDebug` pass。
- Android `:app:lintDebug` pass。
- 如设备可用，验证 Workspace 页面可以完成 create review -> accept -> apply by id。
- 如设备不可用，handoff 明确记录未做 device-level 验证。

## Actual Validation

- `PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py backend/tests/test_sales_workspace_draft_reviews_api.py -q`
  - Result: `31 passed`
- `PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests -q`
  - Result: `78 passed`
- `./gradlew :app:assembleDebug`
  - Result: passed
- `./gradlew :app:lintDebug`
  - Result: passed
- Backend smoke with JSON store:
  - started local backend on `127.0.0.1:8013`
  - seeded `ws_demo` to workspace version `3`
  - verified runtime preview -> create Draft Review -> accept -> apply by `draft_review_id`
  - verified apply result moved workspace to version `4` and ranked `cand_runtime_001` first
  - verified projection and ContextPack remain readable after apply
- Device smoke:
  - `adb devices` detected `f3b59f04`
  - `adb reverse tcp:8013 tcp:8013` succeeded
  - `adb install -r app/build/outputs/apk/debug/app-debug.apk` succeeded
  - launched `com.openclaw.android.nativeentry/.MainActivity`; process and resumed Activity were visible
  - full manual Workspace screen click-through was not claimed; API-level flow was verified separately
