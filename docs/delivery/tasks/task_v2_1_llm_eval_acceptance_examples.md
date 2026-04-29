# Task: V2.1 LLM Eval Acceptance Examples

状态：done

更新时间：2026-04-28

## Objective

用 fake-client tests 和真实 Tencent TokenHub smoke 验证 V2.1 LLM runtime prototype 能覆盖 PRD conversational acceptance 的核心后端路径。

## Scope

- 新增 live LLM smoke test，默认跳过，显式 `OPENCLAW_BACKEND_RUN_LIVE_LLM_SMOKE=1` 才运行。
- 覆盖 5 个中文业务样例的 mixed product + lead direction draft。
- 覆盖 clarifying question 和 workspace explanation 路径。
- 新增 eval 记录，不记录 key、Authorization header 或完整 prompt。

## Out Of Scope

- 不做 prompt tuning 长轮次优化。
- 不接 LangGraph。
- 不接 search / ContactPoint / CRM。
- 不做 Android 改动。

## Outcome

Live LLM smoke 使用现有 Tencent TokenHub 配置运行；结果记录在 `docs/product/research/v2_1_llm_sales_agent_eval_2026_04_28.md`。

## Validation

```bash
PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_runtime.py -q
OPENCLAW_BACKEND_RUN_LIVE_LLM_SMOKE=1 PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_live.py -q
git diff --check
```
