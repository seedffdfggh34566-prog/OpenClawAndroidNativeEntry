# Skill Spec: `backend-runtime-boundary-guard`

更新时间：2026-04-23

## Skill name

`backend-runtime-boundary-guard`

## Purpose

对产品后端与 runtime 执行层之间的边界做守门，避免 runtime 逻辑越权成为产品真相层，或把产品后端静默改造成 agent runtime 宿主；同时吸收当前阶段轻量 `agent_run_lifecycle` 要求。

## When to trigger

适用于以下改动：

- `backend/runtime/*`
- `backend/api/services.py` 中的 run processing 逻辑
- `AgentRun`、正式对象写回链路
- 计划引入 `LangGraph`、`MCP`、observability tracing、tool server 的任务

## Required repo docs

- 根 `AGENTS.md`
- `backend/AGENTS.md`
- `docs/README.md`
- `docs/architecture/system-context.md`
- `docs/architecture/backend/backend-agent-stack-phased-adoption.md`
- 当前 task
- 对应 handoff

## Allowed tools / commands

- `rg "AgentRun|StubRuntimeAdapter|runtime|output_refs|input_refs" backend docs`
- `git diff -- backend/runtime backend/api/services.py docs/architecture`
- `backend/.venv/bin/python -m pytest backend/tests`
- `backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`

## Expected outputs / evidence

输出应至少包括：

- 这次改动是否改变了 product backend / runtime 边界
- 当前 run 状态口径是否仍保持轻量实现
- 输入引用、输出引用和错误记录如何变化
- runtime 仍然只承担什么职责
- formal object writeback 是否仍经由产品后端
- 是否需要提升为专门的 runtime adoption task

## Stop / escalate conditions

遇到以下情况应停止并升级：

- runtime 直接接管正式对象主真相
- 准备把 `LangGraph` 扩展成整个后端框架
- 准备把 `MCP` 扩展成内部服务总线
- observability、tooling、runtime framework 变更超出当前 task

## Bundled resources plan

本 Skill 后续允许补充：

- runtime boundary checklist
- `AgentRun` / object writeback verification checklist
- 轻量 run lifecycle checklist

本阶段不要求脚本实现。

## Non-goals

- 不直接实现新的 runtime 编排
- 不替代架构决策
- 不替代 `backend-local-verify`
- 不自动批准 `LangGraph` 或 `MCP` 接入
- 不假设 `waiting_for_user`、interrupt/resume、durable checkpoints 已落地
- 不单独再拆一个 `agent_run_lifecycle` skill，除非真实 runtime 生命周期能力进入 scope
