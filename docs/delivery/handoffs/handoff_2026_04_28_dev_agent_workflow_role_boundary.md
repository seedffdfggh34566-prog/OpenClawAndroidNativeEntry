# Handoff: Dev Agent Workflow Role Boundary

更新时间：2026-04-28

## Summary

本次收紧多 Agent 工作流中的身份边界，避免 `Status / Planning Agent`、`Execution Agent`、`Review Agent` 被理解成脱离 Dev Agent 约束的实体。

核心口径：

- `Status / Planning Agent`、`Execution Agent`、`Review Agent` 是 Dev Agent 在不同线程中承担的 workflow role。
- 它们不是产品内 `Product Sales Agent`，不是 `Runtime / LangGraph Runtime`，也不是固定工具身份。
- Codex / Claude Code 线程即使承担某个 role，仍必须遵守 `AGENTS.md`、docs source of truth 和 `_active.md` 执行授权边界。

## Changed Files

- `AGENTS.md`
  - 在 `Multi-Agent Responsibility Split` 中增加短规则，明确三个角色都是 Dev Agent workflow roles。
- `docs/how-to/operate/multi_agent_workflow.md`
  - 在角色职责前增加 role identity boundary。
  - 更新 Status / Planning、Execution、Review prompt 模板开头。
- `docs/how-to/operate/multi_agent_prompts.md`
  - 在 quickstart 中增加 role identity boundary。
  - 将三个可复制 prompt 改为“你是一个 Dev Agent，本线程承担某角色”。

## Validation

已验证：

- `rg -n "workflow role|not product agents|不是产品内|你是一个 Dev Agent|固定工具身份" AGENTS.md docs/how-to/operate/multi_agent_workflow.md docs/how-to/operate/multi_agent_prompts.md`
  - 结果：通过；仓库级规则、runbook 和 prompt 模板均可检索到 Dev Agent workflow role 边界。
- `git diff --check`
  - 结果：通过。

## Known Limits

- 本次只修改 workflow / prompt 文档，不开放 `_active.md` current package。
- 本次不改 backend / Android / runtime 代码。
- 当前工作区存在与本次无关的 Android 未提交改动；本次未触碰这些文件。

## Recommended Next Step

后续使用多 Agent prompt 时，优先复制 `docs/how-to/operate/multi_agent_prompts.md` 中的新版本，确保线程先承认自己是 Dev Agent，再说明本线程承担的 workflow role。
