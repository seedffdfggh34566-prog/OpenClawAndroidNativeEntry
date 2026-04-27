# Task: V2.1 Android Chat-first Workspace UI Prototype

状态：planned / blocked by chat-first backend prototype

更新时间：2026-04-27

## Objective

在现有 Android Workspace 页面上补最小 chat-first 产品体验入口，让用户可以输入产品信息或获客方向，并通过 backend-managed Draft Review 审阅 Runtime 生成的 `WorkspacePatchDraft`。

## Required Precondition

- `task_v2_1_chat_first_runtime_backend_prototype.md`

## Scope

- Android 复用现有 `HttpURLConnection + org.json` 风格。
- 在 Workspace 页面增加最小 chat input。
- 调用 backend chat-first endpoint 或 task 明确的 equivalent prototype endpoint。
- 展示 assistant draft summary、draft review id、preview top-level changes。
- 用户 accept / reject / apply 仍走 backend Draft Review routes。
- Apply 成功后刷新 workspace / ranking / projection / ContextPack。

## Out Of Scope

- 不让 Android 构造正式 `WorkspacePatch`。
- 不实现自由编辑 workspace。
- 不引入 Retrofit / Hilt / Room。
- 不接真实 LLM。
- 不接 search / ContactPoint / CRM。
- 不做复杂聊天历史 UI。

## Validation

- `./gradlew :app:assembleDebug`
- `./gradlew :app:lintDebug`
- 如设备可用，执行 backend + Android smoke。
- 如设备不可用，handoff 明确记录未做 device-level 验证。

## Recommended Next

- `task_v2_1_product_experience_demo_runbook.md`
