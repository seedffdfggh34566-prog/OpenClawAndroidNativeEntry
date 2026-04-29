# Handoff: V2.1 LLM Prompt Quality Follow-up

更新时间：2026-04-28

## 1. 本次改了什么

- 扩充 V2.1 Sales Agent LLM runtime fake-client tests。
- 更新 LLM eval 文档，记录 P4 regression coverage。
- `_active.md` 衔接到 P5 Postgres verification hardening。

---

## 2. 为什么这么定

- V2.1 LLM runtime 仍是 explicit-flag prototype，最需要先补 failure semantics 和 structured output 回归覆盖。
- 本任务不改变 runtime 行为，避免把 LLM prototype 升级为 production-ready agent。

---

## 3. 本次验证了什么

1. `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_runtime.py -q`

---

## 4. 已知限制

- 未运行 live LLM smoke。
- 未新增 prompt version。
- formal LangGraph、search/contact 和 production hardening 仍 blocked。

---

## 5. 推荐下一步

继续 P5：执行真实 Postgres verification hardening。

