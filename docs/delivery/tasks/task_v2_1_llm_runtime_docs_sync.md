# Task: V2.1 LLM Runtime Docs Sync

状态：done

更新时间：2026-04-28

## Objective

同步 V2.1 Tencent TokenHub LLM runtime prototype 的入口文档、runbook、reference 和 handoff。

## Scope

- 更新 docs / reference / runtime / how-to / delivery 入口。
- 明确 LLM runtime prototype 已可通过显式 dev flag 使用。
- 明确仍不是 formal LangGraph，也不是 V2.2 search/contact。

## Out Of Scope

- 不改 backend behavior。
- 不改 Android。
- 不开放 V2.2 implementation。

## Outcome

文档入口已经指向 LLM boundary、structured output contract、dev runbook 和 eval 记录。

## Validation

```bash
rg "v2-1-llm-runtime|sales-workspace-chat-first-llm-runtime-contract|sales_agent_turn_llm_v1|Tencent TokenHub" docs backend/README.md
git diff --check
```
