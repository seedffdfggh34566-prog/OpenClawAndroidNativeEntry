# Task：V2 Android workspace read-only view

更新时间：2026-04-27

## 1. 任务定位

- 任务名称：V2 Android workspace read-only view
- 建议路径：`docs/delivery/tasks/task_v2_android_workspace_readonly_view.md`
- 当前状态：`planned`
- 优先级：P1

---

## 2. 任务目标

在 backend API v0 可用后，让 Android 以 read-only 方式查看 Sales Workspace、当前 ranking、Markdown projection 或 ContextPack 摘要。

---

## 3. Blocked By

- `task_v2_sales_workspace_backend_api_v0.md`

---

## 4. Out of Scope Until Unblocked

- 大规模聊天 UI 改造。
- Android 直接写 workspace 主存。
- Android 本地替代 backend truth。
- Runtime / LLM / search 接入。

---

## 5. 验收方向

正式开放后至少应包含：

- Android read-only UI 或 debug view。
- backend API smoke path。
- 最小设备或 emulator 验证。
- 不引入 workspace write path。
