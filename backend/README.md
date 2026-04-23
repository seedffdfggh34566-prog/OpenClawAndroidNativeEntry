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
