# Task: V2.1 LLM Prompt Quality Follow-up

更新时间：2026-04-28

## 1. 任务定位

- 任务名称：V2.1 LLM Prompt Quality Follow-up
- 建议路径：`docs/delivery/tasks/task_v2_1_llm_prompt_quality_followup.md`
- 当前状态：`done`
- 优先级：P1
- 任务类型：`delivery`
- 是否属于 delivery package：`yes`
- 所属 package：`V2.1 Implementation Continuation`

---

## 2. 任务目标

扩充 V2.1 Sales Agent LLM runtime fake-client quality tests，验证 structured output、failure semantics 和 workspace non-mutation boundary。

---

## 3. 范围

In Scope：

- 增加 fake-client pytest 覆盖。
- 更新 LLM eval 记录。

Out of Scope：

- 修改 prompt version。
- 修改 runtime 默认模式。
- formal LangGraph。
- V2.2 search / ContactPoint。
- production-ready LLM quality claim。

---

## 4. 实际产出

- `backend/tests/test_sales_workspace_chat_first_llm_runtime.py` 新增 mixed、workspace explanation、invalid JSON、unsupported operation 和 client failure 覆盖。
- `docs/product/research/v2_1_llm_sales_agent_eval_2026_04_28.md` 补充 fake-client quality regression coverage。

---

## 5. 已做验证

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_runtime.py -q`

---

## 6. 实际结果说明

本任务只扩充测试和 eval 记录，不修改 runtime 行为。真实 LLM live smoke 仍需显式环境变量和密钥，不在本任务中运行。

