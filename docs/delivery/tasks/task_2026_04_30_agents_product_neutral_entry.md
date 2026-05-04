# Task：AGENTS.md 产品无关入口减阻

更新时间：2026-04-30

## 1. 任务定位

- 任务名称：AGENTS.md 产品无关入口减阻
- 当前状态：`done`
- 优先级：P1
- 任务类型：`workflow-docs`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 2 workflow / navigation`

---

## 2. 授权来源

用户明确确认：根 `AGENTS.md` 应作为产品无关的 repo 操作入口，不应定义具体产品内容；产品方向应由 `docs/` 内 PRD、ADR、architecture、project status 和 `_active.md` 承载。

---

## 3. 任务目标

降低正式写代码前的文档干扰：

- 将 `AGENTS.md` 从产品方向说明文件压缩为稳定 repo operating contract。
- 移除根规则中的具体 V3 产品解释。
- 保留 docs 路由、任务授权、安全、git、验证、handoff、scoped rules 和 skill 使用规则。
- 明确 `AGENTS.md` 不是产品真相源。

---

## 4. 范围

In Scope：

- 重写根 `AGENTS.md`。
- 更新 `docs/product/project_status.md` 当前任务指针。
- 更新 `_active.md` 当前任务。
- 更新 `docs/delivery/README.md` 当前入口。
- 新增 handoff。

Out of Scope：

- 修改 `app/AGENTS.md`。
- 修改 `backend/AGENTS.md`。
- 移动或删除历史 docs。
- 改 PRD / ADR / architecture 的产品语义。
- 启动任何 V3 implementation。
- 创建 Web 工程、runtime、memory schema、Android/backend 代码。

---

## 5. 实际结果说明

已完成根 `AGENTS.md` 产品无关化：

- 不再展开 V3 Memory-native、Web dual-entry、runtime memory 或 formal writeback 等产品语义。
- 当前产品方向通过 `docs/README.md`、`docs/product/project_status.md`、`docs/delivery/tasks/_active.md` 和当前 task/handoff 路由。
- 历史文档仅作为 evidence / reference，除非当前 task 明确重开。

---

## 6. 已做验证

- `git diff --check`
- `rg "Memory-native|LangGraph|formal business|Product Sales Agent|Web dual-entry|/lab|/workspace" AGENTS.md`
- `rg "Do not treat AGENTS.md as product truth|Use this file only to decide how to operate safely" AGENTS.md`
- 人工检查未声明 V3 implementation、Web implementation、MVP 或 production-ready 完成。
