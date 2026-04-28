# Task: V2.1 LLM Provider Dev Baseline

状态：done

更新时间：2026-04-28

## Objective

复用仓库已有 Tencent TokenHub LLM client，为 V2.1 chat-first Sales Agent runtime 增加显式 dev mode 配置。

## Scope

- 使用现有 `backend/runtime/llm_client.py` 的 `TokenHubClient`。
- 保持默认 provider / model 为 `tencent_tokenhub` / `minimax-m2.5`。
- 新增 `OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=deterministic|llm`。
- 新增 `OPENCLAW_BACKEND_SALES_AGENT_LLM_PROMPT_VERSION=sales_agent_turn_llm_v1`。
- 更新 backend / runbook 文档。

## Out Of Scope

- 不实现 LLM sales-agent-turn。
- 不新增 LLM SDK。
- 不读取、打印或提交 API key。
- 不改变默认 deterministic runtime。

## Outcome

Backend settings 已具备 V2.1 sales-agent runtime mode 与 prompt version 配置。

## Validation

```bash
PYTHONPATH=$PWD backend/.venv/bin/python - <<'PY'
from backend.api.config import Settings
s = Settings()
assert s.sales_agent_runtime_mode == "deterministic"
assert s.sales_agent_llm_prompt_version == "sales_agent_turn_llm_v1"
PY
git diff --check
```
