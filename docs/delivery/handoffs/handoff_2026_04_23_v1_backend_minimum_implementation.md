# 阶段性交接：V1 后端最小实现

更新时间：2026-04-23

## 1. 本次改了什么

本次完成了 AI 销售助手 V1 的最小正式后端实现：

- 新增 `backend/` Python 项目骨架
- 新增 FastAPI 应用入口与 `/health`
- 新增 SQLite 持久化与 4 个正式对象模型
- 实现 6 个已冻结接口
- 新增 stub runtime 适配层
- 新增后端测试用例
- 补充本地启动与验证命令

核心代码范围包括：

- `backend/api/`
- `backend/runtime/`
- `backend/tests/`
- `backend/pyproject.toml`

---

## 2. 为什么这么定

当前对象基线、Android 壳层和 API contract 都已冻结，后端已成为当前最关键的执行缺口。

本次采用 `Python + FastAPI + SQLite + stub runtime` 的组合，原因是：

- 搭建和迭代速度快
- 便于先把正式对象主真相与 API 边界落地
- 不会把真实 runtime 接入复杂度和正式后端落地绑死在同一任务中

---

## 3. 本次验证了什么

1. 运行 `backend/.venv/bin/python -m unittest backend.tests.test_api`，5 个测试全部通过
2. 运行 `backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
3. 手工调用 `/health` 返回正常
4. 手工跑通 `ProductProfile -> lead_analysis -> report_generation -> /history` 的 smoke test

---

## 4. 已知限制

- 当前 runtime 仍是 stub，不是真实 OpenClaw runtime
- 当前没有鉴权、分页、搜索和多租户
- 当前对 `draft` `ProductProfile` 的 `lead_analysis` 放宽仅服务开发阶段可运行，不代表正式 contract 放宽
- Android 端仍未切到真实后端

---

## 5. 推荐下一步

1. 创建并执行“Android 壳层最小真实数据对接” follow-up task
2. 在客户端真实联调稳定后，再拆“真实 OpenClaw runtime 接入” task
