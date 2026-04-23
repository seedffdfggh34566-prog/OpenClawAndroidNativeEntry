# Backend Skill 落地顺序

更新时间：2026-04-23

## 1. 文档定位

本文档用于给当前仓库的 backend skill specs 提供一个**推荐落地顺序**。

这里的顺序不是强制 roadmap，而是说明：

- 哪些 backend skills 现在最值得先实现
- 哪些更适合等后端进一步复杂后再补强

---

## 2. 当前推荐顺序

### P0：最适合先落地

1. `backend-task-bootstrap`
2. `backend-local-verify`
3. `backend-api-change-check`

原因：

- 当前后端 thread 更容易先失控在 task 边界、验证标准和 API/对象含义漂移
- `backend-task-bootstrap` 负责把任务、验证、handoff 先收口
- `backend-local-verify` 与 `backend-api-change-check` 是当前最直接防回归的两层

### P1：紧接着落地

4. `backend-db-risk-check`

原因：

- 当前正式后端仍以 `SQLite` 为基线
- 真正的数据库风险会在 `Postgres`、迁移、`pgvector`、DB 工具层任务中进一步升高

### P1：按需落地

5. `backend-runtime-boundary-guard`
6. `backend-contract-sync`

原因：

- runtime 边界与轻量 run lifecycle 仍需守门，但当前频率低于 task/bootstrap、verify、API check
- `backend-contract-sync` 更偏 thread 收口，不必早于前几项

---

## 3. 推荐协作关系

当前建议 backend skills 采用以下协作顺序：

1. `backend-task-bootstrap`
   - 先确定当前工作是否需要新 task、follow-up task 和验证模板
2. `backend-api-change-check`
   - 若改动影响 API / schema / object shape，先判定合同与对象语义风险
3. `backend-db-risk-check`
   - 若触及 persistence / migration / DB tooling，先判定数据库风险
4. `backend-runtime-boundary-guard`
   - 若触及 runtime / product backend 边界，再判定边界和轻量 lifecycle 风险
5. `backend-local-verify`
   - 运行最小但足够的本地验证
6. `backend-contract-sync`
   - 最后做 docs / task / handoff 收口

---

## 4. 当前不建议的做法

当前不建议：

- 一开始就把全部 backend skills 都做成重自动化工具
- 在没有 dedicated task 的情况下把 skill 扩展到部署、密钥、真实生产数据库操作
- 把 `backend-db-risk-check` 做成任意 SQL 执行器
- 再额外拆 `api_contract_change`、`schema_and_migration`、`backend_local_runbook`
- 提前新增 `agent_trace_and_eval`、`tool_registration_mcp`、`human_review_gate`

当前 repo 更适合先把 backend skill 边界固定清楚，再按真实任务频率逐个实现。
