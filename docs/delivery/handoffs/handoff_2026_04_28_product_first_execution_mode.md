# Handoff: Product-First Execution Mode

更新时间：2026-04-28

## Summary

本次新增 Product-First Execution Mode，降低 V2.1 Android 产品体验任务的文档治理成本。

核心规则：

- Android UI、demo path、product polish、user-visible experience recovery 默认优先代码和真机体验。
- 默认只更新当前 task outcome 和一个短 handoff。
- 不默认更新 `docs/README.md`、`docs/delivery/README.md`、`docs/product/project_status.md`、milestone review、multi-agent workflow docs 或 package closeout。
- 只有 API/schema/migration、PRD/ADR 含义、V2.2 search/contact/privacy、milestone status、release/deployment/secrets 变化时，才升级到重文档流程。

## Changed Files

- `AGENTS.md`
  - 在 Documentation Update Rules 下新增 `Product-First Execution Mode`。
- `docs/delivery/tasks/task_v2_1_android_chat_entry_recovery_and_demo_path.md`
  - 明确当前任务 `Execution mode: Product-first`。
  - 明确本任务只默认更新 task outcome 和短 handoff。
- `docs/how-to/operate/multi_agent_prompts.md`
  - 更新 Execution Agent prompt，要求输出 `Product-first mode: yes/no`。
  - 更新 Review Agent 检查项，防止产品体验任务被扩大成文档治理任务。

## Validation

已验证：

- `rg -n "Product-First Execution Mode|Product-first mode|产品体验优先|user-visible Android|不默认更新.*project_status|不默认更新.*README" AGENTS.md docs/how-to/operate/multi_agent_prompts.md docs/delivery/tasks/task_v2_1_android_chat_entry_recovery_and_demo_path.md`
  - 结果：通过；Product-first 规则、Execution Agent 输出要求和默认禁止高层文档同步规则均可检索。
- `git diff --check`
  - 结果：通过。

## Known Limits

- 本次不改 Android / backend / runtime 代码。
- 本次不修改 `docs/product/project_status.md`、`docs/README.md`、`docs/delivery/README.md`、milestone review 或 `_active.md`。
- 当前工作区已有其他未提交改动；本次只追加 Product-first 规则。

## Next Step

Execution Agent 应直接继续当前 Android chat surface 产品化任务，并在输出中报告：

- `Product-first mode: yes`
- `docs sync level and rationale`
- 真机上是否看到聊天上下文和输入框
