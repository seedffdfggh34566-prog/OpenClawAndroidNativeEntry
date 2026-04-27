# Task: V2.1 Conversational Completion Scope

状态：done

更新时间：2026-04-27

## Objective

将 PRD acceptance gap review 转成完整 V2.1 conversational product experience 的最小完成范围。

## Scope

- 定义 V2.1 conversational completion 的完成标准。
- 明确必须补齐的能力：主动追问、产品理解、获客方向调整、解释型回答、traceability、Postgres recovery、5 个中文样例验收。
- 明确不做 V2.2 search/contact、CRM、自动触达、真实 LLM、正式 LangGraph 或大规模 Android 重写。
- 给出后续实现顺序，但不直接实现。

## Outcome

- 新增 `docs/architecture/runtime/v2-1-conversational-completion-scope.md`。
- 默认采用 backend-first、deterministic-first 路线。
- 推荐第一个实现任务为 `task_v2_1_clarifying_questions_backend_prototype.md`。

## Validation

```bash
rg "V2.1 Conversational Completion Scope|Clarifying questions|Workspace explanation|deterministic Product Sales Agent" docs/architecture/runtime/v2-1-conversational-completion-scope.md
git diff --check
```
