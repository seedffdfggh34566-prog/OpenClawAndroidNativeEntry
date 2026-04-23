# Skill Spec: `backend-task-bootstrap`

更新时间：2026-04-23

## Skill name

`backend-task-bootstrap`

## Purpose

在后端实现开始前，把 thread 收口成固定的 task / validation / handoff 结构，避免 backend 工作在没有明确边界的情况下直接开工。

## When to trigger

适用于以下场景：

- backend 非 trivial 任务还没有正式 task
- 当前请求其实是 follow-up，不适合继续污染已有 task
- backend 改动触及 API contract、runtime boundary、persistence、migration、observability 或环境假设
- 需要先确定验证等级和 handoff 要点，再进入实现

## Required repo docs

- 根 `AGENTS.md`
- `backend/AGENTS.md`
- `docs/README.md`
- `docs/delivery/tasks/_active.md`
- 当前最相关的 backend task
- 对应 handoff

## Allowed tools / commands

- `rg`
- `git diff --check`
- 只读浏览 `docs/delivery/tasks/`、`docs/delivery/handoffs/`、`docs/reference/`、`docs/architecture/`

本 Skill 默认不直接承担实现验证命令，而是先确定后续该调用哪个 backend workflow skill。

## Expected outputs / evidence

输出应至少包括：

- 是否需要新建 follow-up task
- task 的 objective / scope / out of scope
- likely files
- 最小验证模板
- handoff 应覆盖的要点
- 下一步应该触发哪个 backend skill

## Stop / escalate conditions

遇到以下情况应停止并升级：

- 需要改产品方向、V1 scope 或正式对象语义
- 想把多类高风险 backend 变化打包进一个 thread
- 需要切数据库基线、切 observability、引入 LangGraph / MCP，但没有 dedicated task

## Bundled resources plan

本 Skill 后续允许补充：

- backend task template
- backend validation template
- backend handoff template

本阶段先以文本型 skill 为主，不要求脚本实现。

## Non-goals

- 不替代 task 本身
- 不替代实现 skill
- 不决定产品优先级
- 不自动修改 `_active.md`
