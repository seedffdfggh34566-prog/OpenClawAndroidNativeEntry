# Task: V2.1 Workspace Explanation Backend Prototype

状态：done

更新时间：2026-04-27

## Objective

让 Product Sales Agent 能基于当前 workspace objects 回答解释型问题，例如“为什么推荐这个方向”“风险是什么”“先做哪个方向”。

## Scope

- 仅在 clarifying questions backend prototype 完成后开放。
- assistant response 必须引用当前 `ProductProfileRevision`、`LeadDirectionVersion` 和 ContextPack source versions。
- 解释型回答不一定生成 `WorkspacePatchDraft`。

## Out Of Scope

- 不接 V2.2 search / ContactPoint / CRM。
- 不接真实 LLM，除非后续 task 明确改变策略。
- 不改 formal workspace writeback boundary。

## Outcome

- `workspace_question` sales-agent turns now return an assistant explanation grounded in current `ProductProfileRevision`, `LeadDirectionVersion`, and ContextPack source versions.
- Explanation turns do not create `WorkspacePatchDraft` or Draft Review.
- Workspace version remains unchanged.

## Validation

```bash
PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
git diff --check
```
