# 当前活跃任务

更新时间：2026-04-23

## 1. 使用说明

本文件用于告诉开发者和 agent：

- 当前优先推进哪个正式任务
- 哪个任务只是背景材料
- 哪个任务已经完成，可以作为参考而非继续追加

进入正式开发前，建议先读本文件，再进入对应 task。

---

## 2. 当前状态

### 已完成的基础冻结任务

- `task_v1_domain_model_baseline.md`
- `task_v1_information_architecture.md`
- `task_v1_android_control_shell_refactor.md`
- `task_v1_backend_api_contract.md`
- `task_backend_first_repo_and_docs_alignment.md`
- `task_docs_structure_migration.md`
- `task_docs_migration_review_and_old_path_cleanup.md`
- `task_v1_backend_minimum_implementation.md`

这些任务当前应视为：

- 已完成
- 可引用
- 不在原文件中继续无限追加新需求

### 当前推荐的下一正式任务

- `task_v1_android_minimum_real_backend_integration.md`

推荐原因：

- 当前项目已完成最小正式后端落地
- 下一步更适合让 Android 从占位数据切到真实 `/history` 与对象详情读取
- 真实 OpenClaw runtime 接入可作为 Android 联调后的下一阶段

---

## 3. 当前执行原则

当前默认执行原则为：

1. 一次正式 thread 尽量只对应一个 task
2. 若发现是方向变化，先退出 task 执行，回到 overview / PRD / decision
3. 若只是小修订，可拆为 follow-up task，而不是继续污染已完成 task
