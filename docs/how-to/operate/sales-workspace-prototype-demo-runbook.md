# Sales Workspace Prototype Demo Runbook

更新时间：2026-04-27

## 1. Purpose

本 runbook 用于复现当前 V2 Sales Workspace prototype demo。

目标闭环：

```text
backend JSON store
-> seed ws_demo
-> Android Workspace 页面读取 version 3
-> Runtime PatchDraft preview
-> preview 不改变 workspace
-> Android apply 已审阅 draft
-> backend kernel 写入正式 workspace
-> Android 刷新后看到 version 4 和 Runtime Draft Co 排名第一
```

本 runbook 面向开发者和 Dev Agent，不是产品用户文档。

## 2. Scope

当前 demo 覆盖：

- Sales Workspace Kernel structured state
- no-DB FastAPI prototype
- optional JSON file store prototype
- deterministic Runtime PatchDraft prototype
- PatchDraft preview / explicit apply review gate
- Android Workspace read / review / apply flow

当前 demo 不覆盖：

- 真实 LLM
- 正式 LangGraph graph
- search / contact / CRM
- production persistence / DB migration
- multi-user / auth / tenant
- Android 自由编辑 workspace object

## 3. Preconditions

- 在 `jianglab` 上运行。
- 已安装 backend venv。
- Android debug build 可用。
- 如需真机 demo，`adb devices` 能看到设备。
- 本机端口 `8013` 未被其他 backend 占用。

## 4. Start Backend

使用 JSON file store，便于 demo 期间 backend 重启后保留 workspace：

```bash
rm -rf /tmp/openclaw_sales_workspace_demo_store
mkdir -p /tmp/openclaw_sales_workspace_demo_store

OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR=/tmp/openclaw_sales_workspace_demo_store \
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

## 5. Seed Demo Workspace

在另一个 shell 执行：

```bash
python3 scripts/seed_sales_workspace_demo.py \
  --base-url http://127.0.0.1:8013 \
  --workspace-id ws_demo
```

期望输出包含：

```text
workspace version is now 3
top candidate: cand_d (D Company) score=230
context pack: ctx_ws_demo_v3
```

## 6. Backend Preview / Apply Smoke

确认 apply 前 ranking：

```bash
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/ranking-board/current
```

期望：

- `workspace_version` 为 `3`
- 第一名为 `cand_d`

生成 preview：

```bash
curl -X POST \
  http://127.0.0.1:8013/sales-workspaces/ws_demo/runtime/patch-drafts/prototype/preview \
  -H 'Content-Type: application/json' \
  -d '{"base_workspace_version":3,"instruction":"add one deterministic runtime candidate"}'
```

期望：

- `patch_draft.id` 为 `draft_runtime_v4`
- `patch.id` 为 `patch_runtime_v4`
- `preview_workspace_version` 为 `4`
- `would_mutate` 为 `false`
- preview 第一名为 `cand_runtime_001`

确认 preview 没有改变 workspace：

```bash
curl http://127.0.0.1:8013/sales-workspaces/ws_demo
```

期望：

- `workspace.workspace_version` 仍为 `3`

应用已审阅 draft 时，使用 preview response 中的 `patch_draft` 原样回传：

```json
{
  "patch_draft": {
    "...": "previewed WorkspacePatchDraft"
  }
}
```

应用后确认：

```bash
curl http://127.0.0.1:8013/sales-workspaces/ws_demo/ranking-board/current
```

期望：

- `workspace_version` 为 `4`
- 第一名为 `cand_runtime_001`

## 7. Android Device Demo

构建：

```bash
./gradlew :app:assembleDebug
```

连接 backend：

```bash
adb devices
adb reverse tcp:8013 tcp:8013
```

安装并启动：

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.openclaw.android.nativeentry/.MainActivity
```

人工检查：

1. 打开底部 `Workspace` tab。
2. 初始页面显示 `Version：3`。
3. 候选排序中 `D Company` / `cand_d` 为第一。
4. 滚动到 `PatchDraft Review Gate`。
5. 点击 `生成 PatchDraft 预览`。
6. 期望看到：
   - `Draft：draft_runtime_v4`
   - `Patch：patch_runtime_v4`
   - `Preview version：4；would_mutate=false`
   - `预览第一：#1 Runtime Draft Co`
7. 在 backend 侧确认 workspace 仍为 version 3。
8. 点击 `应用已审阅 Draft`。
9. 页面刷新后显示 `Version：4`。
10. ranking / ContextPack 中 `Runtime Draft Co` / `cand_runtime_001` 为第一。

## 8. Evidence To Record

handoff 或 PR description 应记录：

- backend health check result
- seed output
- preview response summary
- apply response summary
- `adb devices` 是否有设备
- 是否执行 `adb reverse`
- 是否安装并启动 Android app
- Android 页面是否看到 version 3 -> version 4
- Android 页面是否看到 `Runtime Draft Co` 排名第一

## 9. Common Failures

### Android cannot connect to backend

检查：

```bash
curl http://127.0.0.1:8013/health
adb reverse tcp:8013 tcp:8013
```

### Preview returns version conflict

说明 Android 或 curl 使用了旧的 `base_workspace_version`。

处理：

1. 重新读取 workspace。
2. 使用当前 `workspace_version` 重新 preview。

### Seed says workspace already exists

如果需要干净 demo，停止 backend 后删除 store 目录：

```bash
rm -rf /tmp/openclaw_sales_workspace_demo_store
```

然后重新启动 backend 并 seed。

