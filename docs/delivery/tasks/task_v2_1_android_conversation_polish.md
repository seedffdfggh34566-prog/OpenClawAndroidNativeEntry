# Task: V2.1 Android Conversation Polish

状态：done

更新时间：2026-04-27

## Objective

在 backend V2.1 conversational acceptance 通过后，做最小 Android polish，使用户能更清楚地看到追问、解释型回答和 Draft Review 状态。

## Scope

- 仅做现有 Workspace 页面内的最小 UI polish。
- 不重写导航。
- 不新增 Android formal workspace write path。
- 保持 backend / Sales Workspace Kernel 为正式写回裁决层。

## Out Of Scope

- 不做完整聊天产品重写。
- 不接 V2.2 search / ContactPoint / CRM。
- 不实现 Android 自由编辑 workspace。

## Outcome

- Added a `workspace_question` selector to the existing Workspace screen.
- Updated chat-first copy so turns are not all described as Draft Review generation.
- Displayed `clarifying_question` as Sales Agent follow-up questions and `workspace_question` as explanation answers.
- Clarified that turns without `patch_draft` do not enable review/apply and do not write workspace state.

## Validation

```bash
./gradlew :app:assembleDebug
./gradlew :app:lintDebug
```
