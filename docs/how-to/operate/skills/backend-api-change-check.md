# Skill Spec: `backend-api-change-check`

更新时间：2026-04-23

## Skill name

`backend-api-change-check`

## Purpose

对 backend API、schema 和正式对象含义变更做守门，避免实现改动先于合同与文档边界漂移；同时吸收原 `api_contract_change` 方案的 request/response、breaking change 和 smoke check 要求。

## When to trigger

适用于以下改动：

- `backend/api/main.py`
- `backend/api/schemas.py`
- `backend/api/serializers.py`
- `backend/api/services.py`
- `docs/reference/api/backend-v1-minimum-contract.md` 相关联调任务

当改动影响请求体、响应体、状态字段、错误语义或对象聚合方式时，应触发本 Skill。

## Required repo docs

- 根 `AGENTS.md`
- `backend/AGENTS.md`
- `docs/README.md`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/reference/schemas/v1-domain-model-baseline.md`
- 当前 task
- 对应 handoff

## Allowed tools / commands

- `rg`
- `git diff -- backend/ docs/reference/api/ docs/reference/schemas/`
- `backend/.venv/bin/python -m pytest backend/tests`
- `backend/.venv/bin/alembic upgrade head`
- `backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
- `curl http://127.0.0.1:8013/health`

## Expected outputs / evidence

输出应至少包括：

- 这次改动是否影响 formal contract
- 影响的是哪些 request / response model
- 影响的是字段、状态、错误语义还是对象聚合
- 这次改动是 additive、compatible 还是 breaking
- 哪些 docs 需要同步
- 已执行的验证动作
- 最小 smoke test 清单
- 是否还能保持在当前 V1 范围内

## Stop / escalate conditions

遇到以下情况应停止并升级：

- 需要重新定义正式对象语义
- 需要扩展 V1 scope
- 合同变更与 product / ADR 含义冲突
- 想通过代码实现偷偷引入未批准的新接口或新能力

## Bundled resources plan

本 Skill 后续允许补充：

- API contract diff checklist
- schema field drift checklist
- breaking change checklist
- request / response model impact checklist

本阶段不要求脚本实现。

## Non-goals

- 不替代正式 API contract 文档
- 不决定产品方向
- 不自动宣布合同已经批准
- 不替代 `backend-contract-sync`
- 不单独再拆一个 `api_contract_change` skill
