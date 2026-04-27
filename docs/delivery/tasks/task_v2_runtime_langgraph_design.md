# Task: V2 Runtime LangGraph Design

状态：planned / blocked by V2.1 product experience

更新时间：2026-04-27

## Objective

设计正式 Runtime / LangGraph integration，让 Runtime 产出可审阅的 `WorkspacePatchDraft`。

## Blocker

必须等待 V2.1 chat-first contract examples、backend prototype 和产品体验闭环完成后才能执行；Postgres dev environment、Sales Workspace persistence schema design、Draft Review persistence schema 和 writeback 边界已完成，但 V2.1 product experience 仍未完成。

## Scope Placeholder

- Runtime graph 输入 / 输出边界。
- `WorkspacePatchDraft` 生成与 validation。
- ContextPack 读取。
- tool output 与 source evidence 边界。
- observability 与 failure handling。

## Out Of Scope Until Unblocked

- 不接真实 LLM。
- 不实现 LangGraph graph。
- 不接 search / contact / CRM。
- 不改变 Sales Workspace Kernel formal writeback owner。
