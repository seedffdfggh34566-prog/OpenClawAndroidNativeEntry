# Handoff：2026-04-25 Product Learning Backend Preflight

## 本次变更

- backend 新增 `POST /product-profiles/{id}/enrich`
- 新增 enrich 请求 / 响应 schema：
  - `ProductProfileEnrichRequest`
  - `ProductProfileEnrichResponse`
- enrich 会将 `supplemental_notes` 追加到同一个 `ProductProfile.source_notes`
- enrich 会创建新的 `run_type = product_learning` `AgentRun`
- enrich 当前只允许作用于 `draft` `ProductProfile`，非 draft 返回 `409`
- `AgentRun.runtime_metadata` 补齐 observability baseline：
  - `provider`
  - `mode`
  - `phase`
  - `graph_name`
  - `run_type`
  - `trace_id`
  - `prompt_version`
  - `round_index`
- product learning create 首轮为 `round_index = 0`
- product learning enrich 轮次按同一产品画像既有 product learning runs 递增

## 主要文件

- `backend/api/main.py`
- `backend/api/schemas.py`
- `backend/api/services.py`
- `backend/runtime/adapter.py`
- `backend/tests/test_api.py`
- `backend/tests/test_services.py`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/architecture/runtime/langgraph-runtime-architecture.md`
- `docs/delivery/tasks/task_v1_product_learning_backend_preflight.md`
- `docs/delivery/tasks/_active.md`

## 为什么这么定

- ADR-004 已冻结 enrich endpoint，本轮只是把已批准 contract 落到 backend
- LLM Phase 1 需要 `prompt_version` 与 `round_index` 才能做 heuristic vs LLM 对比
- Android iteration UI 应等待 backend contract 和 LLM 能力稳定后再承接

## 验证

- `backend/.venv/bin/python -m pytest backend/tests` -> `28 passed`
- `OPENCLAW_BACKEND_DATABASE_PATH=/tmp/openclaw_preflight.db backend/.venv/bin/alembic upgrade head`
- backend startup on `127.0.0.1:8013`
- `GET /health` -> `{"status":"ok"}`
- 手工 API smoke：
  - `POST /product-profiles`
  - `POST /product-profiles/{id}/enrich`
  - `GET /analysis-runs/{id}` for create and enrich runs
  - `GET /product-profiles/{id}`
  - result: create run `succeeded`, enrich run `succeeded`, profile version reached `3`, `learning_stage = ready_for_confirmation`

## 已知限制

- 当前仍是 heuristic product learning，不接真实 LLM
- 本轮不改 Android UI
- 本轮不新增 message timeline、session 对象、生命周期状态或数据库迁移

## 推荐下一步

1. 继续 `docs/delivery/tasks/task_v1_product_learning_llm_phase1.md`
2. 在 LLM Phase 1 中使用现有样例集记录 heuristic vs LLM 对比
