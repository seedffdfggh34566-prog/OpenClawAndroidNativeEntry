# 阶段性交接：Android Chinese Input Smoke Mechanism

更新时间：2026-04-25

## 1. 本次做了什么

- 新增并完成 `task_android_chinese_input_smoke_mechanism.md`。
- 新增 runbook：`docs/how-to/debug/android-chinese-input-smoke.md`。
- 将真机中文输入问题明确归类为测试输入机制问题，而不是 V1 Android / backend 业务链路问题。
- 记录短期策略：主链路 smoke 继续使用无空格 ASCII 等价样例。
- 记录正式中文自动化输入策略：后续使用测试专用 IME，并在 smoke 结束后恢复原输入法。

---

## 2. 本次验证了什么

1. `adb devices`
   - 结果：检测到真机 `f3b59f04`。
2. `adb shell settings get secure default_input_method`
   - 结果：`com.baidu.input_oppo/.ImeService`。
3. `adb shell ime list -s`
   - 结果：当前仅列出 `com.baidu.input_oppo/.ImeService`。
4. `git diff --check`
   - 结果：通过。

---

## 3. 已知限制

- 本次没有安装或启用测试 IME。
- 本次没有修改产品代码，也没有加入 debug-only 输入入口。
- 当前设备上没有现成测试输入法可切换；后续若要真实中文自动化 smoke，需要先准备可信测试 IME APK。
- `ADB_INPUT_TEXT` broadcast action 需以后续选定测试 IME 的实际文档为准。

---

## 4. 推荐下一步

1. 若需要覆盖中文输入体验，单独执行 runbook 中的测试 IME 方案。
2. 若只是验证 V1 主闭环，继续使用 ASCII 等价样例，避免把输入法问题混入业务验证。
3. 下一项产品工程优先级仍建议在真实样例评估 / prompt tuning follow-up 与 ProductLearning 页面表达 polish 中选择。
