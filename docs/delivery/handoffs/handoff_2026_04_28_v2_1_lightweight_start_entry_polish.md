# Handoff: V2.1 Lightweight Start Entry Polish

更新时间：2026-04-28

## 1. 本次改了什么

- 将 Android Workspace onboarding 入口文案产品化为“开始销售工作区”。
- 将入口卡片从 `Workspace Onboarding` 调整为 `销售工作区入口`，减少首次使用时暴露技术概念。
- 保持使用既有 `POST /sales-workspaces` 创建默认 `ws_demo`，没有新增 backend endpoint。
- 当创建默认 workspace 返回 `409 workspace_already_exists` 时，Android 改为刷新并进入现有 `ws_demo`，随后展示 chat-first 输入。
- 保持已加载 workspace 的 chat submit、Draft Review、apply flow 不变。

## 2. 触达文件

- `app/src/main/java/com/openclaw/android/nativeentry/ui/workspace/SalesWorkspaceScreen.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `docs/delivery/tasks/task_v2_1_chat_first_workspace_start_gap_closure.md`
- `docs/product/research/v2_1_milestone_acceptance_review_2026_04_28.md`
- `docs/product/project_status.md`
- `docs/delivery/packages/package_v2_1_milestone_acceptance_and_gap_closure.md`
- `docs/delivery/tasks/_active.md`
- `docs/README.md`
- `docs/delivery/README.md`

## 3. 验证

- `./gradlew :app:assembleDebug`
  - 结果：通过。
  - 备注：保留既有 AGP/compileSdk warning 和 `LocalLifecycleOwner` deprecation warning。
- `adb devices`
  - 结果：检测到设备 `f3b59f04	device`。
- `adb install -r app/build/outputs/apk/debug/app-debug.apk`
  - 结果：通过。
- `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity`
  - 结果：应用可启动。
- `adb shell uiautomator dump`
  - 结果：可读取 app UI tree；设备恢复在历史 `分析报告` 内页，未自动完成 Workspace 页点击级 smoke。
- `git diff --check`
  - 结果：通过。

## 4. 已知限制

- 本次不声明 V2.1 product milestone 完成，只提供 lightweight entry polish evidence。
- 本次没有新增后端语义；`workspace_already_exists` 识别依赖既有 409 error body。
- 未完成后端联通下的真机点击级验证；需要设备停留或可导航到 Workspace 页，并配置 backend / `adb reverse tcp:8013 tcp:8013` 后复测。
- V2.2 search / ContactPoint / CRM、formal LangGraph、production onboarding、多 workspace、账号、租户、权限仍 blocked。

## 5. 推荐下一步

- 由 Status / Planning flow 基于本 handoff 和 review addendum 判断是否还需要 milestone review addendum follow-up。
- 不自动开放下游 implementation task。
