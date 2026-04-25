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

---

## 4. 已知限制

- Codex 当前 shell 没有 `OPENCLAW_BACKEND_LLM_API_KEY`，且 `backend/.env` 不存在，因此没有运行真实 TokenHub product learning flow。
- 用户已在 `jianglab` 终端验证 `minimax-m2.5` curl 连通，但该 key 尚未注入 Codex/backend 运行环境。
- 真实 3 样例 heuristic vs `minimax-m2.5` 人工 eval 尚未记录。
- MiniMax 返回中可能包含 `<think>...</think>`，当前实现已做剥离，但后续真实样例仍需确认输出稳定性。

---

## 5. 推荐下一步

1. Human 将 API key 注入 `backend/.env` 或启动 backend 的 shell 环境。
2. 运行真实 product profile create -> process run -> get run detail smoke。
3. 用 `runtime-v1-observability-eval-baseline.md` 的 3 个样例记录 heuristic vs `minimax-m2.5` eval 表。
4. 验证完成后将 `task_v1_product_learning_llm_phase1.md` 状态改为 `done`，再进入 Android product learning iteration UI。
