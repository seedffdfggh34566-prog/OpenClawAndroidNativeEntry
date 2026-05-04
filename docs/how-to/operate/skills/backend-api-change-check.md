# Skill Spec: `backend-api-change-check`

更新时间：2026-04-30

## Purpose

检查 backend API、schema、memory API、sandbox working state、customer intelligence 和错误语义，避免 V3 contract drift 或把 sandbox-first 过早写死成 formal object / PatchDraft / Kernel 流程。

## When to trigger

- `backend/api/main.py`
- `backend/api/schemas.py`
- `backend/api/services.py`
- request / response / status / error shape
- memory API、working-state API、customer-intelligence API、runtime-to-backend contract
- `docs/reference/api/`、`docs/reference/schemas/`

## Required repo docs

- 根 `AGENTS.md`
- `backend/AGENTS.md`
- `docs/README.md`
- `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
- `docs/architecture/v3/memory-native-sales-agent.md`
- 相关 API/reference docs
- 当前 task / handoff

V1/V2 contract 只作为 compatibility / historical reference。

## Expected outputs / evidence

- API contract 是否受影响
- 涉及哪些 request / response model
- additive / compatible / breaking 分类
- memory / working-state API 是否保持 sandbox-first
- docs / tests 需要同步什么
- 已执行或仍需执行的验证

## Stop / escalate conditions

- 未更新方向层文档却把 sandbox working state 重定义为 formal object
- 把 V3 memory update 硬塞进旧 `patch_operations` 或 V2-only contract
- 把 inferred / hypothesis memory 当成冻结 schema 或生产业务真相
- 未获 task / contract 授权就引入新 API capability

## Non-goals

- 不批准 API contract。
- 不决定产品方向。
- 不替代 `backend-contract-sync`。
