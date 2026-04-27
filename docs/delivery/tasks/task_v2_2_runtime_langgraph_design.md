# Task: V2.2 Runtime / LangGraph WorkspacePatchDraft Design

状态：planned / blocked

更新时间：2026-04-27

## Objective

设计正式 Runtime / LangGraph 如何在 V2.2 中产出 `WorkspacePatchDraft`，并通过 Draft Review / Sales Workspace Kernel 进入正式 workspace。

## Scope Placeholder

- 定义 Runtime graph 的输入、输出和失败模式。
- 明确 `WorkspacePatchDraft` 生成边界。
- 明确 Runtime 不直接写 formal workspace objects。
- 明确 ContextPack、Draft Review、Kernel apply 的协作顺序。
- 明确真实 LLM 接入前的 mock / fixture 验证方式。

## Out Of Scope Until Unblocked

- 不实现 LangGraph graph。
- 不接真实 LLM。
- 不接 search provider。
- 不改 Android。
- 不新增 backend write route。

## Blocker

必须先完成 V2.1 closeout review，并由 `_active.md` 明确开放。
