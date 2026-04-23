# Skill Spec: `backend-local-verify`

更新时间：2026-04-23

## Skill name

`backend-local-verify`

## Purpose

根据当前 backend 改动风险，选择最轻但足够的本地验证动作，并输出结构化验证摘要；同时吸收当前后端本地 runbook 的最小启动、迁移、健康检查与排障路径。

## When to trigger

适用于任何触及 `backend/` 的实现任务，尤其是：

- `schemas.py`、`serializers.py`、`services.py` 改动
- API endpoint 改动
- 后端启动与配置改动
- runtime 写回链路改动
- backend 本地启动、迁移、健康检查或最短排障路径需要固定化时

如果触及 runtime 边界或数据库风险区域，应先由 `backend-runtime-boundary-guard`
或 `backend-db-risk-check` 判定风险，再决定本 Skill 需要提升到哪个验证等级。

## Required repo docs

- 根 `AGENTS.md`
- `backend/AGENTS.md`
- `docs/README.md`
- 当前 task
- 对应 handoff

## Allowed tools / commands

- `backend/.venv/bin/python -m pytest backend/tests`
- `backend/.venv/bin/alembic upgrade head`
- `backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
- `curl http://127.0.0.1:8013/health`
- 真实 skill 中的 bundled script：`scripts/run_backend_verify.py`

可按风险等级选择命令，不要求每次都启动服务。

## Expected outputs / evidence

输出应至少包括：

- 本次验证等级判断
- 实际执行的命令
- 哪些通过
- 哪些失败
- 哪些跳过
- 跳过原因
- 是否还需要更高一级验证
- 若验证失败，最短排障路径是什么

## Stop / escalate conditions

遇到以下情况应停止并升级：

- 需要更高风险验证但当前环境不满足
- 触及 persistence、runtime 或环境边界，但当前 task 没有授权
- 当前验证结论依赖额外的 schema / contract 决策
- 需要把 docs-only task 扩展成后端实现 task

## Bundled resources plan

本 Skill 后续允许补充：

- 一个“验证等级 -> 命令映射”清单
- 一个低自由度验证脚本
- 一个最短 backend local runbook

本阶段已经允许真实 skill 使用 bundled script。

## Non-goals

- 不判断业务逻辑是否正确
- 不替代代码 review
- 不替代 `backend-runtime-boundary-guard`
- 不自动扩展成 CI 流水线
- 不单独再拆一个 `backend_local_runbook` skill
