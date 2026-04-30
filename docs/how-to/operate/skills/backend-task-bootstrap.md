# Skill Spec: `backend-task-bootstrap`

更新时间：2026-04-29

## Purpose

在 backend 实现前收口任务边界、验证路径和 handoff，特别适用于 V3 runtime、memory、API、persistence 和 backend governance 工作。

## When to trigger

- backend 非 trivial 任务没有明确 task
- 当前请求是 follow-up，不适合继续污染已完成 task
- 触及 API contract、runtime boundary、memory、persistence、migration、observability 或环境假设
- 需要先确定验证等级和 handoff 要点

## Required repo docs

- 根 `AGENTS.md`
- `backend/AGENTS.md`
- `docs/README.md`
- `docs/delivery/tasks/_active.md`
- 最接近的 backend task / handoff

## Expected outputs / evidence

- 授权来源
- 是否需要新建 follow-up task
- objective / in scope / out of scope
- likely files
- 最小验证模板
- handoff 应覆盖的要点
- 下一步应触发哪些 backend guard skills

## Stop / escalate conditions

- 需要改产品方向或正式对象语义
- 未开放 task 就启动 V3 runtime / memory implementation
- 把 LangGraph、memory schema、API contract、migration 打包成一个过大任务
- 切数据库、observability、MCP 或 deployment 假设但没有 dedicated task
- 需要 secrets 或不可逆 Git 操作

## Non-goals

- 不替代 task 本身。
- 不决定产品优先级。
- 不自动修改 `_active.md`，除非当前任务明确要求。
