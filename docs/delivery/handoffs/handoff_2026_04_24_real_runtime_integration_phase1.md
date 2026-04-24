# 阶段性交接：real runtime integration phase 1

更新时间：2026-04-24

## 1. 本次改了什么

- 将 `backend/runtime/adapter.py` 从固定 stub 改为 provider abstraction
- 新增 `backend/runtime/types.py`
- 新增两条 LangGraph graph：
  - `lead_analysis`
  - `report_generation`
- `backend/api/services.py` 切到 `langgraph` provider，但继续保留 formal object writeback 在 services 层
- `backend/pyproject.toml` 新增 `langgraph`
- 更新后端测试，验证 provider 默认值、失败路径和新 analysis/report 输出

---

## 2. 为什么这么定

- 当前 Phase 1 的目标是先替换 stub runtime，而不是一口气引入 product learning runtime、queue worker 或 observability 平台
- LangGraph 被放在 `backend/runtime/` 内，确保 backend 仍是 formal truth layer
- 当前没有现成模型/外部搜索前提，因此 Phase 1 先用受控 Python 节点生成结构化 draft，优先验证 runtime boundary

---

## 3. 本次验证了什么

1. `backend/.venv/bin/python -m pytest backend/tests`：`19 passed`
2. `python3 /home/yulin/.codex/skills/backend-local-verify/scripts/run_backend_verify.py --workspace "$PWD" --mode full`：通过
3. 手动 API flow：
   - `ProductProfile` confirm 成功
   - `lead_analysis` run 成功，`analysis_scope = v1_langgraph_phase1`
   - `report_generation` run 成功
   - 报告返回 5 个 section：产品理解摘要 / 优先行业与客户 / 关键场景机会 / 下一步建议 / 风险与限制

---

## 4. 已知限制

- 当前 LangGraph 节点逻辑仍是受控 Python 生成，不依赖外部 LLM / 搜索
- product learning runtime 仍未接入
- 当前 lifecycle 仍只有 `queued / running / succeeded / failed`
- 未引入 `Langfuse`、`MCP`、`Postgres`

---

## 5. 推荐下一步

1. 创建并执行 `task_v1_product_learning_runtime_followup.md`
2. 在 product learning runtime task 中明确 `ProductLearningRun` 与 `ready_for_confirmation` 的最终归属
