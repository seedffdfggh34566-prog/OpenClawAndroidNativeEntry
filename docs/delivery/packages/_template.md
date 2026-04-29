# Delivery Package: <Package Name>

更新时间：YYYY-MM-DD

## 1. Package 定位

- Package 名称：<名称>
- 建议路径：`docs/delivery/packages/<文件名>.md`
- 当前状态：`planned / in_progress / blocked / done`
- 优先级：P0 / P1 / P2
- Package 类型：`delivery / planning / guardrail / closeout`
- Authorization source：`human instruction / accepted Status Agent recommendation / _active.md auto-continue rule / current package next-package rule`
- 是否允许 package 内部 tasks / steps 连续执行：`yes / no`
- 完成后是否允许自动进入下游 package：`yes / no`
- 文档同步级别：`Level 1 task / Level 2 package / Level 3 status`

---

## 2. 目标

说明本 package 要完成的交付目标，以及它为什么应作为一个 package 而不是单个 task。

---

## 3. Package 内任务 / Steps

固定顺序：

1. ...
2. ...

---

## 4. 允许范围

允许编辑：

- ...

禁止编辑：

- ...

---

## 5. Auto-continue 条件

- ...

---

## 6. Stop Conditions

命中以下情况时停止并交回规划层：

- ...

---

## 7. Package 验收标准

满足以下条件可关闭 package：

1. ...
2. ...

---

## 8. Documentation Sync Plan

默认同步：

- package closeout
- handoff
- `_active.md`，仅当 current package / task、queue、auto-continue 或 stop conditions 变化

不默认同步：

- `docs/product/project_status.md`
- milestone review
- root / docs README

需要同步高层文档的条件：

- capability status、milestone evidence、project phase 或 gap backlog 变化
- docs navigation、目录结构或正式入口变化
- 当前 package 明确包含 status / milestone closeout

---

## 9. Package Closeout

任务完成后补充：

- 实际完成内容
- 验证结果
- handoff
- known limits
- recommended next step
