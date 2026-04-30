# Skill Spec: `backend-api-change-check`

更新时间：2026-04-29

## Purpose

检查 backend API、schema、memory API、formal object writeback 和错误语义，避免 V3 contract drift 或把 runtime memory 与正式业务对象混在一起。

## When to trigger

- `backend/api/main.py`
- `backend/api/schemas.py`
- `backend/api/services.py`
- request / response / status / error shape
- memory API、runtime-to-backend contract、formal object writeback
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

- formal API contract 是否受影响
- 涉及哪些 request / response model
- additive / compatible / breaking 分类
- memory API 与 formal object writeback 是否分离
- docs / tests 需要同步什么
- 已执行或仍需执行的验证

## Stop / escalate conditions

- 未更新方向层文档却重定义正式对象含义
- 把 V3 memory update 硬塞进旧 `patch_operations` 或 V2-only contract
- 把 inferred / hypothesis memory 当成 confirmed business truth
- 未获 task / contract 授权就引入新 API capability

## Non-goals

- 不批准 API contract。
- 不决定产品方向。
- 不替代 `backend-contract-sync`。
