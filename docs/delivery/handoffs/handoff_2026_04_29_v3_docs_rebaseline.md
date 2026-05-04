# Handoff：V3 文档重基线与入口压缩

日期：2026-04-29

## 1. 变更摘要

本次只修改非 AGENTS 文档，不改代码。

核心结果：

- 当前新方向正式定为 V3 Memory-native Sales Agent。
- V3 当前真相入口已新增 PRD、ADR 和架构文档。
- V1 / V2 文档保留为 historical validated prototype / reference only。
- `docs/delivery/README.md` 与 `_active.md` 已压缩为当前执行入口，不再把 V2.1 Android chat recovery 作为当前任务。

## 2. 已知边界

- 未修改 `AGENTS.md`、`backend/AGENTS.md` 或 `app/AGENTS.md`。
- 未实现 LangGraph runtime。
- 未接入 LangChain 或 Letta。
- 未新增 schema、migration 或 API。
- 未启动 Android UI 改造。

## 3. 验证

- `git diff --check`
- `rg "V3|Memory-native|ADR-009|ai_sales_assistant_v3_prd|implementation not started|historical" docs`
- `rg "Current delivery package|Current task|Auto-continue" docs/delivery/tasks/_active.md docs/delivery/README.md`
- `git diff --name-only -- AGENTS.md backend/AGENTS.md app/AGENTS.md`

## 4. 推荐下一步

单独讨论并精简 `AGENTS.md`。在正式 implementation 前，建议先创建 V3 runtime POC task，明确 LangChain / Tencent API、memory tools 和 backend governance 的最小验证路径。
