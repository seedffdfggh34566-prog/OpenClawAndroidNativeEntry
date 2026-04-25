# Handoff：V1 Report Readability Postprocess Follow-up

日期：2026-04-25

## 变更内容

- 增强 `report_generation` 的文本后处理。
- summary 控制长度，section bullet 按常见中文标点拆分长句。
- 未改 API、schema、Android 或 report_generation runtime 模式。

## 触达文件

- `backend/runtime/graphs/report_generation.py`
- `backend/tests/test_api.py`
- `docs/delivery/tasks/task_v1_report_readability_postprocess_followup.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`

## 验证

- `backend/.venv/bin/python -m pytest backend/tests`
  - 通过。
- backend API smoke with mocked TokenHub
  - summary 与 section line 长度受控。
- `git diff --check`
  - 通过。

## 已知限制

- 仍是 heuristic report_generation，不是 LLM 报告生成。
- 当前拆分按常见标点做轻量处理，不做复杂自然语言重写。
- 报告质量仍依赖 LeadAnalysisResult 的输入质量。

## 建议下一步

执行 `task_v1_extended_business_eval_round2.md`，用扩展样例评估 RC 质量、稳定性和 token 成本。
