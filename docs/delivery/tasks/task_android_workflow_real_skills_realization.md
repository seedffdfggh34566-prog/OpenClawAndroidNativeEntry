# Task：Android / Workflow Real Skills 落地

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：Android / Workflow Real Skills 落地
- 建议路径：`docs/delivery/tasks/task_android_workflow_real_skills_realization.md`
- 当前状态：`done`
- 优先级：P1

本任务用于把当前 Android / workflow skill specs 中最适合立刻使用的部分落成 repo-managed real skills，并同步安装到本机 Codex skills 目录。

---

## 2. 任务目标

至少完成以下结果：

- `android-build-verify` 落成 real skill
- `android-runtime-integration-guard` 落成 real skill
- `android-logcat-triage` 落成 real skill
- `task-handoff-sync` 落成 real skill
- `android-ui-change-check` 保留为 spec，不误宣称 screenshot testing 已可用

---

## 3. 范围

本任务 In Scope：

- 新增 4 个 real skill source
- 为 `android-build-verify` 增加安全验证脚本
- 扩展 `scripts/sync_codex_skills.py` 为 managed skills 同步入口
- 更新 skills 索引与边界说明
- 同步安装到本机 Codex skills 目录

本任务 Out of Scope：

- 修改 Android 产品代码
- 新增 screenshot testing 基建
- 将 `android-ui-change-check` 落成 real skill
- 修改当前正式活跃任务 `_active.md`

---

## 4. 实际产出

本次已完成以下产出：

1. 新增 `docs/how-to/operate/skills-src/android-build-verify/`
2. 新增 `docs/how-to/operate/skills-src/android-runtime-integration-guard/`
3. 新增 `docs/how-to/operate/skills-src/android-logcat-triage/`
4. 新增 `docs/how-to/operate/skills-src/task-handoff-sync/`
5. 扩展 `scripts/sync_codex_skills.py`，默认同步 10 个 repo-managed skills
6. 更新 skills 索引与边界说明

---

## 5. 已做验证

本次已完成以下验证：

1. 运行 10 个 real skill source 的 `quick_validate.py`
2. 运行 `scripts/sync_codex_skills.py`
3. 确认 `${CODEX_HOME:-$HOME/.codex}/skills/` 下存在 10 个 repo-managed skills
4. 运行 `android-build-verify` bundled script 的 `devices` smoke
5. 运行 `adb devices` 作为 `android-logcat-triage` 只读 smoke
6. 运行 `git diff --check`

---

## 6. 下一步衔接

后续进入 Android 真实后端联调任务时，优先使用：

1. `android-runtime-integration-guard`
2. `android-build-verify`
3. `android-logcat-triage`
4. `task-handoff-sync`

若未来引入 screenshot testing，再考虑将 `android-ui-change-check` 落成 real skill。
