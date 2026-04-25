# Task：V1 Report Generation Polish

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Report Generation Polish
- 建议路径：`docs/delivery/tasks/task_v1_report_generation_polish.md`
- 当前状态：`done`
- 优先级：P1

本任务用于在 ProductLearning LLM、LeadAnalysis LLM 与 V1 readiness freeze 完成后，增强 `report_generation` 的最终报告表达，使其更像用户可复看的销售分析交付物。

本任务不把 report generation 切到 LLM，不改 public API，不改 Android DTO / UI。

---

## 2. 任务目标

1. 使用现有 `AnalysisReport` 字段承载更完整的报告结构。
2. 报告至少包含产品理解、优先客户与行业、场景机会、上下游 / 邻近机会、首轮销售验证计划、不建议优先方向、风险限制和行动清单。
3. Android 报告页无需改动即可展示 polished report。

---

## 3. 范围

本任务 In Scope：

- `backend/runtime/graphs/report_generation.py`
- backend tests
- task / handoff / delivery navigation

本任务 Out of Scope：

- 不改 backend API / schema。
- 不改 Android。
- 不切 report_generation LLM。
- 不新增导出、分享、编辑、CRM。

---

## 4. 验收标准

1. backend tests 通过。
2. 1 个 backend API smoke 能生成 polished report。
3. report sections 包含：
   - 产品理解
   - 优先客户与行业
   - 场景机会
   - 上下游与邻近机会
   - 首轮销售验证计划
   - 不建议优先方向
   - 风险与限制
   - 下一步行动清单
4. 用户可见字段不泄漏工程词。
5. `git diff --check` 通过。

---

## 5. 实际产出

- `report_generation` 继续保持 heuristic graph，不切 LLM。
- 仍使用现有 `AnalysisReport.title`、`summary`、`sections`、`body_markdown` 承载报告内容。
- 报告 section 调整为更像交付物的固定结构：
  - 产品理解
  - 优先行业与客户
  - 场景机会
  - 上下游与邻近机会
  - 首轮销售验证计划
  - 不建议优先方向
  - 风险与限制
  - 下一步行动清单
- Android 不需要改动，现有报告页可直接展示这些 sections。

---

## 6. 已做验证

- `backend/.venv/bin/python -m pytest backend/tests`
  - 39 passed。
- backend API smoke with mocked TokenHub
  - 创建 ProductProfile。
  - 确认 ProductProfile。
  - 生成 LeadAnalysisResult。
  - 生成 AnalysisReport。
  - 确认 report sections 包含 8 个 polished report section。
- `git diff --check`
  - 通过。

---

## 7. Handoff

见 `docs/delivery/handoffs/handoff_2026_04_25_report_generation_polish.md`。
