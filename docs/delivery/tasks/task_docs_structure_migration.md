# Task：文档结构迁移到新 docs 架构

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：文档结构迁移到新 docs 架构
- 建议路径：`docs/delivery/tasks/task_docs_structure_migration.md`
- 当前状态：`done`
- 优先级：P0

本任务用于把仓库文档从旧的编号目录迁移到新的 `product / architecture / reference / how-to / adr / delivery / archive` 结构。

---

## 2. 任务目标

至少完成以下结果：

- 建立新的 docs 目录骨架
- 迁移现有正式文档到新结构
- 修正核心入口与主要内部引用
- 让 agent 工作流正式以新 docs 结构为准

---

## 3. 当前背景

仓库此前已经完成了后端优先的工作流对齐，但 `docs/` 目录仍保留旧的编号式心智模型。

这会导致：

- agent 入口和目录语义不一致
- 后续多端与后端文档难以继续扩展
- 新旧路径在 handoff / task / runbook 中长期并存

---

## 4. 范围

本任务 In Scope：

- 建新目录骨架
- 迁移现有 markdown 文件
- 更新主要入口与核心引用
- 新增目录级 README 与少量占位文件

本任务 Out of Scope：

- 代码目录重构
- 大规模重写原有文档内容
- 新增 iOS / PC 文档细节

---

## 5. 涉及文件

高概率涉及：

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/product/`
- `docs/architecture/`
- `docs/reference/`
- `docs/how-to/`
- `docs/adr/`
- `docs/delivery/`
- `docs/archive/`

---

## 6. 产出要求

至少产出以下内容：

1. 新 docs 目录树
2. 更新后的统一导航
3. 更新后的 agent 入口路径
4. 迁移 handoff

---

## 7. 验收标准

满足以下条件可认为完成：

1. 旧编号目录不再作为正式入口
2. `docs/README.md` 可正确引导到新目录
3. `AGENTS.md` 与 `docs/delivery/tasks/_active.md` 已切到新路径

---

## 8. 实际产出

本次已完成：

1. 建立新 docs 目录结构
2. 迁移现有正式文档到新结构
3. 更新 `AGENTS.md`、`docs/README.md` 与 workflow 手册
4. 新增目录级 README、`roadmap.md` 与 `glossary.md`

---

## 9. 已做验证

本次已完成以下验证：

1. 检查 `docs/` 文件树已切到新结构
2. 检查主入口文件已指向新路径
3. 检查主要旧路径引用已被更新

---

## 10. 实际结果说明

当前文档结构迁移已完成，后续任务与 handoff 应默认使用新 docs 结构。
