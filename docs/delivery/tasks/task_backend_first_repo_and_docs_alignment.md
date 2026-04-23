# Task：后端优先的仓库与文档对齐

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：后端优先的仓库与文档对齐
- 建议路径：`docs/delivery/tasks/task_backend_first_repo_and_docs_alignment.md`
- 当前状态：`done`
- 优先级：P0

本任务用于在不立刻做大规模目录迁移的前提下，把当前仓库正式调整到“后端优先、多端入口、agent 可持续推进”的工作方式上。

---

## 2. 任务目标

至少完成以下结果：

- 明确当前仓库已不再只是 Android 入口仓库
- 明确后端、runtime、数据层的边界
- 建立当前文档系统的统一入口
- 建立 active task 与模板基础设施
- 为下一步后端最小实现线程提供明确入口

---

## 3. 当前背景

当前仓库已经在产品方向上切换到 AI 销售助手 V1，也已经冻结了：

- V1 领域对象基线
- V1 信息架构
- Android 控制壳层
- V1 最小 API contract

但当前仓库仍存在以下问题：

- 仓库名和根 README 仍容易让人误解为 Android 专仓
- 文档缺少统一导航入口
- agent 虽有规则，但缺少稳定的 active task 入口和模板
- 后端加入后，仓库组织与工作流边界仍未正式收口

---

## 4. 范围

本任务 In Scope：

- 新增对齐方案 spec
- 新增 docs 总导航
- 新增当前活跃任务索引
- 新增 task / handoff 模板
- 新增后端优先阶段的 Codex runbook
- 新建下一正式任务文档
- 最小同步 AGENTS 与 README 导航

本任务 Out of Scope：

- 实现后端代码
- 整体迁移全部旧文档目录
- 大规模重写根 README
- 立即引入 iOS / PC 代码目录

---

## 5. 涉及文件

高概率涉及：

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/architecture/repository-layout.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/tasks/_template.md`
- `docs/delivery/tasks/task_backend_first_repo_and_docs_alignment.md`
- `docs/delivery/tasks/task_v1_backend_minimum_implementation.md`
- `docs/delivery/README.md`
- `docs/how-to/operate/codex_backend_first_workflow.md`
- `docs/delivery/handoffs/_template.md`
- `docs/delivery/handoffs/handoff_2026_04_23_backend_first_repo_and_docs_alignment.md`

参考文件：

- `AGENTS.md`
- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/architecture/system-context.md`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/adr/ADR-001-backend-deployment-baseline.md`

---

## 6. 产出要求

至少产出以下内容：

1. 仓库与文档调整方案
2. agent 可读的 docs 总导航
3. 当前活跃任务入口
4. 模板化 task / handoff 基线
5. 下一正式后端任务

---

## 7. 验收标准

满足以下条件可认为完成：

1. 开发者和 agent 都能快速判断当前应先读哪些文档
2. 后端优先的仓库理解和边界已被正式写入 spec
3. 当前推荐下一任务已被正式落为 task
4. 本次改动未扩展成大规模目录搬迁

---

## 8. 推荐执行顺序

建议执行顺序：

1. 回顾 AGENTS、overview、PRD、decision、spec
2. 新增仓库与文档对齐 spec
3. 新增 docs 入口与 runbook
4. 新增 active task 与模板
5. 新建下一正式任务
6. 更新 README、AGENTS、task 总览与 handoff

---

## 9. 风险与注意事项

- 不要把本任务扩展成整仓目录迁移
- 不要在未落后端 task 前直接进入实现
- 不要静默改写 human-owned 方向文档

---

## 10. 下一步衔接

本任务完成后，优先继续：

1. `task_v1_backend_minimum_implementation.md`

---

## 11. 实际产出

本次已完成以下产出：

1. 新增 `docs/README.md`
2. 新增 `docs/architecture/repository-layout.md`
3. 新增 `docs/how-to/operate/codex_backend_first_workflow.md`
4. 新增 `docs/delivery/tasks/_active.md`
5. 新增 `docs/delivery/tasks/_template.md`
6. 新增 `docs/delivery/handoffs/_template.md`
7. 新增 `docs/delivery/tasks/task_v1_backend_minimum_implementation.md`
8. 同步更新 `AGENTS.md`、`README.md` 与 `docs/delivery/README.md`

---

## 12. 本次定稿边界

本次明确采用以下边界：

- 当前仓库应被视为产品主仓库，而不是 Android 专仓
- 后端应作为独立层加入当前仓库，而不是进入 `app/`
- 旧文档结构继续有效，但开始建立新的导航与执行基础设施

本次未扩展到：

- 后端代码实现
- 全量 docs 目录迁移
- 客户端代码重构

---

## 13. 已做验证

本次已完成以下验证：

1. 对照 overview、PRD、decision、runtime/data spec 与 API contract，确认本次没有改变既有产品含义
2. 检查新增导航、模板、task 与 handoff 之间可相互引用
3. 检查当前下一任务已清晰落到 task 文件

---

## 14. 实际结果说明

当前该任务已满足原验收目标：

1. 仓库与文档的后端优先调整方案已被正式写入
2. 当前 agent 工作流入口已更清晰
3. 下一步后端正式实现线程已有可直接执行的 task
