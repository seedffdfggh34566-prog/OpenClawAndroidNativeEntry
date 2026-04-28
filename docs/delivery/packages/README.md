# Delivery Packages

更新时间：2026-04-28

## 1. 目录定位

本目录用于承载 delivery package 文档。

Delivery package 是执行授权边界和 task group，不是具体执行 task。它用于说明：

- package 目标
- authorization source
- auto-continue 范围
- package 内 tasks / steps
- allowed / forbidden scope
- stop conditions
- closeout / handoff 要求

具体执行 task 继续放在：

- `docs/delivery/tasks/`

---

## 2. 使用规则

- 新 package 文件应放在 `docs/delivery/packages/`。
- 新 task 文件应放在 `docs/delivery/tasks/`。
- `_active.md` 可以同时引用 current package 和 current task，但路径必须显式。
- package 不应替代 task outcome；task 不应替代 package authorization boundary。
- 普通 package / task / handoff 不得自行声明产品阶段或 milestone 完成。

---

## 3. 当前 Package

- `package_v2_1_milestone_acceptance_and_gap_closure.md`（in_progress）
- `package_v2_1_implementation_rebaseline.md`
- `package_v2_1_implementation_continuation.md`

---

## 4. 模板

新建 package 时优先使用：

- `_template.md`
