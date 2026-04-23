# Android / Workflow Skills Specs

更新时间：2026-04-23

## 1. 文档定位

本目录用于承载当前仓库的 **Skill 规格层**。

这里的内容不是实际安装到 Codex 的 Skill 目录，也不是新的项目事实源，而是：

- 面向当前仓库的 Skill 设计说明
- 后续若要创建真实 Skills 的实现依据
- 帮助开发者和 agent 先把触发条件、命令边界、输出格式和停止条件说清楚

本目录中的 Skill specs 仍应服从：

1. 根 `AGENTS.md`
2. `app/AGENTS.md`
3. `docs/README.md`
4. `docs/delivery/tasks/_active.md`
5. 当前 task / handoff / runbook

---

## 2. 当前 Skill 规格总览

本轮规划覆盖以下 5 个推荐 Skills：

1. `android-build-verify`
2. `android-logcat-triage`
3. `task-handoff-sync`
4. `android-ui-change-check`
5. `android-runtime-integration-guard`

这些 Skills 都应被理解为：

- **执行增强层**
- **不是方向层**
- **不是任务优先级定义层**
- **不是架构真相层**

---

## 3. 当前优先级与成熟度

### P0：现在最适合先落地

1. `android-build-verify`
2. `task-handoff-sync`
3. `android-runtime-integration-guard`

原因：

- 当前仓库规则已经足够明确
- 当前环境已具备 `adb`、真机和相关 Gradle 任务
- 最容易直接提升 Android thread 的稳定性与收口质量

### P1：适合紧接着落地

4. `android-logcat-triage`

原因：

- 当前已经具备 `adb` 与真机条件
- 但更适合结合真实排障样本进一步优化

### P1：先做轻量版

5. `android-ui-change-check`

原因：

- 当前需要 UI 守门与证据要求
- 但当前仓库没有 `test/`、`androidTest/` 或 screenshot testing 基建
- 因此只适合先做“轻量守门版”

---

## 4. 统一模板

每个 Skill spec 都使用以下固定字段：

- `Skill name`
- `Purpose`
- `When to trigger`
- `Required repo docs`
- `Allowed tools / commands`
- `Expected outputs / evidence`
- `Stop / escalate conditions`
- `Bundled resources plan`
- `Non-goals`

这样做的目的是：

- 避免后续真正创建 Skill 时重新做设计决策
- 让不同 Skill 之间的边界可以直接比较
- 让后续脚本、引用文档和触发策略更容易统一

---

## 5. 当前文件清单

- `rollout-order.md`
- `android-build-verify.md`
- `android-logcat-triage.md`
- `task-handoff-sync.md`
- `android-ui-change-check.md`
- `android-runtime-integration-guard.md`

---

## 6. 当前使用原则

当后续 thread 需要继续推进这些 Skills 时：

1. 先读本目录中的对应 spec
2. 再确认它依赖的仓库规则和 task 文档
3. 只在明确授权后，才进入真实 Skill 目录创建或脚本实现

换句话说：

> **本目录先解决“该怎么做”，而不是立刻解决“把 Skill 放哪儿并自动触发”。**
