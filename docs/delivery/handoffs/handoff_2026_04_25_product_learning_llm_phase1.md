# 阶段性交接：Product Learning LLM Phase 1

更新时间：2026-04-25

## 1. 本次改了什么

- 接入腾讯云 TokenHub 普通按量 API，新增最小 `httpx` client。
- 将 `product_learning_graph` 的 draft 生成从 heuristic 改为 LLM prompt + JSON 解析 + `ProductLearningDraft` 校验。
- Runtime metadata 对 product learning 记录 `product_learning_llm_v1`、`tencent_tokenhub`、`minimax-m2.5` 和 base URL。
- 后端配置新增 LLM 环境变量入口，`.gitignore` 忽略 `backend/.env` 和 `backend/.env.*`。
- 后端测试改为 mock TokenHub，不依赖真实 API key。

---

## 2. 为什么这么定

- 当前 V1 只需要 product learning 真实 draft 能力验证，不需要多模型路由、长期记忆或新 lifecycle。
- Runtime 继续只负责 typed draft 生成；正式写回仍由 `backend/api/services.py` 完成。
- 使用普通 TokenHub 按量 API，符合当前“先小规模试验，不先购买 Token Plan”的决策。

---

## 3. 本次验证了什么

1. `backend/.venv/bin/python -m compileall backend/api backend/runtime backend/tests`
2. `backend/.venv/bin/python -m pytest backend/tests`
   - 结果：`35 passed`
3. `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_llm_phase1_verify.db backend/.venv/bin/alembic upgrade head`
4. `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_llm_phase1_smoke.db backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
5. `curl -sS http://127.0.0.1:8013/health`
   - 结果：`{"status":"ok"}`
6. 本地 mock TokenHub API flow：
   - `POST /product-profiles` 后轮询 `GET /analysis-runs/{id}`
   - 结果：`AgentRun.status=succeeded`、`learning_stage=ready_for_confirmation`
   - DB metadata 确认包含 `prompt_version=product_learning_llm_v1`、`llm_provider=tencent_tokenhub`、`llm_model=minimax-m2.5`
7. 真实 TokenHub smoke：
   - 使用 `backend/.env` 中的真实 API key
   - 结果：`AgentRun.status=succeeded`、`learning_stage=ready_for_confirmation`、`missing_fields=[]`
8. 真实 3 样例 eval：
   - 3/3 `AgentRun.status=succeeded`
   - 3/3 required fields filled `4/4`
   - 3/3 `learning_stage=ready_for_confirmation`

最小 eval 记录：

| sample_id | run_type | prompt_version | round_index | required_fields_filled | ready_stage_judgement | hallucination_count | review_note |
|---|---|---|---:|---|---|---:|---|
| sample_a | product_learning | heuristic_v1 | 0 | 4/4 | match | 0 | 旧 heuristic 能补齐字段，但表达较模板化 |
| sample_b | product_learning | heuristic_v1 | 0 | 4/4 | too_early | 1 | 制造业样例容易被旧 heuristic 归到泛企业服务 |
| sample_c | product_learning | heuristic_v1 | 0 | 4/4 | match | 0 | 旧 heuristic 能补齐字段，但零售行业表达较浅 |
| sample_a | product_learning | product_learning_llm_v1 | 0 | 4/4 | match | 1 | 目标客户、场景、痛点完整；部分行业归类偏 SaaS / 互联网，需要后续 prompt 收敛 |
| sample_b | product_learning | product_learning_llm_v1 | 0 | 4/4 | match | 0 | 制造业、设备主管、巡检维修场景识别明显优于 heuristic |
| sample_c | product_learning | product_learning_llm_v1 | 0 | 4/4 | match | 0 | 连锁零售、门店运营和异常处理表达完整，限制项合理 |

---

## 4. 已知限制

- Sample A 的行业归类仍偏 SaaS / 互联网，后续可继续收敛 prompt。
- MiniMax 返回中可能包含 `<think>...</think>`，当前实现已做剥离，但后续真实样例仍需确认输出稳定性。

---

## 5. 推荐下一步

1. 进入 `docs/delivery/tasks/task_v1_android_product_learning_iteration_ui.md`。
2. 后续如需继续提升质量，可单独拆 prompt tuning / eval follow-up。
