# 阶段性交接：后端优先的仓库与文档对齐

更新时间：2026-04-23

## 1. 本次改了什么

本次围绕“后端优先 + agent 控制平面”完成了一轮以文档为主的对齐工作：

- 新增 `docs/README.md` 作为 docs 总入口
- 新增 `docs/architecture/repository-layout.md`
- 新增 `docs/how-to/operate/codex_backend_first_workflow.md`
- 新增 `docs/delivery/tasks/_active.md`
- 新增 `docs/delivery/tasks/_template.md`
- 新增 `docs/delivery/handoffs/_template.md`
- 新增 `docs/delivery/tasks/task_backend_first_repo_and_docs_alignment.md`
- 新增 `docs/delivery/tasks/task_v1_backend_minimum_implementation.md`
- 更新 `AGENTS.md`
- 更新 `docs/delivery/README.md`
- 更新根 `README.md`

---

## 2. 为什么这么定

当前项目虽然已在文档层切换到 AI 销售助手 V1，但仓库入口、README、任务导航和 agent 执行接口仍偏向旧的 Android 入口叙事。

本次没有直接做大规模目录迁移，而是先采用“低 blast radius 的控制平面对齐”方式，原因是：

- 当前更需要让 agent 和开发者先对同一套入口达成共识
- 当前更需要给后端最小实现线程建立明确入口
- 当前还不到一次性迁移所有旧文档目录的时机

---

## 3. 本次验证了什么

1. 对照 overview、PRD、decision、runtime/data spec 与 API contract，确认本次没有改变既有产品含义
2. 检查新增 docs 入口、task 入口、模板和 runbook 之间已形成闭环
3. 检查“下一正式任务”已经明确落到 `task_v1_backend_minimum_implementation.md`

---

## 4. 已知限制

- 当前旧文档目录结构仍然保留，尚未正式迁移到 `product / architecture / reference / delivery`
- 当前只是完成了工作流与文档对齐，没有开始后端代码实现
- 根仓库名仍保留旧 Android 历史痕迹

---

## 5. 推荐下一步

1. 正式进入 `task_v1_backend_minimum_implementation.md`
2. 在最小后端实现落地后，再决定是否进入下一轮 docs 目录迁移
