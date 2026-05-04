# Task：V3 文档重基线与入口压缩

更新时间：2026-04-29

## 1. 任务定位

- 任务名称：V3 文档重基线与入口压缩
- 当前状态：`done`
- 优先级：P0
- 任务类型：`planning`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 3 status / navigation`

---

## 2. 任务目标

将当前新方向正式定为 V3 Memory-native Sales Agent，并压缩非 AGENTS 文档入口，避免 Dev Agent 继续被旧 V2.1 Android / PatchDraft / conservative memory gate 口径误导。

---

## 3. 范围

In Scope：

- 新增 V3 PRD、ADR 和架构入口。
- 更新 docs / product / architecture / adr / delivery 当前入口。
- 标注旧 V2 runtime contract 的范围。
- 保留 V1 / V2 历史资产，不批量改历史 task / handoff。

Out of Scope：

- 修改 `AGENTS.md` 或任何 scoped `AGENTS.md`。
- 代码实现。
- 依赖接入。
- DB schema / migration。
- API contract 冻结。
- Android UI contract。

---

## 4. 实际结果说明

已完成 V3 docs rebaseline。当前 V3 是 accepted direction / implementation not started。后续 implementation 需单独开放 task。

---

## 5. 已做验证

- `git diff --check`
- `rg "V3|Memory-native|ADR-009|ai_sales_assistant_v3_prd|implementation not started|historical" docs`
- `rg "Current delivery package|Current task|Auto-continue" docs/delivery/tasks/_active.md docs/delivery/README.md`
- `git diff --name-only -- AGENTS.md backend/AGENTS.md app/AGENTS.md`
