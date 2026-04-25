# Task：V1 Report Readability Postprocess Follow-up

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Report Readability Postprocess Follow-up
- 建议路径：`docs/delivery/tasks/task_v1_report_readability_postprocess_followup.md`
- 当前状态：`done`
- 优先级：P0

本任务用于在 report_generation polish 后，继续收口最终报告的可读性，让报告页更适合作为 demo / RC 交付物。

---

## 2. 范围

In Scope：

- 只调整 backend `report_generation` 的文本后处理。
- 减少超长 bullet、连续分号挤在一条建议、summary 过长等问题。
- 更新 backend tests。
- 保持 `AnalysisReport.sections` 现有承载方式。

Out of Scope：

- 不改 public API。
- 不改 persisted schema。
- 不改 Android DTO / UI / navigation。
- 不把 report_generation 切 LLM。
- 不接外部搜索。

---

## 3. 实际产出

- `report_generation` 新增轻量可读性后处理：
  - summary 最长控制在 120 个字符以内。
  - section body 中的长条目按中文分号、英文分号和句号拆分。
  - 无法拆分的超长条目会截断并追加省略号。
  - 各 section 继续以 bullet list 呈现。
- backend tests 增加断言：
  - summary 长度不超过 120。
  - 长建议可拆成多条。
  - section 单行长度不超过 130。
  - 报告仍包含交付物结构与关键文案。

---

## 4. 验证

- `backend/.venv/bin/python -m pytest backend/tests`
  - 通过。
- backend API smoke with mocked TokenHub
  - 生成 report sections，确认 summary 和 section line 长度受控。
- `git diff --check`
  - 通过。

---

## 5. 后续建议

继续执行 `task_v1_extended_business_eval_round2.md`，用 16 个真实中文业务样例验证 ProductLearning / LeadAnalysis / ReportGeneration 的质量、稳定性和 token 成本。
