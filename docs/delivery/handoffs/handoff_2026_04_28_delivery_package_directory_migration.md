# 阶段性交接：Delivery Package Directory Migration

更新时间：2026-04-28

## 1. 本次改了什么

- 新增 `docs/delivery/packages/` 作为 delivery package 权威目录。
- 新增 `docs/delivery/packages/README.md` 和 `_template.md`。
- 将两个 package 文档从 `docs/delivery/tasks/` 迁移到 `docs/delivery/packages/`：
  - `package_v2_1_implementation_rebaseline.md`
  - `package_v2_1_implementation_continuation.md`
- 更新 `_active.md`、delivery README、相关 task / handoff / research 文档中的 package 路径引用。
- 更新 multi-agent workflow，明确 package 文件默认放 `docs/delivery/packages/`，task 文件默认放 `docs/delivery/tasks/`。

---

## 2. 为什么这么定

- package 是执行授权边界和 task group，不是具体执行 task。
- 将 package 与 task 分目录可以减少 `_active.md`、Status Agent、Execution Agent 和 Review Agent 的层级混淆。
- 当前只有两个 package 文件，直接迁移比保留兼容旧路径更清晰。

---

## 3. 本次验证了什么

已完成验证：

1. package 引用扫描
   - 结果：正式 package 路径均指向 `docs/delivery/packages/`；剩余命中为文件名、历史验证命令或本 handoff 说明。
2. package 目录检查
   - 结果：`docs/delivery/packages/` 下存在 README、模板和两个 package 文件；`docs/delivery/tasks/` 下无 `package_*.md`。
3. `git diff --check`
   - 结果：通过。

---

## 4. 已知限制

- 本次没有改 backend / Android 代码。
- 本次没有迁移 task 文件。
- 本次没有改变 `_active.md` 的 current package / current task 开放状态。
- 历史文本中只保留 package 文件名的描述仍可存在；正式路径应使用 `docs/delivery/packages/`。

---

## 5. 推荐下一步

后续新建 delivery package 时使用 `docs/delivery/packages/_template.md`。新 task 仍放在 `docs/delivery/tasks/`。
