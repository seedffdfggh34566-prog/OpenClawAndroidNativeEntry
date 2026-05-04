# Handoff：V3 Web 双入口方向沉淀

日期：2026-04-30

## 1. 变更摘要

本次只做文档方向沉淀，不改代码、不新增依赖。

核心结果：

- 新增 `docs/architecture/v3/web-dual-entry-prototype.md`。
- V3 Web 方向明确为一个 Web 工程、两个入口：`/lab` 和 `/workspace`。
- `/lab` 面向内部开发者、产品测试和 Dev Agent 自动化验证。
- `/workspace` 面向真实销售用户 Web 雏形。
- App 仍是长期主要用户入口。
- Web 不代表 production SaaS、auth、tenant 或正式部署已启动。

## 2. 文件或区域

- `docs/architecture/v3/web-dual-entry-prototype.md`
- `docs/architecture/v3/memory-native-sales-agent.md`
- `docs/architecture/README.md`
- `docs/product/prd/ai_sales_assistant_v3_prd.md`
- `docs/product/overview.md`
- `docs/product/project_status.md`
- `docs/product/README.md`
- `docs/product/roadmap.md`
- `docs/README.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/tasks/task_2026_04_30_v3_web_dual_entry_direction.md`

## 3. 验证

- `git diff --check`
- `rg "web-dual-entry|Web dual-entry|/lab|/workspace|production Web SaaS" docs`

## 4. 已知边界

- 未创建 `web/` 工程。
- 未选择 Web framework。
- 未新增 npm / Playwright 依赖。
- 未实现 V3 runtime、memory API 或 Web UI。
- 未改变 Android App 作为长期主要入口的策略。

## 5. 推荐下一步

如果要正式开始 Web implementation，建议新开任务：`V3 Web dual-entry scaffold`。

该任务应先明确：

- framework：可优先评估 Vite + React + TypeScript，但本次未冻结选型。
- route：`/lab` 与 `/workspace`。
- shared area：API client、domain types、conversation state、memory rendering。
- validation：本地 dev server + Playwright smoke。
- scope：首版只接已有 Sales Workspace API，不启动 auth / tenant / production deployment。
