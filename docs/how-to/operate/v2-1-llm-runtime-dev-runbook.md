# V2.1 LLM Runtime Dev Runbook

更新时间：2026-04-28

## Purpose

本 runbook 用于本地验证 V2.1 chat-first Sales Agent 的 Tencent TokenHub LLM runtime prototype。

## Environment

默认 deterministic runtime 不需要 LLM key。

启用真实 LLM runtime 时使用：

```bash
export OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=llm
export OPENCLAW_BACKEND_LLM_PROVIDER=tencent_tokenhub
export OPENCLAW_BACKEND_LLM_BASE_URL=https://tokenhub.tencentmaas.com/v1
export OPENCLAW_BACKEND_LLM_MODEL=minimax-m2.5
export OPENCLAW_BACKEND_SALES_AGENT_LLM_PROMPT_VERSION=sales_agent_turn_llm_v1
```

`OPENCLAW_BACKEND_LLM_API_KEY` 只能来自进程环境或 ignored `backend/.env`。不要在命令、文档、日志、handoff 或 PR 描述中打印 key。

如需确认本地 `.env` 不会被提交：

```bash
git check-ignore -v backend/.env
```

该命令只验证 ignore 规则，不读取文件内容。

## Expected Boundary

LLM runtime 只生成 assistant message、clarifying questions 或 `WorkspacePatchDraft`。

正式写回仍必须经过：

```text
WorkspacePatchDraft -> Draft Review -> WorkspacePatch -> Sales Workspace Kernel
```

## Smoke Commands

```bash
PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
```

真实 LLM smoke 需要后续 LLM runtime task 提供对应测试。执行时不得打印 key。
