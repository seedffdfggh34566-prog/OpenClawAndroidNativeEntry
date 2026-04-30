# Skill Spec: `task-handoff-sync`

更新时间：2026-04-29

## Skill name

`task-handoff-sync`

## Purpose

检查 task、handoff、docs 导航与实际产出的一致性，保证任务能完整收口。

## When to trigger

适用于任何非 trivial Android / backend / docs 任务的收尾阶段，尤其适用于：

- Android thread 完成后
- workflow / docs / guardrails 变更后
- 一个 task 明显跨多个文档入口时

通常在功能或文档工作已经完成后触发，作为最后一轮收口检查。

## Required repo docs

- 根 `AGENTS.md`
- `docs/README.md`
- `docs/delivery/tasks/_active.md`
- 当前 task
- 对应 handoff

## Allowed tools / commands

- 只读搜索命令
- `git diff --check`
- 路径 / 链接一致性检查

不要求编译或运行 Android 工程。

## Expected outputs / evidence

输出应至少包括：

- 当前 task 是否存在
- task 状态是否合理
- handoff 是否存在
- handoff 是否记录了验证、限制和下一步
- task / handoff 是否只声明任务完成、验证结果和已知限制
- task / handoff 是否避免随意声明 V3 implementation、版本、milestone、产品阶段、产品体验或 production-ready 完成
- 是否误把历史 V1/V2 文档当成当前 V3 真相
- 相关 docs 入口是否需要同步
- 哪些地方仍未收口

## Stop / escalate conditions

遇到以下情况应停止并升级：

- 没有当前 task
- 涉及方向层变化但未先更新方向层文档
- task 与 handoff 对“已完成内容”表述冲突
- task / handoff 把局部任务证据升级为版本、milestone、产品阶段或产品体验完成结论
- task / handoff 在没有真实 implementation task 的情况下声称 V3 implementation started/done
- 历史 V1/V2 docs 被当成当前 V3 direction
- 需要 agent 擅自裁决任务优先级

## Bundled resources plan

本 Skill 后续允许补充：

- 统一检查清单模板
- 轻量一致性巡检脚本

本阶段优先固定检查清单，不需要复杂脚本。

## Non-goals

- 不自动决定任务是否“业务上完成”
- 不替代 task 本身
- 不改写方向层文档含义
