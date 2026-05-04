# Skill Spec: `backend-runtime-boundary-guard`

更新时间：2026-04-30

## Purpose

守住 V3 sandbox-first 边界：runtime memory、workspace working state 和 customer intelligence working state 可以开放、自编辑、由 agent 维护；不要把 V3 初期写死为 formal object / PatchDraft / Kernel 流程。

## When to trigger

- `backend/runtime/*`
- `AgentRun` 或 run-processing flow
- LangGraph / LangChain runtime 接入
- memory tools、自编辑 memory、archival memory、memory status labels
- sandbox working state / customer intelligence working state
- 试图把 V3 初期重新导向 formal object、PatchDraft 或 Kernel 默认路径
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

- 是否改变 sandbox-first 假设
- 是否允许 runtime memory 保存 observed / inferred / hypothesis / confirmed / rejected / superseded
- 是否把 sandbox working state 过早冻结成 formal object / PatchDraft / Kernel 流程
- 是否误把 LangGraph checkpoint 当成业务 memory 主存
- 是否需要 dedicated V3 runtime / memory / working-state / customer-intelligence task

## Stop / escalate conditions

- V3 sandbox working state 被强制塞进 formal object / PatchDraft / Kernel 流程
- 因为 memory 是推断或假设就阻止 runtime 认知形成
- LangGraph checkpoint 成为唯一长期业务 memory 存储
- 未开放 task 就开始 V3 runtime implementation
- MCP / DB tools 暴露 unrestricted SQL、生产 CRM 写入、真实外部触达或不可逆导出

## Non-goals

- 不实现 runtime。
- 不批准 LangGraph / MCP / DB tool 接入。
- 不替代 ADR 或 V3 architecture。
