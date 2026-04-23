# 阶段性交接：docs 迁移复核与旧路径心智清理

更新时间：2026-04-23

## 1. 本次改了什么

- 收口了根 `README.md`，把仓库正式定位切到 AI 销售助手 V1 主仓库
- 修正了 `docs/product/overview.md`、PRD、research、ADR 和 `jianglab_codex_ops.md` 中的旧编号目录残留
- 更新了 `docs/delivery/README.md`，明确历史 handoff 只反映当时状态
- 更新了 `docs/archive/openclaw/README.md` 与早期 handoff 的历史说明
- 新增本次清理 task，并把它纳入 `_active.md` 的已完成任务列表

---

## 2. 为什么这么定

docs 目录虽然已经迁到新结构，但当前仍有少量正式文档和仓库入口保留旧路径或旧 Android 入口叙事，会误导后续 agent 判断。

本次采用“只修权威入口和高影响文档，不重写全部历史正文”的方式，既能尽快稳定当前工作流，也能避免大规模改写历史材料造成失真。

---

## 3. 本次验证了什么

1. 复核 `AGENTS.md`、`docs/README.md`、`docs/delivery/tasks/_active.md` 的入口顺序一致
2. 用 `rg` 检查正式入口、方向文档、runbook、ADR 中的旧编号目录残留
3. 检查历史 handoff 与 archive 已增加“仅作历史参考”的隔离说明

---

## 4. 已知限制

- `docs/delivery/handoffs/` 中部分历史文档正文仍保留旧路径，这是刻意保留的历史状态
- archive 内具体历史文档未逐篇重写，只在目录级说明中隔离
- 本次没有创建新的 Android 联调 task，也没有进入任何代码实现

---

## 5. 推荐下一步

1. 基于新文档入口创建“Android 壳层最小真实数据对接” follow-up task
2. 后续所有新 task、handoff 与 runbook 只使用新 docs 路径
