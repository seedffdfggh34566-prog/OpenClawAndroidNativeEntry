# Task：V1 Lead Analysis LLM Phase 1

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Lead Analysis LLM Phase 1
- 建议路径：`docs/delivery/tasks/task_v1_lead_analysis_llm_phase1.md`
- 当前状态：`done`
- 优先级：P1

本任务用于在 V1 主闭环、ProductLearning LLM、usage metadata、真实中文 smoke、真实业务样例库和 lead_analysis heuristic quality follow-up 均完成后，将 `lead_analysis` 从增强 heuristic 推进到真实 LLM draft 生成。

目标是验证 LLM 是否能显著提升获客分析深度，同时继续保持后端是产品真相层。

---

## 2. 任务目标

1. `lead_analysis` 使用 Tencent TokenHub `minimax-m2.5` 生成 `LeadAnalysisDraft`。
2. LLM 输出只作为 draft，由 `backend/api/services.py` 校验并写回正式 `LeadAnalysisResult`。
3. 成功 run 的 `AgentRun.runtime_metadata` 记录 `llm_usage`。
4. 不改变 public API、不改 schema、不改 Android。
5. 复用 8 个真实中文业务样例做完整 backend API eval。

---

## 3. 范围

本任务 In Scope：

- `backend/runtime/graphs/lead_analysis.py`
- `backend/runtime/adapter.py`
- `backend/runtime/types.py`
- `backend/api/services.py`
- backend tests
- task / eval / handoff docs

本任务 Out of Scope：

- 不新增 public endpoint。
- 不改 request / response schema。
- 不改 Android DTO / UI。
- 不把 report_generation 切到 LLM。
- 不做多模型路由。
- 不接外部搜索。
- 不引入 Langfuse / OTEL。
- 不自动 fallback 到 heuristic。

---

## 4. 验收标准

1. mock tests 覆盖 lead_analysis LLM 成功、带 `<think>` 解析、非 JSON 失败和 metadata usage。
2. `backend/.venv/bin/python -m pytest backend/tests` 通过。
3. 8 个真实中文业务样例 eval：
   - 8/8 product_learning succeeded。
   - 8/8 lead_analysis succeeded。
   - 8/8 report_generation succeeded。
   - 至少 6/8 lead_analysis actionability pass。
   - 至少 6/8 neighbor_opportunity_quality pass。
   - 8/8 report_readability pass。
   - 工程词泄漏为 0。
   - 明显幻觉总数小于 4。
   - product_learning 与 lead_analysis token usage 均可记录。
4. `git diff --check` 通过。

---

## 5. 执行环境

- backend：`127.0.0.1:8013`
- database：`/tmp/openclaw_v1_lead_analysis_llm_phase1_2026_04_25.db`
- provider：腾讯云 TokenHub
- model：`minimax-m2.5`
- API key：只从 `backend/.env` 或环境变量读取，不打印、不写入文档

---

## 6. 实际产出

- `lead_analysis` 已从增强 heuristic 切换为 TokenHub LLM draft 生成。
- 默认模型继续使用 `minimax-m2.5`。
- Prompt version 固定为 `lead_analysis_llm_v1`。
- 成功 run 的 `AgentRun.runtime_metadata` 现在包含：
  - `llm_provider`
  - `llm_model`
  - `llm_base_url`
  - `llm_usage`
- `LeadAnalysisDraft` 仍由 runtime 返回，正式 `LeadAnalysisResult` 仍由 `backend/api/services.py` 写回。
- `report_generation` 未切 LLM，只被动承接 `LeadAnalysisResult`。
- 为 lead_analysis LLM 路径设置最小 60s timeout，并在 prompt 中限制单条输出长度，解决真实样例中的 TokenHub timeout。
- 更新 backend tests、runtime observability reference、API contract reference、schema reference。
- 新增 eval 记录：`docs/product/research/v1_lead_analysis_llm_eval_2026_04_25.md`。

---

## 7. 已做验证

已完成：

1. `backend/.venv/bin/python -m pytest backend/tests`
   - 39 passed。
2. `git diff --check`
   - 通过。
3. backend real API eval
   - DB：`/tmp/openclaw_v1_lead_analysis_llm_phase1_2026_04_25.db`
   - 8 个真实中文业务样例完整跑通。
   - product_learning succeeded：8/8。
   - lead_analysis succeeded：8/8。
   - report_generation succeeded：8/8。
   - lead_analysis actionability pass：8/8。
   - neighbor_opportunity_quality pass：8/8。
   - report_readability pass：8/8。
   - 工程词泄漏：0。
   - 明显幻觉总数：0。
   - product_learning token total：9222。
   - lead_analysis token total：15286。
4. timeout 修复验证
   - sample 08 初始两次 lead_analysis timeout。
   - 调整 lead_analysis LLM timeout 与 prompt 输出长度后，复用同一 ProductProfile 重试成功。
5. 临时 backend
   - 已停止，`127.0.0.1:8013` 已释放。

---

## 8. Handoff

见 `docs/delivery/handoffs/handoff_2026_04_25_lead_analysis_llm_phase1.md`。
