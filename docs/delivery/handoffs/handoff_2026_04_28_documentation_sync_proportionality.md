# Handoff: Documentation Sync Proportionality

更新时间：2026-04-28

## Summary

本次补充文档同步分级规则，解决小 implementation / polish step 牵动过多高层文档的问题。

核心口径：

- 小 step / polish 默认只更新 task outcome 和 handoff。
- `_active.md` 只在执行授权、current package / task、queue、auto-continue 或 stop conditions 变化时更新。
- `project_status.md`、milestone review 和 root / docs README 只在 capability、milestone、project phase、证据矩阵或正式导航入口变化时更新。
- 如果 task 明确要求更新高层文档，执行 agent 可以更新，但必须说明原因。

## Changed Files

- `AGENTS.md`
  - 在 Documentation Update Rules 中增加 proportional docs sync 原则。
- `docs/how-to/operate/developer_workflow_playbook.md`
  - 新增“文档同步按影响范围分级”。
  - 更新日常收口流程，要求按影响范围决定是否更新高层文档。
- `docs/how-to/operate/multi_agent_workflow.md`
  - 新增 `Documentation Sync Proportionality`。
  - 更新 Execution Agent prompt 模板，要求报告 docs sync level and rationale。
- `docs/how-to/operate/multi_agent_prompts.md`
  - 更新可复制 Execution Agent prompt 和 Review Agent 检查项。
- `docs/delivery/tasks/_template.md`
  - 增加文档同步级别和同步范围字段。
- `docs/delivery/packages/_template.md`
  - 增加文档同步级别和 package documentation sync plan。
- `docs/delivery/README.md`
  - 增加 delivery 目录级文档同步范围规则。

## Validation

已验证：

- `rg -n "Documentation Sync Proportionality|文档同步按影响范围|文档同步范围|docs sync level|文档同步级别|project_status.md.*milestone review|小 step / polish" AGENTS.md docs`
  - 结果：通过；仓库级规则、runbook、prompt、模板、delivery README 和 handoff 均可检索。
- `git diff --check`
  - 结果：通过。

## Known Limits

- 本次只更新 workflow / template / delivery 文档，不回退或改写当前 Android implementation。
- 当前工作区已有 V2.1 lightweight entry polish 和多 Agent role boundary 相关未提交改动；本次在其基础上追加规则，不处理这些改动。
- 本次不修改 `_active.md` current state。

## Recommended Next Step

后续 Execution Agent 输出应新增 `docs sync level and rationale`，Review Agent 应检查小 step / polish 是否不必要地更新了 `project_status.md`、milestone review 或 README。
