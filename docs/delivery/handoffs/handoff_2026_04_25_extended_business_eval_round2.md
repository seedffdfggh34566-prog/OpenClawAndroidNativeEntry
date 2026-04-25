# Handoff：V1 Extended Business Eval Round 2

日期：2026-04-25

## 变更内容

- 使用真实 TokenHub `minimax-m2.5` 跑完 16 个中文业务样例。
- 开启 developer LLM inspector 记录 ProductLearning / LeadAnalysis trace。
- 更新 eval 记录：`docs/product/research/v1_extended_business_eval_round2_2026_04_25.md`。
- 修复 LeadAnalysis parser 对 MiniMax 尾部 malformed JSON 的最小兼容问题。
- 未改 Android、public API、schema、模型、provider 或 prompt。

## 触达文件

- `backend/runtime/graphs/lead_analysis.py`
- `backend/tests/test_tokenhub_client.py`
- `docs/product/research/v1_extended_business_eval_round2_2026_04_25.md`
- `docs/delivery/tasks/task_v1_extended_business_eval_round2.md`
- `docs/delivery/tasks/task_v1_demo_runbook_and_evidence_pack.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`
- `docs/README.md`

## 验证

- `backend/.venv/bin/python -m pytest backend/tests/test_tokenhub_client.py backend/tests/test_dev_llm_inspector.py`
  - 通过，16 passed。
- `backend/.venv/bin/python -m pytest backend/tests`
  - 通过，47 passed。
- 真实 backend API eval：
  - ProductLearning succeeded：16/16。
  - LeadAnalysis succeeded：16/16。
  - ReportGeneration succeeded：16/16。
  - report_readability pass：16/16。
  - hallucination_count total：0。
- `git diff --check`
  - 通过。

## 关键发现

- 初始 LeadAnalysis 为 13/16 succeeded，失败原因均为 `lead_analysis_llm_json_decode_failed`。
- inspector trace 显示失败不是 timeout，而是 MiniMax 在 JSON 末尾偶发输出 malformed brackets。
- parser 修复仅在严格解析失败后尝试已观测的尾部括号修复，不扩大为通用 JSON repair。
- 本轮 token：
  - ProductLearning total：18785。
  - LeadAnalysis total：28451。
  - Combined total：47236。
  - Average combined：约 2952 / 样例。

## 已知限制

- round2 eval 是人工/脚本辅助执行，不是长期自动化 eval 平台。
- inspector trace 保留在 `/tmp/openclaw_llm_traces_round2`，其中可能包含模型原始输出，不能提交到 Git。
- 本轮未验证 Android 真机 demo；下一步应进入 demo runbook and evidence pack。

## 建议下一步

执行 `task_v1_demo_runbook_and_evidence_pack.md`，固化可重复 demo 流程并收集真机证据包。
