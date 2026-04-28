# Handoff: V2.1 LLM Eval Acceptance Examples

日期：2026-04-28

## Changed

- 新增 live Tencent TokenHub smoke test。
- 新增 `task_v2_1_llm_eval_acceptance_examples.md`。
- 新增 eval 记录：`docs/product/research/v2_1_llm_sales_agent_eval_2026_04_28.md`。

## Result

V2.1 LLM runtime eval 覆盖：

- 5 个中文 mixed product + lead direction 样例。
- 信息不足时 clarifying questions。
- workspace explanation。

实际 live smoke 通过：

```bash
OPENCLAW_BACKEND_RUN_LIVE_LLM_SMOKE=1 PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_live.py -q
```

结果：`6 passed in 97.19s`。

执行过程中发现并修正了真实模型常见输出漂移：

- 带 patch 的更新 turn 偶尔标成 `workspace_question`。
- 方向 payload 偶尔混入产品字段。
- 模型偶尔先输出非目标 JSON object 或文本解释。

Backend runtime 已增加收敛逻辑：重试一次 structured output、按 operation 类型裁剪 payload、workspace explanation 可保留非 mutating text fallback。

## Validation

- fake-client LLM runtime tests。
- live Tencent TokenHub smoke。
- `git diff --check`。

## Limitations

- 本轮不是 prompt tuning 任务。
- 本轮不接正式 LangGraph。
- 本轮不接 V2.2 search / ContactPoint / CRM。

## Next Step

执行 docs / runbook / handoff sync。
