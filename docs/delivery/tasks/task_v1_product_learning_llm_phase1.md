# Task：V1 Product Learning LLM Phase 1

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Product Learning LLM Phase 1
- 建议路径：`docs/delivery/tasks/task_v1_product_learning_llm_phase1.md`
- 当前状态：`done`
- 优先级：P1

本任务用于在 iteration contract 和 observability baseline 明确后，把当前 heuristic `product_learning_graph` 切换到真实 LLM 驱动，实现 V1 product learning 的第一轮真实能力验证。

当前模型决策已补充到：

- `docs/reference/runtime-v1-llm-provider-selection.md`

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/task_v1_runtime_observability_eval_baseline.md`
- 建议下游任务：
  1. `docs/delivery/tasks/task_v1_android_product_learning_iteration_ui.md`
  2. 视结果再拆 prompt / eval / follow-up
- 停止条件：
  - 需要改变正式 API 或对象模型
  - 需要新增生命周期状态或基础设施
  - 需要把本任务扩大成完整 multi-agent / memory 平台

---

## 2. 任务目标

在保持 backend truth layer 不变的前提下，实现：

1. `product_learning_graph` 从 heuristic 切换到真实 LLM draft 生成
2. 仍由 backend 做 canonical `missing_fields` 和 `learning_stage` 判定
3. 仍复用 `AgentRun`
4. 样例集上的质量可比 heuristic 更好

---

## 3. 当前背景

当前 product learning 已经有：

- `POST /product-profiles` -> `product_learning` `AgentRun`
- LangGraph graph
- 同对象写回
- `learning_stage`

但其核心生成逻辑仍是受控 Python heuristic，因此只能验证执行边界，不能验证真实 AI 产品价值。

本任务就是将“可运行骨架”推进到“可评估真实能力”。

---

## 4. 范围

本任务 In Scope：

- `product_learning_graph` 的 LLM draft 生成
- typed output schema
- prompt / input context 最小实现
- 腾讯云 TokenHub 普通按量 API OpenAI-compatible 调用接入
- 默认使用 `minimax-m2.5` 做第一轮 product learning baseline
- 测试与样例验证
- 必要文档与 handoff 更新

本任务 Out of Scope：

- 多轮聊天协议
- 长期记忆
- `waiting_for_user / paused / resumed`
- 新 public endpoint
- Android 大规模 UI 改造
- analysis/report 的 LLM 策略重写

---

## 5. 涉及文件

高概率涉及：

- `backend/runtime/graphs/product_learning.py`
- `backend/runtime/types.py`
- `backend/runtime/adapter.py`
- `backend/api/services.py`
- `backend/tests/*`
- `docs/architecture/runtime/langgraph-runtime-architecture.md`
- `docs/reference/api/backend-v1-minimum-contract.md`

参考文件：

- `docs/delivery/tasks/task_v1_product_learning_runtime_followup.md`
- `docs/delivery/tasks/task_v1_runtime_observability_eval_baseline.md`
- `docs/reference/runtime-v1-llm-provider-selection.md`

---

## 5.1 当前 Provider / Model 决策

本任务第一轮真实 LLM 接入采用：

- provider：`tencent_tokenhub`
- base URL：`https://tokenhub.tencentmaas.com/v1`
- chat completions URL：`https://tokenhub.tencentmaas.com/v1/chat/completions`
- default model：`minimax-m2.5`
- prompt version：`product_learning_llm_v1`

不使用 `auto` 作为 baseline，因为自动路由不利于样例对比和质量归因。

`kimi-k2.5` 不作为第一轮默认模型，但应作为第二轮对照模型保留。如果 `minimax-m2.5` 在 JSON 稳定性、字段质量或幻觉控制上不达标，再用同一 prompt / schema 跑 `kimi-k2.5` 对比。

`glm-5` 作为结构化稳定性兜底对照模型。

推荐实现配置名：

```bash
OPENCLAW_BACKEND_LLM_PROVIDER=tencent_tokenhub
OPENCLAW_BACKEND_LLM_BASE_URL=https://tokenhub.tencentmaas.com/v1
OPENCLAW_BACKEND_LLM_MODEL=minimax-m2.5
OPENCLAW_BACKEND_LLM_API_KEY=<provided-by-human>
OPENCLAW_BACKEND_LLM_PROMPT_VERSION=product_learning_llm_v1
```

API Key 只能存在于 backend/server 运行环境，不允许进入 Android 客户端或 Git。

Token Plan 企业版不作为本阶段默认方案，只作为后续用量稳定后的成本优化候选。

---

## 5.2 Human 前置动作

在实现真实调用前，human 需要完成：

1. 进入 TokenHub 控制台：`https://console.cloud.tencent.com/tokenhub/`。
2. 在模型广场 `https://console.cloud.tencent.com/tokenhub/models` 开通或确认普通按量 API 可用。
3. 可先领取新用户免费体验额度；额度不足后按普通语言模型 token 后付费计量。
4. 在 API Key 管理 `https://console.cloud.tencent.com/tokenhub/apikey` 创建普通 TokenHub API Key，建议命名为 `openclaw-v1-product-learning-dev`。
5. 该 Key 至少授权 `MiniMax-M2.5`；建议同时授权 `Kimi-K2.5` 和 `GLM-5`，便于后续同 prompt 对照。
6. 将 API Key 通过服务器环境变量或 secret 注入，不写入仓库。
7. 告知执行 agent：key 已在目标运行环境就绪，以及可用 model ids。

---

## 6. 产出要求

至少应产出：

1. 一份真实 LLM 驱动的 product learning draft 生成实现
2. 一套受控 prompt / schema / validation 方案
3. 与 heuristic 的最小对比结果
4. `minimax-m2.5` 第一轮样例结果
5. handoff 与验证记录

---

## 7. 验收标准

满足以下条件可认为完成：

1. `product_learning_graph` 不再只依赖 heuristic 生成 draft
2. 输出仍通过 typed schema 校验
3. backend 仍保留 `missing_fields` 和 `learning_stage` 的最终所有权
4. 样例集下的字段质量优于或不差于 heuristic baseline
5. 失败时 `AgentRun` 和日志可定位问题
6. runtime metadata 可定位 `tencent_tokenhub`、`minimax-m2.5` 与 `product_learning_llm_v1`
7. `backend/.venv/bin/python -m pytest backend/tests` 通过

---

## 8. 推荐执行顺序

建议执行顺序：

1. 先基于 iteration contract 收紧输入输出
2. 确认 human 已提供腾讯云 TokenHub API Key
3. 接入 `minimax-m2.5` draft 生成
4. 保持 backend canonical 判定不变
5. 对样例集做 heuristic vs `minimax-m2.5` 最小对比
6. 如 `minimax-m2.5` 不达标，再对照 `kimi-k2.5` / `glm-5`
7. 更新 docs / handoff / task 状态

---

## 9. 风险与注意事项

- 不要让 LLM 直接决定正式对象状态
- 不要让 prompt 逻辑替代 backend 规则
- 不要把腾讯云 API Key 写进 Git、Android 客户端或 task / handoff 文档
- 不要用 `auto` 做本任务的质量 baseline
- 若质量显著不稳定，应先停在 prompt / schema 调整，不要顺手扩生命周期

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. `docs/delivery/tasks/task_v1_android_product_learning_iteration_ui.md`
2. 若产品价值已显著改善，再考虑 product learning public endpoint follow-up

---

## 11. 实际产出

- 新增腾讯云 TokenHub 普通按量 API 最小 client，使用现有 `httpx`，不引入 OpenAI SDK。
- `product_learning_graph` 已从 heuristic draft 生成切到 LLM prompt + JSON 解析 + `ProductLearningDraft` typed validation。
- 支持剥离 MiniMax 可能返回的 `<think>...</think>` 与 markdown code fence，再提取 JSON object。
- Runtime metadata 对 `product_learning` 写入：
  - `prompt_version=product_learning_llm_v1`
  - `llm_provider=tencent_tokenhub`
  - `llm_model=minimax-m2.5`
  - `llm_base_url=https://tokenhub.tencentmaas.com/v1`
- `.gitignore` 已忽略 `backend/.env` 与 `backend/.env.*`，避免误提交 API key。
- Backend tests 已通过 mock TokenHub completion 覆盖成功路径和失败路径。

---

## 12. 本次定稿边界

- 未新增 public endpoint。
- 未新增 AgentRun lifecycle 状态。
- 未改变 ProductProfile 正式写回所有权：runtime 仍只返回 typed draft，`backend/api/services.py` 继续负责正式对象写回、版本递增、`missing_fields` 与 `learning_stage`。
- 未接入 Token Plan；当前仍按普通 TokenHub 按量 API 配置。
- 未做 `kimi-k2.5` / `glm-5` 自动路由。

---

## 13. 已做验证

已完成：

1. `backend/.venv/bin/python -m compileall backend/api backend/runtime backend/tests`
2. `backend/.venv/bin/python -m pytest backend/tests`
   - 结果：`35 passed`
3. `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_llm_phase1_verify.db backend/.venv/bin/alembic upgrade head`
4. `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_llm_phase1_smoke.db backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
5. `curl -sS http://127.0.0.1:8013/health`
   - 结果：`{"status":"ok"}`
6. 本地 mock TokenHub API flow：
   - mock TokenHub：`http://127.0.0.1:18081/v1/chat/completions`
   - backend：`OPENCLAW_BACKEND_LLM_BASE_URL=http://127.0.0.1:18081/v1 ... uvicorn ... --port 8014`
   - `POST /product-profiles` -> `GET /analysis-runs/{id}`
   - 结果：`AgentRun.status=succeeded`、`learning_stage=ready_for_confirmation`、metadata 包含 `prompt_version=product_learning_llm_v1` 与 `llm_model=minimax-m2.5`
7. 真实 TokenHub smoke：
   - 使用 `backend/.env` 中的真实 API key
   - `POST /product-profiles` -> `GET /analysis-runs/{id}` -> `GET /product-profiles/{id}`
   - 结果：`AgentRun.status=succeeded`、`learning_stage=ready_for_confirmation`、`missing_fields=[]`
8. 真实 3 样例 `minimax-m2.5` eval：
   - 结果：3/3 `AgentRun.status=succeeded`
   - 结果：3/3 required fields filled `4/4`
   - 结果：3/3 `learning_stage=ready_for_confirmation`

---

## 14. 实际结果说明

代码实现已完成并通过本地 mock 验证、真实 TokenHub smoke 与 3 样例 eval。当前真实 LLM 输出已达到 V1 product learning Phase 1 可用标准，可进入 Android product learning iteration UI。

最小 eval 记录：

| sample_id | run_type | prompt_version | round_index | required_fields_filled | ready_stage_judgement | hallucination_count | review_note |
|---|---|---|---:|---|---|---:|---|
| sample_a | product_learning | heuristic_v1 | 0 | 4/4 | match | 0 | 旧 heuristic 能补齐字段，但表达较模板化 |
| sample_b | product_learning | heuristic_v1 | 0 | 4/4 | too_early | 1 | 制造业样例容易被旧 heuristic 归到泛企业服务 |
| sample_c | product_learning | heuristic_v1 | 0 | 4/4 | match | 0 | 旧 heuristic 能补齐字段，但零售行业表达较浅 |
| sample_a | product_learning | product_learning_llm_v1 | 0 | 4/4 | match | 1 | 目标客户、场景、痛点完整；部分行业归类偏 SaaS / 互联网，需要后续 prompt 收敛 |
| sample_b | product_learning | product_learning_llm_v1 | 0 | 4/4 | match | 0 | 制造业、设备主管、巡检维修场景识别明显优于 heuristic |
| sample_c | product_learning | product_learning_llm_v1 | 0 | 4/4 | match | 0 | 连锁零售、门店运营和异常处理表达完整，限制项合理 |
