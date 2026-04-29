# Handoff: Status Evaluation Evidence Model

更新时间：2026-04-28

## Summary

本次补强多 Agent 工作流中的 Status / Planning Agent 规则，使项目状态评估从 task / handoff summary 转为 evidence-based milestone review。

核心口径：

- Status / Planning Agent 可以读取 task / package / handoff，但它们只能作为 delivery evidence。
- Capability 或 milestone status 不能只凭 task / handoff 的 `done` 更新。
- `done` 必须至少有 acceptance source、implementation evidence 和 validation evidence。
- Milestone closeout 必须使用 `PRD Acceptance Traceability`，并逐项记录证据来源、gap 和 confidence。

## Changed Files

- `docs/how-to/operate/multi_agent_workflow.md`
  - 新增 `Status Evaluation Evidence Model`。
  - 明确 Status / Planning Agent 的四层证据模型。
  - 更新标准协作流程和 prompt 模板。
- `docs/how-to/operate/multi_agent_prompts.md`
  - 更新 Project Status / Planning Agent prompt。
  - 增加 evidence matrix 输出格式和 status 更新规则。
  - 增加 Review Agent 对状态评估输出的检查要求。
- `docs/product/project_status.md`
  - 增加 Capability Matrix 更新的 evidence class 和状态更新规则。
- `docs/product/research/_milestone_acceptance_review_template.md`
  - 新增 milestone acceptance review 模板。
- `docs/product/README.md`
  - 增加 milestone acceptance review 模板入口。

## Validation

已验证：

- `rg -n "Status Evaluation Evidence Model|Evidence matrix|_milestone_acceptance_review_template|acceptance source|implementation evidence|validation evidence|delivery evidence" docs`
  - 结果：通过；规则入口、prompt、模板和 handoff 均可检索。
- `rg -n "task / handoff.*primary|只凭 task|Capability Matrix 更新|PRD Acceptance Traceability|low confidence|Confidence 标为 low" docs/how-to/operate/multi_agent_workflow.md docs/how-to/operate/multi_agent_prompts.md docs/product/project_status.md docs/product/research/_milestone_acceptance_review_template.md`
  - 结果：通过；核心约束可检索。
- `git diff --check`
  - 结果：通过。

## Known Limits

- 本次只改 workflow / product status 规则，不更新当前 capability matrix 的具体状态。
- 本次不开放 `_active.md` current package，不创建 V2.1 milestone acceptance review task。
- 本次不检查 backend / Android / runtime 实现证据；后续 milestone review 应按新模板执行。

## Recommended Next Step

如需继续，应开放 docs-only `V2.1 Milestone Acceptance Review` package，使用 `docs/product/research/_milestone_acceptance_review_template.md` 逐项核对 V2 PRD success criteria、代码实现和验证证据。
