# Task：后端工具栈基础设施落地（Phase 1 + Phase 2 基础）

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：后端工具栈基础设施落地（Phase 1 + Phase 2 基础）
- 建议路径：`docs/delivery/tasks/task_backend_tooling_foundation_phase1_phase2.md`
- 当前状态：`done`
- 优先级：P1

本任务用于在不进入 Postgres、Langfuse、LangGraph、MCP 正式接入的前提下，先完成 backend 当前最该落地的基础设施：`pytest`、结构化日志、Alembic baseline 和新的数据库配置入口。

---

## 2. 任务目标

完成一组能直接改善当前 backend 开发体验和可维护性的基础设施变更，至少满足：

- `pytest` 成为默认测试入口
- backend 至少具备 schema / service / persistence / API smoke 的最小测试面
- backend 已有标准库 JSON structured logging
- Alembic 已接入并具备 baseline revision
- 配置层已支持 `OPENCLAW_BACKEND_DATABASE_URL`

---

## 3. 当前背景

当前仓库 backend 已经有最小正式实现，但仍存在几个明显缺口：

- 默认测试入口仍停留在 `unittest`
- 只有 API 级 smoke/integration 测试
- 数据库 schema 历史仍由 `create_all()` 隐式承担
- 日志仍缺少结构化上下文

因此，本轮更适合先补“开发底盘”，而不是直接推进 Postgres、Langfuse 或真实 runtime 编排。

---

## 4. 范围

本任务 In Scope：

- 新增 `pytest` 依赖与默认配置
- 新增 schema / services / persistence tests
- 接入标准库 JSON structured logging
- 新增 Alembic 配置、env 与 baseline revision
- 新增 `OPENCLAW_BACKEND_DATABASE_URL` 配置入口
- 同步 backend 规则与 workflow 文档

本任务 Out of Scope：

- 接入 `Postgres`
- 接入 `Langfuse`
- 接入 `LangGraph`
- 接入 `MCP`
- 接入 `pgvector`
- 接入 `MCP Toolbox for Databases`

---

## 5. 涉及文件

高概率涉及：

- `backend/pyproject.toml`
- `backend/api/config.py`
- `backend/api/database.py`
- `backend/api/main.py`
- `backend/api/services.py`
- `backend/api/logging_utils.py`
- `backend/alembic/*`
- `backend/tests/*`
- `backend/README.md`
- `backend/AGENTS.md`
- `docs/how-to/operate/codex_backend_first_workflow.md`

参考文件：

- `docs/architecture/backend/backend-agent-stack-phased-adoption.md`
- `docs/delivery/tasks/task_v1_backend_minimum_implementation.md`
- `docs/delivery/handoffs/handoff_2026_04_23_v1_backend_minimum_implementation.md`

---

## 6. 产出要求

至少应产出：

1. `pytest` 默认测试入口
2. 新的 backend 最小测试面
3. JSON structured logging 基础设施
4. Alembic baseline 与迁移入口
5. 新的 DB URL 配置入口
6. 对应 task / handoff 与 workflow 文档更新

---

## 7. 验收标准

满足以下条件可认为完成：

1. `backend/.venv/bin/python -m pytest backend/tests` 可跑通
2. 至少新增 1 组 schema、1 组 service、1 组 persistence tests
3. backend 启动与请求/运行日志为结构化 JSON
4. `alembic upgrade head` 可在空库执行
5. `alembic check` 可用于 schema drift 检查

---

## 8. 推荐执行顺序

建议执行顺序：

1. 更新依赖与配置入口
2. 接入 structured logging
3. 接入 Alembic baseline
4. 补 pytest fixtures 与新增测试
5. 同步 backend rules / workflow docs
6. 运行文档与命令层验证

---

## 9. 风险与注意事项

- 不要误把本任务扩展成 Postgres 迁移
- 不要在没有 Langfuse SDK 的情况下宣称 observability 已接入
- 不要因为加了 Alembic 就直接修改 repo 中已有 `backend/data/app.db`

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. 单独新建 follow-up task 做 `SQLite -> Postgres`
2. 单独新建 follow-up task 做 `Langfuse` tracing

---

## 11. 实际产出

本次已完成以下产出：

1. 新增 `pytest` 依赖与默认配置
2. 新增 `conftest.py`、`test_schemas.py`、`test_services.py`、`test_persistence.py`
3. 新增 `backend/api/logging_utils.py`
4. 新增 `alembic.ini` 与 `backend/alembic/` baseline
5. 新增 `OPENCLAW_BACKEND_DATABASE_URL` 与日志 / Langfuse 预留配置项
6. 同步 backend rules / workflow / skill specs
7. 将 Python 生成物从 Git 跟踪中移除，并由 `.gitignore` 统一忽略

---

## 12. 本次定稿边界

本次明确采用以下边界：

- 真正落地的只有 `pytest`、structured logging、Alembic baseline、配置入口补强
- `Langfuse` 只做配置与后续接入预留，没有真正接 SDK
- `Postgres`、`LangGraph`、`MCP`、`pgvector`、`MCP Toolbox` 仍保持 follow-up 状态

---

## 13. 已做验证

本次已完成以下验证：

1. 安装并刷新 backend 依赖
2. 运行 `backend/.venv/bin/python -m pytest backend/tests`
3. 在临时 SQLite 数据库上运行 `backend/.venv/bin/alembic upgrade head`
4. 在临时 SQLite 数据库上运行 `backend/.venv/bin/alembic check`
5. 运行 `git diff --check`
6. 确认 `__pycache__`、`.pyc`、`*.egg-info/` 不再出现在 `git status` 中

---

## 14. 实际结果说明

当前本任务已满足原验收目标：

1. backend 已切到 `pytest` 默认测试入口
2. 最小测试面已从单一 API smoke 扩展到 schema / service / persistence / API smoke
3. backend 已具备结构化 JSON 日志基础设施
4. Alembic 已成为正式 schema 历史管理入口
