# Task: V2 Android Review History View

状态：planned / blocked

更新时间：2026-04-27

## Objective

为 Android Workspace 页面设计和实现 Draft Review history / detail view。

## Blocker

必须等待 Draft Review persistence schema 与 backend read API 明确后才能执行。

## Scope Placeholder

- 展示历史 Draft Review。
- 展示 review status、decision、apply result 和 failure reason。
- 支持读取 detail。

## Out Of Scope Until Unblocked

- 不让 Android 构造正式 `WorkspacePatch`。
- 不实现 Android 自由编辑 workspace。
- 不新增 backend route，除非前置 backend task 已完成。
- 不接 LLM / LangGraph / search。
