# Task：docs 迁移复核与旧路径心智清理

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：docs 迁移复核与旧路径心智清理
- 建议路径：`docs/delivery/tasks/task_docs_migration_review_and_old_path_cleanup.md`
- 当前状态：`done`
- 优先级：P0

本任务用于在 docs 结构迁移完成后，再做一轮正式复核，清掉仍会误导 agent 的旧路径和旧 Android 入口项目叙事。

---

## 2. 任务目标

至少完成以下结果：

- 让 `AGENTS.md -> docs/README.md -> docs/delivery/tasks/_active.md` 成为唯一正式入口链路
- 清掉权威入口和高影响文档中的旧编号目录表述
- 把历史 handoff / archive 与当前正式导航隔离开

---

## 3. 当前背景

虽然 docs 已经迁到 `product / architecture / reference / how-to / adr / delivery / archive` 新结构，但当前仍存在两类残留：

- 少数正式文档仍引用旧编号目录
- 根 README 与部分历史文档仍保留过强的旧 Android 入口叙事

如果不清理，agent 在接手时仍可能误判当前正式入口和当前项目本体。

---

## 4. 范围

本任务 In Scope：

- 复核 `AGENTS.md`、`docs/README.md`、`docs/delivery/tasks/_active.md`
- 修正文档中的旧路径残留
- 压缩根 README 中的旧项目主叙事
- 给历史 handoff 与 archive 增加低成本隔离说明

本任务 Out of Scope：

- 代码目录重构
- 后端实现调整
- 重写全部历史 handoff 正文
- 新增 Android 联调实现

---

## 5. 涉及文件

高概率涉及：

- `README.md`
- `docs/product/overview.md`
- `docs/how-to/operate/jianglab_codex_ops.md`
- `docs/adr/ADR-001-backend-deployment-baseline.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/product/research/v1_reference_notes.md`
- `docs/delivery/README.md`
- `docs/archive/openclaw/README.md`

参考文件：

- `AGENTS.md`
- `docs/README.md`
- `docs/delivery/tasks/_active.md`

---

## 6. 产出要求

至少应产出：

1. 更新后的正式入口文档
2. 更新后的高优先级方向 / runbook / ADR 文案
3. 一份说明本轮清理结果的 handoff

---

## 7. 验收标准

满足以下条件可认为完成：

1. 在 `AGENTS.md`、`README.md`、`docs/product`、`docs/how-to`、`docs/adr`、`docs/delivery/README.md` 中不再出现旧编号目录路径
2. 根 `README.md` 不再把仓库主体定义为 Android Native Entry 项目
3. 历史 handoff 与 archive 已被明确标注为历史参考

---

## 8. 实际产出

本次已完成：

1. 收口根 `README.md` 的正式仓库定位
2. 更新 overview、PRD、research、ADR 与 runbook 中的旧路径残留
3. 在 delivery 与 archive 增加历史隔离说明
4. 为早期 handoff 补充迁移说明

---

## 9. 已做验证

本次已完成以下验证：

1. 用 `rg` 检查高优先级正式文档中的旧编号目录残留
2. 复核 `AGENTS.md`、`docs/README.md` 与 `docs/delivery/tasks/_active.md` 的入口顺序
3. 复核历史 handoff 与 archive 的隔离说明已落盘

---

## 10. 实际结果说明

当前正式文档入口已经稳定到新结构，旧编号目录与旧 Android 入口项目叙事只保留为历史背景，不再作为当前 agent 的默认导航来源。
