# Skill Spec: `backend-runtime-boundary-guard`

更新时间：2026-04-29

## Purpose

守住 V3 runtime / memory / backend governance 边界：runtime memory 可以开放、自编辑、包含推断和假设；正式业务对象写回仍由 backend / Sales Workspace Kernel 裁决。

## When to trigger

- `backend/runtime/*`
- `AgentRun` 或 run-processing flow
- LangGraph / LangChain runtime 接入
- memory tools、自编辑 memory、archival memory、memory status labels
- runtime 输出写回正式业务对象
- MCP、observability、tool server 改变 runtime 权限

## Required repo docs

- 根 `AGENTS.md`
- `backend/AGENTS.md`
- `docs/README.md`
- `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
- `docs/architecture/v3/memory-native-sales-agent.md`
- 当前 task / handoff

V1/V2 runtime 文档只作 historical reference。

## Expected outputs / evidence

- 是否改变 runtime memory / formal object 边界
- 是否允许 runtime memory 保存 observed / inferred / hypothesis / confirmed / rejected / superseded
- formal object writeback 是否仍由 backend governance 裁决
- 是否误把 LangGraph checkpoint 当成业务 memory 主存
- 是否需要 dedicated V3 runtime / memory task

## Stop / escalate conditions

- runtime memory 被当成无治理的正式业务对象
- 因为 memory 是推断或假设就阻止 runtime 认知形成
- LangGraph checkpoint 成为唯一长期业务 memory 存储
- 未开放 task 就开始 V3 runtime implementation
- MCP / DB tools 暴露 unrestricted formal-object writes

## Non-goals

- 不实现 runtime。
- 不批准 LangGraph / MCP / DB tool 接入。
- 不替代 ADR 或 V3 architecture。
