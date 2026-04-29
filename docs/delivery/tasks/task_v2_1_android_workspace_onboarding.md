# Task: V2.1 Android Workspace Onboarding

更新时间：2026-04-28

## 1. 任务定位

- 任务名称：V2.1 Android Workspace Onboarding
- 建议路径：`docs/delivery/tasks/task_v2_1_android_workspace_onboarding.md`
- 当前状态：`done`
- 优先级：P1
- 任务类型：`delivery`
- 是否属于 delivery package：`yes`
- 所属 package：`V2.1 Implementation Continuation`

---

## 2. 任务目标

让 Android Workspace 页面在后端尚未存在 `ws_demo` 时，可以通过已有 `POST /sales-workspaces` 创建默认空 workspace，并在创建后自动刷新当前 workspace。

---

## 3. 范围

In Scope：

- Android backend client 新增 `createWorkspace` 方法。
- Android Workspace 页面新增默认 `ws_demo` 创建入口。
- `OpenClawApp` / `OpenClawNavHost` 增加最小状态和回调传递。

Out of Scope：

- 多 workspace 管理。
- 账号、租户、权限。
- 新 backend endpoint。
- backend schema / migration。
- V2.2 search / ContactPoint。

---

## 4. 实际产出

- Android 可创建默认 `ws_demo` workspace。
- 创建成功后自动读取 `SalesWorkspaceReadOnlySnapshot`。
- UI 在已加载 workspace 时禁用创建按钮，避免误触发 409。

---

## 5. 已做验证

- `./gradlew :app:assembleDebug`

---

## 6. 实际结果说明

本任务没有新增 backend API；Android 只复用已有 `POST /sales-workspaces`。设备 smoke 留给 P3 或最终 package closeout 统一记录。

