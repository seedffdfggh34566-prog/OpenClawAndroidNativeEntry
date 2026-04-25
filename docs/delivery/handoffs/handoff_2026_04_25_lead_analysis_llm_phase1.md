# Handoff：V1 Lead Analysis LLM Phase 1

日期：2026-04-25

## 变更内容

- 将 `lead_analysis` 切换为 TokenHub `minimax-m2.5` LLM draft 生成。
- 新增内部结果对象 `LeadAnalysisDraftResult`，用于把 draft 和 `runtime_metadata` 一起返回给 service 层。
- `backend/api/services.py` 继续负责正式 `LeadAnalysisResult` 写回，并合并 `llm_usage`。
- `AgentRun.runtime_metadata.prompt_version`：
  - `lead_analysis` 改为 `lead_analysis_llm_v1`。
  - `report_generation` 仍为 `heuristic_v1`。
- 为 lead_analysis LLM 路径设置最小 60s timeout，并限制 prompt 输出长度。
- 更新 tests、runtime observability baseline、API contract reference、schema reference、task 和 eval 记录。

## 触达文件

- `backend/runtime/graphs/lead_analysis.py`
- `backend/runtime/adapter.py`
- `backend/runtime/types.py`
- `backend/api/services.py`
- `backend/tests/*`
- `docs/reference/runtime-v1-observability-eval-baseline.md`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/reference/schemas/v1-domain-model-baseline.md`
- `docs/product/research/v1_lead_analysis_llm_eval_2026_04_25.md`
- `docs/delivery/tasks/task_v1_lead_analysis_llm_phase1.md`

## 验证

- `backend/.venv/bin/python -m pytest backend/tests`
  - 39 passed。
- 真实 backend API eval：
  - DB：`/tmp/openclaw_v1_lead_analysis_llm_phase1_2026_04_25.db`
  - 8/8 product_learning succeeded。
  - 8/8 lead_analysis succeeded。
  - 8/8 report_generation succeeded。
  - 8/8 lead_analysis actionability pass。
  - 8/8 neighbor_opportunity_quality pass。
  - 8/8 report_readability pass。
  - 工程词泄漏：0。
  - 明显幻觉总数：0。
  - product_learning token total：9222。
  - lead_analysis token total：15286。
- `git diff --check`
  - 通过。

## 已知限制

- `lead_analysis` LLM 失败时当前仍按计划让 AgentRun failed，不自动 fallback 到 heuristic。
- 本轮不接外部搜索，因此行业证据仍来自产品画像和模型常识归纳。
- lead_analysis LLM token 成本明显高于 ProductLearning，后续商业化前应继续观察成本。
- `report_generation` 仍是 heuristic，只承接 LLM lead analysis 的结构化结果。

## 建议下一步

当前 V1 主链路已完成 ProductLearning LLM 与 LeadAnalysis LLM 两个核心智能节点。下一步建议先做 `task_v1_readiness_freeze_and_demo_acceptance.md`，冻结 V1 内测验收标准、已知限制、demo 路径和是否进入 report_generation polish，而不是继续无边界扩新能力。
