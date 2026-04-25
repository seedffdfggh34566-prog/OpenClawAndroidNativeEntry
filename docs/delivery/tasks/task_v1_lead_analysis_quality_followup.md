# Task：V1 Lead Analysis Quality Follow-up

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Lead Analysis Quality Follow-up
- 建议路径：`docs/delivery/tasks/task_v1_lead_analysis_quality_followup.md`
- 当前状态：`done`
- 优先级：P1

本任务用于在 V1 主闭环、真实 LLM ProductLearning、真实中文 smoke、usage metadata 与 8 个真实业务样例 eval 均完成后，提升 `lead_analysis` 的分析深度。

当前重点不是扩 UI，也不是先做报告页 polish，而是在不改 public contract 的前提下，让 V1 最终交付更接近可用于销售验证的获客分析。

---

## 2. 任务目标

增强现有 backend heuristic `lead_analysis` 输出，使其至少补齐：

1. 上下游 / 邻近机会。
2. 更具体的优先级判断依据。
3. 首轮销售验证建议。
4. 明确的“不建议优先做什么”。
5. 报告生成可承接新增分析内容。

---

## 3. 范围

本任务 In Scope：

- 增强 `backend/runtime/graphs/lead_analysis.py` 中的 heuristic graph。
- 最小调整 `backend/runtime/graphs/report_generation.py`，让报告正文承接新增判断依据。
- 更新 backend tests。
- 新增质量对比 eval 记录。
- 更新 task、handoff 和 delivery 入口。

本任务 Out of Scope：

- 不接外部搜索。
- 不引入 Langfuse / OTEL。
- 不切换模型。
- 不把 `lead_analysis` 切到 LLM。
- 不新增 public endpoint。
- 不改 schema。
- 不改 Android DTO / UI。

---

## 4. 验收标准

满足以下条件可认为完成：

1. 8/8 `lead_analysis` run succeeded。
2. 8/8 `report_generation` run succeeded。
3. 8/8 report readability pass。
4. 至少 6/8 neighbor_opportunity_quality pass。
5. 用户可见字段中工程词泄漏为 0。
6. 明显幻觉总数小于 4。
7. `backend/.venv/bin/python -m pytest backend/tests` 通过。
8. `git diff --check` 通过。

---

## 5. 执行环境

- backend：`127.0.0.1:8013`
- database：`/tmp/openclaw_v1_lead_analysis_quality_followup_2026_04_25.db`
- product learning provider：腾讯云 TokenHub
- product learning model：`minimax-m2.5`
- API key：只从 `backend/.env` 读取，不打印、不写入文档

---

## 6. 计划验证

1. Unit / backend tests：
   - `analysis_scope` 仍为用户可读文案。
   - `ranking_explanations`、`recommendations`、`scenario_opportunities` 不包含 `Phase 1`、`LangGraph`、`runtime` 等工程词。
   - `scenario_opportunities` 可承载邻近 / 上下游机会。
   - `recommendations` 包含首轮销售验证建议与不优先建议。
   - report_generation 能把增强后的 lead analysis 内容带入报告。
2. Eval smoke：
   - 复用 8 个真实中文业务样例跑完整 backend API flow。
   - 记录 lead/report 状态、邻近机会质量、报告可读性和明显幻觉。

---

## 7. 实际产出

- 增强 `backend/runtime/graphs/lead_analysis.py`：
  - `scenario_opportunities` 新增邻近机会与上下游机会。
  - `ranking_explanations` 增强优先行业、客户角色和扩展顺序的判断依据。
  - `recommendations` 新增首轮销售验证建议与“不建议优先做什么”。
  - 用户可见限制说明去除工程对象表述。
- 最小调整 `backend/runtime/graphs/report_generation.py`：
  - 报告“优先行业与客户”章节承接 `ranking_explanations`，展示为“判断依据”。
  - 关键场景机会继续从 `scenario_opportunities` 承接邻近 / 上下游机会。
- 更新 backend tests，覆盖：
  - 用户可见字段不泄漏 `Phase 1`、`LangGraph`、`runtime`、`v1_langgraph_phase1`。
  - lead analysis 输出包含邻近 / 上下游机会、首轮销售验证建议和不优先建议。
  - report generation 承接判断依据、邻近机会和不优先建议。
- 新增 eval 记录：`docs/product/research/v1_lead_analysis_quality_eval_2026_04_25.md`。
- 新增 handoff：`docs/delivery/handoffs/handoff_2026_04_25_lead_analysis_quality_followup.md`。

---

## 8. 已做验证

已完成：

1. `backend/.venv/bin/python -m pytest backend/tests`
   - 结果：35 passed。
2. backend real API eval
   - DB：`/tmp/openclaw_v1_lead_analysis_quality_followup_2026_04_25.db`
   - `/health` 返回 `{"status":"ok"}`。
   - 8 个真实中文业务样例完整跑通：
     - product_learning succeeded：8/8。
     - lead_analysis succeeded：8/8。
     - report_generation succeeded：8/8。
     - neighbor_opportunity_quality pass：8/8。
     - report_readability pass：8/8。
     - 工程词泄漏：0。
     - 明显幻觉总数：0。
     - product_learning LLM token total：8981。
3. `git diff --check`
   - 结果：通过。
4. 临时 backend
   - 已停止，`127.0.0.1:8013` 已释放。

---

## 9. Handoff

见 `docs/delivery/handoffs/handoff_2026_04_25_lead_analysis_quality_followup.md`。
