# Task：V1 Product Learning Backend Preflight

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Product Learning Backend Preflight
- 建议路径：`docs/delivery/tasks/task_v1_product_learning_backend_preflight.md`
- 当前状态：`done`
- 优先级：P1

本任务用于在 `task_v1_product_learning_llm_phase1.md` 前补齐 backend product learning iteration 的最小运行基线，避免 LLM 接入与 Android iteration UI 继续依赖未落地的 backend contract。

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/reference/runtime-v1-observability-eval-baseline.md`
- 建议下游任务：
  1. `docs/delivery/tasks/task_v1_product_learning_llm_phase1.md`
- 停止条件：
  - 需要引入真实 LLM provider、prompt 或新 secret
  - 需要新增数据库迁移、正式业务对象或 lifecycle 状态
  - 需要改动 Android UI

---

## 2. 任务目标

在不扩大 V1 范围的前提下完成：

1. `AgentRun.runtime_metadata` 对齐最小 observability baseline
2. `POST /product-profiles/{id}/enrich` backend contract 落地
3. product learning create / enrich 维护 `round_index`
4. 后续 LLM Phase 1 可直接基于同一套 contract 进入实现

---

## 3. 范围

本任务 In Scope：

- backend schema / route / service 最小实现
- product learning run metadata baseline
- backend tests
- API contract、runtime architecture、task 与 handoff 文档同步

本任务 Out of Scope：

- 真实 LLM 接入
- Android UI 改造
- 新 product learning message / session 对象
- 新 lifecycle 状态
- 数据库迁移

---

## 4. 实际产出

- 新增 `POST /product-profiles/{id}/enrich`
- 新增 `ProductProfileEnrichRequest` / `ProductProfileEnrichResponse`
- `runtime_metadata` 补齐：
  - `provider`
  - `mode`
  - `phase`
  - `graph_name`
  - `run_type`
  - `trace_id`
  - `prompt_version`
  - `round_index`
- product learning create 首轮固定 `round_index = 0`
- product learning enrich 轮次按同一 `ProductProfile` 既有 product learning runs 递增

---

## 5. 本次定稿边界

- enrich 只承接 `supplemental_notes` 与 `trigger_source`
- enrich 当前只允许作用于 `draft` `ProductProfile`
- backend 只把补充文本追加到同一个 `ProductProfile.source_notes`
- runtime 仍只返回 typed draft payload
- 正式对象写回仍由 `backend/api/services.py` 负责
- `missing_fields` 与 `learning_stage` 仍由 backend 重算
- 当前 prompt version 仍为 `heuristic_v1`

---

## 6. 已做验证

- `backend/.venv/bin/python -m pytest backend/tests`
- `OPENCLAW_BACKEND_DATABASE_PATH=/tmp/openclaw_preflight.db backend/.venv/bin/alembic upgrade head`
- backend startup on `127.0.0.1:8013`
- `GET /health`
- 手工 API smoke：
  - `POST /product-profiles`
  - `POST /product-profiles/{id}/enrich`
  - `GET /analysis-runs/{id}`
  - `GET /product-profiles/{id}`

---

## 7. 实际结果说明

任务完成后，backend 已具备 LLM Phase 1 的 metadata 与 iteration endpoint 前置条件。下一步应继续 `task_v1_product_learning_llm_phase1.md`，不要先进入 Android iteration UI。
