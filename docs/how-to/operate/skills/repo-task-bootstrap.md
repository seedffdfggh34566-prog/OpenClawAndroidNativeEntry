# Skill Spec: `repo-task-bootstrap`

更新时间：2026-04-29

## Skill name

`repo-task-bootstrap`

## Purpose

用于非 backend 专属的仓库级任务开工前收口：确认授权来源、任务边界、验证路径和 handoff 要求，避免把 workflow/docs/guardrail 变更扩成产品方向判断。

## When to trigger

适用于：

- docs / workflow / repo guardrail / skill 变更
- 当前 `_active.md` 没有明确 task，但用户在当前线程明确授权
- 已完成 task 不应被继续扩展，需要单独记录新的 follow-up
- 执行前需要明确 validation 和 handoff

不用于 backend 专属任务；backend 任务使用 `backend-task-bootstrap`。

## Required repo docs

- 根 `AGENTS.md`
- `docs/README.md`
- `docs/delivery/tasks/_active.md`
- 最接近的 task / handoff

## Allowed tools / commands

- 只读 repo 搜索
- 创建或更新 task / handoff
- `git diff --check`

## Expected outputs / evidence

输出应至少说明：

- 授权来源
- 当前用户消息是否已经授权本次工作
- in scope / out of scope
- 需要触及的文档或 workflow 区域
- 最轻有效验证
- 是否需要 handoff
- 是否需要明确标注历史 V1/V2 文档仅作 reference

## Stop / escalate conditions

- 需要决定产品方向或 release 状态
- 需要启动 V3 runtime / memory / Android / backend 实现
- 把历史 V1/V2 docs 当成当前真相
- 需要 secret、deployment、migration 或不可逆 Git 操作
- 需要把 task/handoff 证据升级为版本、milestone 或产品阶段完成结论

## Bundled resources plan

本阶段只需要 `SKILL.md`。后续如出现重复检查，可补轻量脚本。

## Non-goals

- 不替代产品方向文档
- 不替代 `backend-task-bootstrap`
- 不裁决 milestone / release / product phase 是否完成
