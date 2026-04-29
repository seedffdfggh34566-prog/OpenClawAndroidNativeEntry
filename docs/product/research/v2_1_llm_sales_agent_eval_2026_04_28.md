# V2.1 LLM Sales Agent Eval

日期：2026-04-28

## Scope

本次 eval 验证 V2.1 chat-first Sales Agent 在 Tencent TokenHub LLM runtime mode 下是否能产出可验证的 structured output。

Provider / model：

- provider：Tencent TokenHub
- model：`minimax-m2.5`
- prompt version：`sales_agent_turn_llm_v1`
- runtime mode：`real_llm_no_langgraph`

安全边界：

- 不记录 API key。
- 不记录 Authorization header。
- 不提交完整 prompt 或 provider console export。
- LLM output 必须经 backend structured validation。
- formal writeback 必须经 Draft Review 和 Sales Workspace Kernel。

## Samples

| Sample | Input Type | Expected |
| --- | --- | --- |
| 工业设备维保软件 | mixed product + direction | Draft Review previewed; product and direction operations present |
| 本地企业培训服务 | mixed product + direction | Draft Review previewed; product and direction operations present |
| 中小企业财税 SaaS | mixed product + direction | Draft Review previewed; product and direction operations present |
| 产业园区招商运营服务 | mixed product + direction | Draft Review previewed; product and direction operations present |
| 制造业外包生产和装配服务 | mixed product + direction | Draft Review previewed; product and direction operations present |
| 信息不足输入 | product update | clarifying questions; no Draft Review |
| 解释型问题 | workspace question | explanation; no Draft Review |

## Result

实际 live smoke 结果：

- 5 个中文 mixed product + lead direction 样例：通过。
- 信息不足输入 clarifying questions：通过。
- workspace explanation：通过。
- 所有 formal writeback 仍通过 Draft Review / Sales Workspace Kernel；live smoke 中 Draft Review preview 不直接 mutate workspace。

验证命令：

```bash
OPENCLAW_BACKEND_RUN_LIVE_LLM_SMOKE=1 PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_live.py -q
```

结果：`6 passed in 97.19s`。

若 live smoke 通过，可认为 V2.1 backend-level LLM runtime prototype 已具备基础可用性；仍不代表正式 LangGraph、V2.2 search/contact 或 production-ready LLM agent 完成。

## Fake-client quality regression coverage

P4 follow-up 扩充 fake-client tests，覆盖：

- mixed product + lead direction structured output。
- clarifying questions without Draft Review。
- workspace explanation without mutation。
- invalid schema output。
- invalid non-JSON output。
- unsupported operation blocked by Sales Workspace Kernel gate。
- TokenHub client failure recorded as failed AgentRun。
- workspace version conflict without mutation。

验证命令：

```bash
backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_runtime.py -q
```

结果：`10 passed`。
