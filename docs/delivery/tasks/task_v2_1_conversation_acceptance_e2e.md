# Task: V2.1 Conversation Acceptance E2E

状态：done

更新时间：2026-04-27

## Objective

使用 5 个中文业务样例验证 V2.1 conversational product experience 是否满足 PRD success criteria。

## Scope

- 覆盖 `docs/reference/evals/v2_1_conversation_acceptance_examples.md` 中的 5 个样例。
- 验证 clarifying questions、ProductProfileRevision、LeadDirectionVersion、workspace explanation、trace refs 和 Postgres recovery。
- 输出最终 PRD Acceptance Traceability 更新。

## Out Of Scope

- 不验证 V2.2 search / ContactPoint。
- 不要求真实 LLM。
- 不宣称 V2.1 completed，除非 PRD success criteria 均为 `done` 或由产品文档明确 re-scope。

## Outcome

- Added backend e2e coverage for all 5 Chinese business samples.
- Each sample verifies clarifying question behavior, product profile draft/review/apply, lead direction draft/review/apply, workspace explanation, AgentRun output refs, Draft Review refs, WorkspaceCommit refs, and no mutation for non-draft turns.
- Updated PRD Acceptance Traceability to mark backend-level V2.1 conversational acceptance as completed while keeping Android polish / device acceptance partial.

## Validation

```bash
PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
git diff --check
```
