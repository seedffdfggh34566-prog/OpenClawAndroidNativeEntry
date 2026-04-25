# AI Sales Assistant Backend

最小正式后端实现，采用：

- FastAPI
- Pydantic v2
- SQLAlchemy
- SQLite
- Alembic
- pytest
- structured logging

本轮仅覆盖 V1 最小闭环，不包含鉴权、搜索、分页和真实 OpenClaw runtime 接入。

当前常用命令：

```bash
backend/.venv/bin/pip install -e backend
backend/.venv/bin/python -m pytest backend/tests
backend/.venv/bin/alembic upgrade head
backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
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

当前 product learning LLM Phase 1 默认使用腾讯云 TokenHub 普通按量 API：

```bash
OPENCLAW_BACKEND_LLM_PROVIDER=tencent_tokenhub
OPENCLAW_BACKEND_LLM_BASE_URL=https://tokenhub.tencentmaas.com/v1
OPENCLAW_BACKEND_LLM_MODEL=minimax-m2.5
OPENCLAW_BACKEND_LLM_PROMPT_VERSION=product_learning_llm_v1
```

`OPENCLAW_BACKEND_LLM_API_KEY` 只能通过服务端环境变量或 `backend/.env` 注入。不要提交 API key。
