# AI Sales Assistant Backend

最小正式后端实现，采用：

- FastAPI
- Pydantic v2
- SQLAlchemy
- SQLite
- Postgres dev environment baseline
- Alembic
- pytest
- structured logging

V1 最小闭环已经作为 demo-ready baseline 收口。当前 V2 backend-only v0 新增
`backend/sales_workspace/`，用于验证 Sales Workspace Kernel 的结构化状态机、
WorkspacePatch、候选排序、Markdown projection 和 ContextPack Compiler。

当前 V2 已新增 no-DB FastAPI prototype endpoint，用于验证 Sales Workspace Kernel
API contract 可调用性。该 prototype 使用进程内 `InMemoryWorkspaceStore`，不是正式
persistence baseline。

当前 V2 persistence baseline design 已冻结为 Postgres / Alembic，并提供本地
Postgres dev environment。Sales Workspace persistence migration、repository layer、
显式 Postgres-backed API store 和 Draft Review persistence 已完成。当前仍不包含 Android 新 UI、
LangGraph、真实 LLM、联网搜索或 CRM pipeline。

当前常用命令：

```bash
backend/.venv/bin/pip install -e backend
backend/.venv/bin/python -m pytest backend/tests -q
backend/.venv/bin/alembic upgrade head
backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
```

Postgres dev environment：

```bash
docker compose -f compose.postgres.yml up -d
docker exec openclaw-postgres pg_isready -U openclaw -d openclaw_dev
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/alembic -c alembic.ini upgrade head
OPENCLAW_BACKEND_POSTGRES_VERIFY_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/python -m pytest backend/tests/test_postgres_dev_environment.py -q
docker compose -f compose.postgres.yml down
```

详细说明见：

- `docs/how-to/operate/postgres-dev-environment.md`

Sales Workspace Kernel v0 固定验证命令：

```bash
backend/.venv/bin/python -m pytest backend/tests/sales_workspace -q
backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py -q
backend/.venv/bin/python -m pytest backend/tests -q
```

当前环境变量入口：

- `OPENCLAW_BACKEND_DATABASE_URL`
- `OPENCLAW_BACKEND_DATABASE_PATH`
- `OPENCLAW_BACKEND_LOG_LEVEL`
- `OPENCLAW_BACKEND_LOG_JSON`
- `OPENCLAW_BACKEND_LANGFUSE_ENABLED`
- `OPENCLAW_BACKEND_LANGFUSE_PUBLIC_KEY`
- `OPENCLAW_BACKEND_LANGFUSE_SECRET_KEY`
- `OPENCLAW_BACKEND_LANGFUSE_HOST`
- `OPENCLAW_BACKEND_LLM_PROVIDER`
- `OPENCLAW_BACKEND_LLM_BASE_URL`
- `OPENCLAW_BACKEND_LLM_MODEL`
- `OPENCLAW_BACKEND_LLM_API_KEY`
- `OPENCLAW_BACKEND_LLM_PROMPT_VERSION`
- `OPENCLAW_BACKEND_LLM_TIMEOUT_SECONDS`
- `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND`
- `OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR`

当前 product learning LLM Phase 1 默认使用腾讯云 TokenHub 普通按量 API：

```bash
OPENCLAW_BACKEND_LLM_PROVIDER=tencent_tokenhub
OPENCLAW_BACKEND_LLM_BASE_URL=https://tokenhub.tencentmaas.com/v1
OPENCLAW_BACKEND_LLM_MODEL=minimax-m2.5
OPENCLAW_BACKEND_LLM_PROMPT_VERSION=product_learning_llm_v1
```

`OPENCLAW_BACKEND_LLM_API_KEY` 只能通过服务端环境变量或 `backend/.env` 注入。不要提交 API key。
