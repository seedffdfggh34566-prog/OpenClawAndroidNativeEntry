# Handoff: V2.1 Android Workspace Onboarding

更新时间：2026-04-28

## 1. 本次改了什么

- Android `SalesWorkspaceBackendClient` 新增 `createWorkspace`。
- `OpenClawApp` 增加 workspace creation state 和创建成功后的自动刷新。
- `SalesWorkspaceScreen` 增加默认 `ws_demo` onboarding card。
- `_active.md` 衔接到 P3 trace / message history visibility。

---

## 2. 为什么这么定

- V2.1 Android demo path 的主要缺口是依赖预置 backend workspace。
- 使用已有 backend endpoint 可以减少 blast radius，不改变 API contract 或 persistence baseline。

---

## 3. 本次验证了什么

1. `./gradlew :app:assembleDebug`

---

## 4. 已知限制

- 只创建默认 `ws_demo`，不支持多 workspace 管理。
- 未做真机手动 smoke；后续 package closeout 应记录 adb/device 情况。
- workspace 已存在时 backend 仍会返回 409；UI 在已加载 workspace 时禁用创建按钮。

---

## 5. 推荐下一步

继续 P3：在 Android Workspace 页面展示最小 ConversationMessage history。

