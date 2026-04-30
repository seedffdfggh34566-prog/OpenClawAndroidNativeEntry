# Task：V3 Web 双入口方向沉淀

更新时间：2026-04-30

## 1. 任务定位

- 任务名称：V3 Web 双入口方向沉淀
- 当前状态：`done`
- 优先级：P1
- 任务类型：`planning`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 2 product / architecture direction`

---

## 2. 授权来源

用户明确表示希望同时拥有：

- 内部开发者友好型 Web。
- 面向真实销售用户的 Web。
- 长期仍以 App 作为主要用户入口。

本任务只沉淀方向和后续实施边界，不启动 Web implementation。

---

## 3. 任务目标

将 V3 Web 方向从讨论结论沉淀为仓库当前文档：

- 一个 `web/` 工程。
- 两个入口：`/lab` 和 `/workspace`。
- `/lab` 面向内部开发、产品测试和 Dev Agent 自动化验证。
- `/workspace` 面向真实销售用户体验雏形。
- App-first 长期策略不变。

---

## 4. 范围

In Scope：

- 新增 V3 Web 双入口架构文档。
- 更新 V3 PRD、overview、project status、roadmap 和导航入口。
- 更新 `_active.md` 记录本次任务结果。
- 新增 handoff。

Out of Scope：

- 新增 `web/` 工程。
- 选择 React / Vite / Next 等框架。
- 新增 npm 依赖。
- 实现 Playwright 测试。
- 实现 V3 runtime / memory API。
- 实现 auth / tenant / production deployment。
- 改 Android UI。

---

## 5. 实际结果说明

已完成 V3 Web 双入口方向沉淀。Web 被定义为 V3 产品雏形和测试入口，但不改变 App-first 长期策略。

后续如需实现，应另开 Web scaffold task，明确 framework、目录、首屏范围和验证命令。

---

## 6. 已做验证

- `git diff --check`
- `rg "web-dual-entry|Web dual-entry|/lab|/workspace|production Web SaaS" docs`
- 人工检查未声明 V3 implementation done、Web implementation done、MVP done 或 production-ready。
