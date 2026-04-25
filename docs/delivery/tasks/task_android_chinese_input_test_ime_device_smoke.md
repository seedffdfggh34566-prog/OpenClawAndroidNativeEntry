# Task：Android Chinese Input Test IME Device Smoke

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：Android Chinese Input Test IME Device Smoke
- 建议路径：`docs/delivery/tasks/task_android_chinese_input_test_ime_device_smoke.md`
- 当前状态：`done`
- 优先级：P2

本任务用于把真机 smoke 中的中文自动化输入从“已记录风险”推进到“已验证可用方案”。

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：
  1. 如验证成功，后续 V1 真机 smoke 可恢复使用真实中文样例。
  2. 如验证失败，记录为设备 / Android 16 / 测试 IME 兼容性问题，不回退到产品代码内置测试入口。
- 停止条件：
  - 测试 IME 无法在当前 Android 16 设备启用或切换。
  - 中文输入无法进入当前焦点输入框且无法通过 base64 broadcast 修复。
  - 需要修改 Android 产品代码或引入新的产品依赖。

---

## 2. 任务目标

在当前真机 `f3b59f04` 上安装临时测试输入法，通过 `ADB_INPUT_B64` 向 OpenClaw Android 输入框注入中文，并在验证后恢复原输入法、卸载测试输入法。

---

## 3. 当前背景

上一任务 `task_android_chinese_input_smoke_mechanism.md` 已确认：

- 当前设备直接使用 `adb shell input text "中文"` 不可靠。
- 当前设备只列出系统输入法 `com.baidu.input_oppo/.ImeService`。
- 推荐方案是使用测试专用 IME，但尚未执行真实验证。

当前设备事实：

- 设备：`f3b59f04`
- 型号：OnePlus PHK110
- Android：16 / API 36
- 原默认输入法：`com.baidu.input_oppo/.ImeService`

---

## 4. 范围

本任务 In Scope：

- 下载并临时安装 `senzhk/ADBKeyBoard` GitHub `v2.5-dev` APK。
- 记录 APK 来源、文件名、SHA-256。
- 切换到 `com.android.adbkeyboard/.AdbIME`。
- 使用 `ADB_INPUT_B64` 输入中文。
- 用 UIAutomator dump 验证中文文本进入目标输入框。
- 恢复原输入法并卸载测试 IME。
- 更新 runbook、任务结果和 handoff。

本任务 Out of Scope：

- 不修改 Android 产品代码。
- 不修改 backend。
- 不新增 Appium、Instrumentation 测试或 debug-only 输入入口。
- 不把测试 APK 提交到 Git。

---

## 5. 涉及文件

高概率涉及：

- `docs/delivery/tasks/_active.md`
- `docs/delivery/tasks/task_android_chinese_input_test_ime_device_smoke.md`
- `docs/how-to/debug/android-chinese-input-smoke.md`
- `docs/delivery/handoffs/handoff_2026_04_25_android_chinese_input_test_ime_device_smoke.md`

---

## 6. 产出要求

至少应产出：

1. 真实设备上的测试 IME 中文输入验证结果。
2. 恢复原输入法和卸载测试 IME 的证据。
3. 更新后的 runbook 与 handoff。

---

## 7. 验收标准

满足以下条件可认为完成：

1. `adb devices` 检测到真机。
2. 测试 IME 成功安装、启用并切换。
3. `ADB_INPUT_B64` 可把 `工厂设备巡检助手` 注入目标输入框。
4. UIAutomator dump 能看到该中文文本。
5. 默认输入法恢复为 `com.baidu.input_oppo/.ImeService`。
6. `com.android.adbkeyboard` 已卸载。
7. `git diff --check` 通过。

---

## 8. 推荐执行顺序

建议执行顺序：

1. 记录设备和原默认输入法。
2. 下载测试 IME APK 到 `/tmp/openclaw-adbkeyboard/` 并计算 SHA-256。
3. 安装、启用并切换测试 IME。
4. 打开 App 到可编辑输入框。
5. 通过 `ADB_INPUT_B64` 输入中文。
6. 用 UIAutomator dump 验证文本。
7. 恢复原输入法，卸载测试 IME。
8. 更新 runbook、task、handoff。

---

## 9. 风险与注意事项

- 测试 IME 会临时改变设备默认输入法，必须记录并恢复。
- 当前设备为 Android 16，因此优先使用 GitHub `v2.5-dev`，而不是旧版 F-Droid 包。
- 该 APK 只作为本机 smoke 工具，不进入 Git。

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. 后续真机 smoke 恢复使用真实中文样例。
2. 如后续需要更强自动化，再单独规划 UIAutomator / instrumentation 输入方案。

---

## 11. 实际产出

- 新增本任务文档，并把 `_active.md` 纳入本次任务历史。
- 下载并验证 `senzhk/ADBKeyBoard` GitHub `v2.5-dev` APK：
  - URL：`https://github.com/senzhk/ADBKeyBoard/releases/download/v2.5-dev/keyboardservice-debug.apk`
  - 本地临时路径：`/tmp/openclaw-adbkeyboard/keyboardservice-debug.apk`
  - SHA-256：`41a8a0996d7397a2390d1ca16a75cb66c4a7bdaa89cf4e63600a4d3fb346fbbb`
- 已在当前 Android 16 真机上安装、启用并切换测试 IME。
- 已通过 `ADB_INPUT_B64` 向 OpenClaw Android 产品学习页的产品名称输入框注入中文 `工厂设备巡检助手`。
- 已用 UIAutomator dump 确认中文文本进入目标输入框。
- 已恢复原输入法并卸载测试 IME。
- 已更新 `docs/how-to/debug/android-chinese-input-smoke.md`。

---

## 12. 本次定稿边界

- 本次只解决真机 smoke 的中文自动化输入通道。
- 不改 Android 产品代码、不改 backend、不新增产品依赖。
- 测试 IME APK 不进入 Git，只保留来源和校验信息。

---

## 13. 已做验证

已完成：

1. `adb devices`
   - 结果：检测到真机 `f3b59f04`。
2. `adb shell getprop ro.build.version.release`
   - 结果：`16`。
3. `adb shell getprop ro.build.version.sdk`
   - 结果：`36`。
4. `adb shell settings get secure default_input_method`
   - 验证前：`com.baidu.input_oppo/.ImeService`。
   - 切换测试 IME 后：`com.android.adbkeyboard/.AdbIME`。
   - 恢复后：`com.baidu.input_oppo/.ImeService`。
5. `adb shell pm install -r /data/local/tmp/openclaw-adbkeyboard.apk`
   - 结果：`Success`。
6. `adb shell am broadcast -a ADB_INPUT_B64 --es msg "$MSG_B64"`
   - 结果：broadcast `result=0`。
7. `adb exec-out cat /sdcard/window.xml | rg "工厂设备巡检助手"`
   - 结果：UIAutomator XML 中出现 `text="工厂设备巡检助手"`。
8. `adb uninstall com.android.adbkeyboard`
   - 结果：`Success`。

---

## 14. 实际结果说明

当前设备的中文自动化输入问题已解决：后续真机 smoke 需要中文样例时，可以临时使用 `senzhk/ADBKeyBoard` v2.5-dev，通过 `ADB_INPUT_B64` 注入中文，并在测试结束后恢复原输入法、卸载测试 IME。

执行中发现 `adb install -r /tmp/openclaw-adbkeyboard/keyboardservice-debug.apk` 曾长时间无返回；本次实际成功路径是先 `adb push` 到 `/data/local/tmp/`，再执行 `adb shell pm install -r`。
