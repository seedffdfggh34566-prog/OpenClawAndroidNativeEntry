# Handoff：V3 Web `/lab` Scaffold

日期：2026-04-30

## 1. 变更摘要

本次实现 V3 Web `/lab` scaffold。

核心结果：

- 新增独立 `web/` 工程，使用 Vite + React + TypeScript。
- `/lab` 连接真实 backend `/v3/sandbox` API，不提供前端 mock mode。
- 页面可观察 session、messages、memory、working state、customer intelligence draft、trace/actions 和 backend 错误码。
- Vite dev proxy 将 `/api/*` 转发到本地 FastAPI `127.0.0.1:8013`。
- 新增 Playwright e2e，验证页面加载、创建 session、提交 turn、渲染 state/trace/error。

## 2. 文件或区域

- `web/`
- `.gitignore`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`
- `docs/delivery/tasks/task_2026_04_30_v3_web_lab_scaffold.md`
- `docs/product/project_status.md`
- `docs/architecture/v3/web-dual-entry-prototype.md`

## 3. 验证

- `cd web && npm install`
- `cd web && npm run build`
- `OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_lab_e2e.db OPENCLAW_BACKEND_LLM_API_KEY= backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
- `cd web && npx playwright install chromium`
- `cd web && npm run test:e2e`
- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -q`
- `git diff --check`

## 4. 已知边界

- `/workspace` 未实现。
- 未加入前端 mock mode。
- 未接 Android。
- 未新增 DB schema / migration。
- 未加入 auth / tenant / production deployment。
- 未启用 CRM 生产写入、真实外部触达、不可逆导出或 production SaaS。
- `npm install` 报告 2 个 moderate audit findings；未执行 `npm audit fix --force`，避免破坏性依赖升级。

## 5. 推荐下一步

建议下一步单独开放：

- `V3 /lab replay and seed controls`：加 demo seed、reset、replay。
- 或 `V3 sandbox memory persistence design`：基于 `/lab` 观察结果决定正式 persistence 设计。
- 或 `V3 /workspace prototype planning`：把已验证的 lab 信息转为用户可理解体验。
