# Handoff：V3 Sandbox Runtime POC

日期：2026-04-30

## 1. 变更摘要

本次实现 backend-only V3 sandbox runtime POC。

核心结果：

- 新增独立 `/v3/sandbox` API，不挂到 V2 Sales Workspace 路径。
- 新增 V3 sandbox Pydantic 模型，用于 memory、sandbox working state、customer intelligence draft 和 agent actions。
- 新增最小 LangGraph runtime loop：`load_state -> call_llm -> parse_actions -> apply_actions -> return_turn`。
- 新增 in-memory store 和可选 JSON file store。
- 真实 LLM 是运行主路径；自动化测试使用 mock TokenHub，不需要密钥。
- 用户纠错可将旧 memory 标为 `superseded`，并写入新的 `confirmed` memory。

## 2. 文件或区域

- `backend/api/v3_sandbox.py`
- `backend/api/main.py`
- `backend/api/config.py`
- `backend/runtime/v3_sandbox/`
- `backend/tests/test_v3_sandbox_runtime.py`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`
- `docs/delivery/tasks/task_2026_04_30_v3_sandbox_runtime_poc.md`

## 3. 验证

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -q`
- `backend/.venv/bin/python -m pytest backend/tests -q`
- `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_sandbox_smoke.db backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
- `curl -sS http://127.0.0.1:8013/health`
- 真实 LLM 配置 smoke：`/v3/sandbox` 三轮 turn 均返回 200，trace 连续写入。
- `git diff --check`

环境门控说明：

- Postgres 专项测试因未设置 `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` 跳过。
- 既有 V2.1 live LLM 测试因未设置 `OPENCLAW_BACKEND_RUN_LIVE_LLM_SMOKE=1` 跳过。

## 4. 已知边界

- 未新增 DB schema 或 Alembic migration。
- 未改 Android 或 Web。
- 未引入 Letta server。
- 未把 LangGraph checkpoint 当 memory 主存。
- 未把 V3 sandbox state 写入 V2 `WorkspacePatchDraft` / Draft Review / Sales Workspace Kernel。
- 未启用 CRM 生产写入、真实外部触达、不可逆导出或 production SaaS/auth/tenant。
- 真实 LLM smoke 需要本地有效 `OPENCLAW_BACKEND_LLM_API_KEY`，本次不读取或记录密钥。

## 5. 推荐下一步

建议下一步单独开放 `V3 Web /lab scaffold` 或 `V3 sandbox memory persistence design` task：

- `/lab` 可渲染 session、memory、working state、customer intelligence draft 和 trace。
- persistence design 可在 POC 经验明确后再决定是否进入正式 DB schema。
