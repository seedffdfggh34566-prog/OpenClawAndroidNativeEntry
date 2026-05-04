# Handoff：AGENTS.md 产品无关入口减阻

日期：2026-04-30

## 1. 变更摘要

本次只做文档减阻，不改代码、不移动历史文档。

核心结果：

- 根 `AGENTS.md` 被压缩为产品无关的 repo operating contract。
- 移除了根规则中的具体 V3 产品解释。
- `AGENTS.md` 明确不是产品真相源，产品方向通过 `docs/` 当前入口读取。
- 保留了授权、scope、git、secret、validation、handoff、scoped rules 和 skills 使用规则。

## 2. 文件或区域

- `AGENTS.md`
- `docs/product/project_status.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`
- `docs/delivery/tasks/task_2026_04_30_agents_product_neutral_entry.md`

## 3. 验证

- `git diff --check`
- `rg "Memory-native|LangGraph|formal business|Product Sales Agent|Web dual-entry|/lab|/workspace" AGENTS.md`
- `rg "Do not treat AGENTS.md as product truth|Use this file only to decide how to operate safely" AGENTS.md`

## 4. 已知边界

- 未修改 scoped `app/AGENTS.md` 或 `backend/AGENTS.md`。
- 未移动、删除或归档历史 docs。
- 未改 PRD / ADR / architecture 的产品语义。
- 未启动 Web、runtime、memory、Android 或 backend implementation。

## 5. 推荐下一步

正式写代码前，建议只在具体 implementation task 中补最小启动包，不再继续扩大文档重组范围。
