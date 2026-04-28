# Task: V2.1 Sales Agent Structured Output Contract

状态：done

更新时间：2026-04-28

## Objective

定义 V2.1 Tencent TokenHub LLM runtime 的 structured output contract，保证 LLM 输出可验证、可拒绝、可追踪，并且不绕过 Draft Review / Sales Workspace Kernel。

## Scope

- 定义 `SalesAgentTurnLlmOutput` JSON shape。
- 定义 assistant message、clarifying questions、workspace explanation 和 patch operations 的输出规则。
- 定义 invalid LLM output 的错误语义。
- 明确 backend materialization / validation 责任。

## Out Of Scope

- 不实现 backend runtime。
- 不新增 route。
- 不改 Android。
- 不接正式 LangGraph。

## Outcome

新增 `docs/reference/api/sales-workspace-chat-first-llm-runtime-contract.md`。

## Validation

```bash
rg "SalesAgentTurnLlmOutput|llm_structured_output_invalid|WorkspacePatchDraft|Draft Review" docs/reference/api/sales-workspace-chat-first-llm-runtime-contract.md
git diff --check
```
