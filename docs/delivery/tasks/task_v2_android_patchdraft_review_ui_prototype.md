# V2 Android PatchDraft Review UI Prototype

状态：done

更新时间：2026-04-27

## 1. Objective

在 PR #11 的 PatchDraft review gate backend prototype 合入后，为 Android Workspace 页面补一个最小人工审阅 UI。

目标是让 Android 作为控制入口完成：

```text
读取 workspace
-> 生成 Runtime PatchDraft preview
-> 人工查看 preview ranking
-> 显式 apply 已审阅 draft
-> 刷新 workspace / ranking / projection / ContextPack
```

## 2. Scope

- 扩展现有 Android `SalesWorkspaceBackendClient`。
- 扩展现有 Android DTO / JSON parser。
- 在现有 Workspace 页面加入 PatchDraft Review Gate 区块。
- Android preview 使用当前 loaded workspace version。
- Android apply 原样回传 backend preview response 中的 `patch_draft` raw JSON。
- apply 成功后刷新当前 workspace snapshot。
- 同步入口文档与 handoff。

## 3. Out Of Scope

- 不新增 backend endpoint。
- 不改 `WorkspacePatch` contract。
- 不让 Android 构造正式 workspace object。
- 不改 Android Manifest、导航结构、Gradle、Room、Retrofit、Hilt。
- 不接真实 LLM。
- 不实现正式 LangGraph graph。
- 不接 search / contact / CRM / auto outreach。
- 不写 SQLAlchemy model、Alembic migration、SQLite schema 或 Postgres persistence。

## 4. Implementation Notes

- Preview endpoint:
  - `POST /sales-workspaces/{workspace_id}/runtime/patch-drafts/prototype/preview`
- Apply endpoint:
  - `POST /sales-workspaces/{workspace_id}/runtime/patch-drafts/prototype/apply`
- Android 保存 `patch_draft.rawJson`，apply 时放入 `{ "patch_draft": ... }` 回传。
- Version conflict 由 backend 返回 `409 workspace_version_conflict`，Android 只展示错误并要求重新刷新 / preview。

## 5. Validation Criteria

- Backend baseline tests pass.
- Android `:app:assembleDebug` pass.
- Android `:app:lintDebug` pass.
- Backend + seed smoke 可以验证 preview 不 mutate。
- 若设备可用，Android Workspace 页面可以完成 preview / apply demo。
- 若设备不可用，handoff 明确记录未做 device-level 验证。

## 6. Actual Validation

- `PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py -q`
- `PYTHONPATH=$PWD /home/yulin/projects/OpenClawAndroidNativeEntry/backend/.venv/bin/python -m pytest backend/tests -q`
- `./gradlew :app:assembleDebug`
- `./gradlew :app:lintDebug`
- Backend smoke with JSON store on `127.0.0.1:8013`:
  - seed `ws_demo` to version 3
  - preview returned `cand_runtime_001` as preview rank #1
  - preview did not mutate workspace; workspace stayed version 3
  - apply changed workspace to version 4
  - ranking board and ContextPack returned `cand_runtime_001` first
- Device smoke:
  - `adb devices` detected `f3b59f04`
  - `adb reverse tcp:8013 tcp:8013`
  - installed and launched `app-debug.apk`
  - Workspace page showed version 3 before apply
  - preview UI showed `draft_runtime_v4`, `patch_runtime_v4`, `would_mutate=false`, and `Runtime Draft Co`
  - apply refreshed Workspace page to version 4 and showed `Runtime Draft Co` ranked first
