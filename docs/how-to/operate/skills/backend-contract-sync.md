# Skill Spec: `backend-contract-sync`

更新时间：2026-04-29

## Purpose

收口 backend 专属 contract/docs：API、runtime、memory、persistence、architecture、task、handoff 与验证证据。通用 task/handoff wording 仍交给 `task-handoff-sync`。

## When to trigger

- backend 实现任务收尾
- API / schema / persistence / runtime / memory 边界文档同步
- V3 backend governance follow-up 完成后收口

## Required repo docs

- 根 `AGENTS.md`
- `backend/AGENTS.md`
- `docs/README.md`
- 当前 backend task / handoff
- 被触及的 reference、architecture 或 V3 docs

## Expected outputs / evidence

- 哪些 backend contract/docs 已同步
- 哪些 backend docs 仍需要 follow-up
- task 与 handoff 是否反映真实工作
- V3 memory / formal boundary 是否一致
- validation evidence 是否记录清楚

## Stop / escalate conditions

- 方向层文档需要语义变化
- 实现与 ADR-009 或 V3 architecture 冲突
- backend task/handoff 未经 review 声称 V3 implementation、milestone 或 production-ready
- 当前 thread 没有合法 task 却试图收口正式 backend 实现

## Non-goals

- 不替代 `task-handoff-sync`。
- 不决定任务是否业务上完成。
- 不自动改写 product / ADR 含义。
