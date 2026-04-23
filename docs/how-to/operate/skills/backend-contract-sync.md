# Skill Spec: `backend-contract-sync`

更新时间：2026-04-23

## Skill name

`backend-contract-sync`

## Purpose

检查 backend 改动后的 contract、architecture、task 和 handoff 是否同步收口，避免“代码变了但边界说明还停在旧状态”。

## When to trigger

适用于以下场景：

- backend 实现任务收尾
- API / schema / persistence / runtime 边界文档同步
- 后端 follow-up task 完成后收口

## Required repo docs

- 根 `AGENTS.md`
- `backend/AGENTS.md`
- `docs/README.md`
- `docs/reference/api/backend-v1-minimum-contract.md`
- 当前 task
- 对应 handoff

必要时还应读取：

- `docs/architecture/system-context.md`
- `docs/architecture/backend/backend-agent-stack-phased-adoption.md`

## Allowed tools / commands

- `rg "backend|LangGraph|MCP|Postgres|pgvector|Langfuse" docs backend`
- `git diff -- docs backend`
- `git diff --check`

## Expected outputs / evidence

输出应至少包括：

- 哪些 backend 相关 docs 已同步
- 哪些 docs 仍需要补
- task 与 handoff 是否一致
- 当前实现是否仍符合已有 contract / architecture 边界

## Stop / escalate conditions

遇到以下情况应停止并升级：

- 已发生方向层变化，但还没更新对应方向层文档
- backend 技术栈结论与现有 architecture / ADR 冲突
- 当前 thread 没有明确 task 却试图收口正式实现

## Bundled resources plan

本 Skill 后续允许补充：

- backend docs sync checklist
- contract / task / handoff drift checklist

本阶段不要求脚本实现。

## Non-goals

- 不替代 task 本身
- 不决定任务是否业务上完成
- 不替代 `task-handoff-sync`
- 不自动改写 product / ADR 含义
