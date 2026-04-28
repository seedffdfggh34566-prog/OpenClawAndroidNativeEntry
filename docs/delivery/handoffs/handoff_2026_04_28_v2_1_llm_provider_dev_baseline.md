# Handoff: V2.1 LLM Provider Dev Baseline

日期：2026-04-28

## Changed

- `backend/api/config.py` 新增 V2.1 sales-agent runtime mode 与 prompt version 配置。
- 新增 `task_v2_1_llm_provider_dev_baseline.md`。
- 新增 `docs/how-to/operate/v2-1-llm-runtime-dev-runbook.md`。
- 更新 backend README。

## Result

V2.1 可通过显式配置进入真实 LLM runtime：

```text
OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=llm
OPENCLAW_BACKEND_SALES_AGENT_LLM_PROMPT_VERSION=sales_agent_turn_llm_v1
```

默认仍为 deterministic。

## Validation

- Settings default import check。
- `git diff --check`。

## Limitations

- 尚未实现 LLM sales-agent-turn。
- 尚未运行真实 TokenHub smoke。

## Next Step

执行 `task_v2_1_sales_agent_structured_output_contract.md`，定义 LLM structured output contract。
