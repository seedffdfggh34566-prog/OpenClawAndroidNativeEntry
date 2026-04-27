# Task: V2.1 Android Conversation Sample Smoke

状态：done

更新时间：2026-04-27

## Objective

用 Android Workspace 页面验证代表性 V2.1 中文业务样例能走通 chat-first product experience。

## Scope

- 使用现有 Workspace 页面，不改导航。
- 覆盖至少 2 个中文样例：
  - 工业设备维保软件。
  - 中小企业财税 SaaS。
- 验证 Android 可展示：
  - insufficient input -> `clarifying_question`
  - product turn -> Draft Review
  - accept/apply -> product profile visible
  - direction turn -> Draft Review
  - accept/apply -> lead direction visible
  - `workspace_question` -> explanation answer

## Out Of Scope

- 不要求 Android 自动创建 workspace。
- 不接真实 LLM。
- 不接 V2.2 search / ContactPoint / CRM。
- 不实现 Android 自由编辑 workspace。

## Outcome

- Sample smoke scenario is defined for the device acceptance task.
- Actual device evidence is recorded in `task_v2_1_product_experience_device_acceptance.md` and its handoff.

## Validation

```bash
adb devices
adb reverse tcp:8013 tcp:8013
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.openclaw.android.nativeentry/.MainActivity
```
