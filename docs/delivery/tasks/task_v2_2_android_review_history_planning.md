# Task: V2.2 Android Review History Planning

状态：planned / blocked

更新时间：2026-04-27

## Objective

规划 Android 如何展示 Draft Review history / detail view，并保持 Android 只作为人工审阅入口，不成为 formal truth layer。

## Scope Placeholder

- 定义 Android history view 需要读取的 backend contract。
- 定义 review status、event timeline、apply result、failure reason 的展示边界。
- 明确 stale / expired / rejected / applied 状态的用户提示。

## Out Of Scope Until Unblocked

- 不改 Android UI。
- 不新增 backend history endpoint。
- 不改 Draft Review persistence schema。
- 不接 Runtime / LangGraph。

## Blocker

必须等待 Draft Review history read API contract 或 Runtime / LangGraph design 明确后再开放。
