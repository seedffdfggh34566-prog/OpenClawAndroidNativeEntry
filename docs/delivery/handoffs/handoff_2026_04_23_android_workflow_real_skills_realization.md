# 阶段性交接：Android / Workflow Real Skills 落地

更新时间：2026-04-23

## 1. 本次改了什么

- 新增 4 个 repo-managed real skills：
  - `android-build-verify`
  - `android-runtime-integration-guard`
  - `android-logcat-triage`
  - `task-handoff-sync`
- 为 `android-build-verify` 增加安全验证脚本 `run_android_verify.py`
- 将 `scripts/sync_codex_skills.py` 扩展为 10 个 managed skills 的同步入口
- 更新 skills 索引与边界文档

---

## 2. 当前未做什么

- 没有修改 Android 产品代码
- 没有引入 screenshot testing
- 没有把 `android-ui-change-check` 落成 real skill
- 没有修改 `_active.md`

---

## 3. 本次验证了什么

1. 10 个 real skill source 均通过 `quick_validate.py`
2. 10 个 managed skills 已同步到 `${CODEX_HOME:-$HOME/.codex}/skills/`
3. `android-build-verify` 的 `devices` smoke 可执行
4. `adb devices` 可作为 `android-logcat-triage` 只读 smoke
5. `git diff --check` 通过

---

## 4. 推荐下一步

进入 Android 真实后端联调任务时，建议按以下顺序使用 skills：

1. `android-runtime-integration-guard`
2. `android-build-verify`
3. `android-logcat-triage`
4. `task-handoff-sync`

`android-ui-change-check` 继续作为 spec 层守门说明，等 screenshot testing 基建明确后再落成 real skill。
