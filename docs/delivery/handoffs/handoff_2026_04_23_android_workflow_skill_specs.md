# 阶段性交接：Android / workflow Skills 规格层设计

更新时间：2026-04-23

## 1. 本次改了什么

- 新增 `docs/how-to/operate/skills/README.md`
- 新增 `docs/how-to/operate/skills/rollout-order.md`
- 新增 5 份独立 Skill specs
- 更新 `docs/how-to/operate/agent_skills_boundary_and_index.md`
- 更新 `docs/how-to/README.md`
- 新增本 task 记录

---

## 2. 为什么这么定

- 当前仓库已经形成规则源和事实源分层，适合先补 Skill 规格层
- 当前环境已具备 `adb`、真机和关键 Gradle 任务，说明部分 Skills 已具备落地条件
- 当前没有 `test/`、`androidTest/` 或截图测试基建，因此 `android-ui-change-check` 只能先做轻量版
- 当前最稳妥的策略是先把 5 个 Skills 的边界、依赖关系和落地顺序固定下来

---

## 3. 本次验证了什么

1. 确认 `adb` 可用，且当前有一台真机在线
2. 确认 `:app:assembleDebug`、`:app:lintDebug`、`:app:testDebugUnitTest`、`:app:connectedDebugAndroidTest` 等任务存在
3. 确认当前 `app/` 没有 `test/`、`androidTest/` 与 screenshot testing 基建
4. 运行 `git diff --check`，确认本次文档改动无格式问题

---

## 4. 已知限制

- 本次没有创建真实 Skill 目录
- 本次没有编写复杂执行脚本
- `android-logcat-triage` 和 `android-ui-change-check` 后续仍适合结合真实样本进一步细化

---

## 5. 推荐下一步

1. 先实现 `android-build-verify`
2. 再实现 `task-handoff-sync`
3. 再实现 `android-runtime-integration-guard`
