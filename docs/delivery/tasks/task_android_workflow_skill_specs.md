# Task：Android / workflow Skills 规格层设计

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：Android / workflow Skills 规格层设计
- 建议路径：`docs/delivery/tasks/task_android_workflow_skill_specs.md`
- 当前状态：`done`
- 优先级：P1

---

## 2. 任务目标

在不创建真实 Skill 目录的前提下，为当前仓库形成一套可实施的 Skill 规格层，覆盖：

- `android-build-verify`
- `android-logcat-triage`
- `task-handoff-sync`
- `android-ui-change-check`
- `android-runtime-integration-guard`

---

## 3. 当前背景

当前仓库已经完成：

- 根 `AGENTS.md` 与 `app/AGENTS.md` 分层
- Android 默认实现风格说明文档
- Skills 与 docs 的边界说明

当前还没有完成：

- 仓库内可直接引用的 Skill 规格文档
- 5 个推荐 Skills 的统一接口定义
- 这些 Skills 的固定落地顺序与成熟度分层

由于当前仓库仍是 docs-driven first，且尚未授权直接创建真实 Skill 目录，因此更适合先补“规格层”，而不是立刻实现。

---

## 4. 范围

本任务 In Scope：

- 新增一个 Skill 总索引文档
- 新增 5 份独立 Skill spec 文档
- 新增落地顺序说明
- 同步更新 Skills 边界文档与 how-to 导航
- 新增本 task 与对应 handoff

本任务 Out of Scope：

- 创建 `$CODEX_HOME/skills` 下的真实 Skills
- 编写复杂脚本
- 引入 screenshot testing 或 Android 新测试基建
- 修改 Android 产品代码

---

## 5. 涉及文件

高概率涉及：

- `docs/how-to/operate/agent_skills_boundary_and_index.md`
- `docs/how-to/operate/skills/README.md`
- `docs/how-to/operate/skills/rollout-order.md`
- `docs/how-to/operate/skills/*.md`
- `docs/how-to/README.md`
- `docs/delivery/tasks/task_android_workflow_skill_specs.md`
- `docs/delivery/handoffs/handoff_2026_04_23_android_workflow_skill_specs.md`

参考文件：

- 根 `AGENTS.md`
- `app/AGENTS.md`
- `docs/architecture/clients/android-client-implementation-constraints.md`
- `docs/delivery/tasks/_active.md`

---

## 6. 产出要求

至少应产出：

1. 一份 Skill 总索引文档
2. 一份固定落地顺序说明
3. 5 份独立 Skill specs
4. 对本次规格层设计的 task 与 handoff 记录

---

## 7. 验收标准

满足以下条件可认为完成：

1. 每个 Skill spec 都使用统一模板
2. 每个 Skill 都明确触发条件、允许命令、输出证据与停止条件
3. 5 个 Skills 的职责没有互相替代
4. 规格没有依赖当前仓库不存在的测试或截图基建
5. Skills 仍被定位为执行增强层，而不是事实源

---

## 8. 推荐执行顺序

建议执行顺序：

1. 回顾当前 `AGENTS.md` / `app/AGENTS.md` / Skills 边界文档
2. 确认 Android 工程和环境事实
3. 先写总索引和落地顺序
4. 再写 5 份独立 Skill specs
5. 最后同步导航与交接文档

---

## 9. 风险与注意事项

- 不要把本任务扩展成真实 Skill 实现任务
- 不要让 Skills 反向定义项目事实源
- 不要把 `android-ui-change-check` 写成重型截图测试方案
- 不要在没有样本前把 `android-logcat-triage` 设计得过重

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. 先实现 `android-build-verify`
2. 再实现 `task-handoff-sync`
3. 再实现 `android-runtime-integration-guard`

---

## 11. 实际产出

本次已完成以下产出：

1. 新增 `docs/how-to/operate/skills/README.md`
2. 新增 `docs/how-to/operate/skills/rollout-order.md`
3. 新增 5 份独立 Skill specs
4. 同步更新 Skills 边界文档与 how-to 导航
5. 新增本 task 与对应 handoff

---

## 12. 本次定稿边界

本次明确采用以下边界：

- 只做 repo 内 Skill 规格层
- 不创建真实 Skill 目录
- `android-ui-change-check` 固定为轻量守门版
- 只允许规划轻量脚本/参考文件，不直接实现

---

## 13. 已做验证

本次已完成以下验证：

1. 对照当前 Android 工程结构，确认当前没有 `test/`、`androidTest/`、screenshot testing 基建
2. 对照当前环境，确认 `adb` 可用且有真机在线
3. 对照 Gradle 任务，确认 `assembleDebug`、`lintDebug`、`testDebugUnitTest`、`connectedDebugAndroidTest` 等命令存在
4. 运行文档层校验命令确认 patch 无格式错误

---

## 14. 实际结果说明

当前仓库已经具备一套可实施的 Android / workflow Skill 规格层：

1. 每个 Skill 的边界已经清楚
2. 5 个 Skills 的成熟度和落地顺序已经固定
3. 后续实现真实 Skills 时不再需要重新做主要设计决策
