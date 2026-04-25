# 阶段性交接：Android Chinese Input Device Preflight

更新时间：2026-04-25

## 1. 本次改了什么

- 完成 `task_android_chinese_input_device_preflight.md`。
- 将当前真机准备为中文 smoke ready 状态。
- 未修改 Android 产品代码或 backend。
- 未卸载 `com.android.adbkeyboard`，作为后续 smoke 的预装测试工具保留。

---

## 2. 为什么这么定

- OnePlus / OPlus 未知来源输入法安装可能触发安全页和拼图验证，不能作为稳定自动化步骤。
- 设备预检后，日常 smoke 只需要切换 IME，不再重复安装和卸载测试输入法。

---

## 3. 本次验证了什么

1. `adb devices`
   - 检测到真机 `f3b59f04`。
2. 安装状态
   - `adb shell pm install -r /data/local/tmp/openclaw-adbkeyboard.apk` 返回 `Success`。
   - `adb shell pm list packages com.android.adbkeyboard` 返回 `package:com.android.adbkeyboard`。
3. IME 状态
   - `adb shell ime enable com.android.adbkeyboard/.AdbIME` 成功。
   - `adb shell ime set com.android.adbkeyboard/.AdbIME` 成功。
   - 切换后默认输入法为 `com.android.adbkeyboard/.AdbIME`。
4. 中文输入
   - 通过 `ADB_INPUT_B64` 输入 `工厂设备巡检助手`。
   - UIAutomator XML 中确认出现 `text="工厂设备巡检助手"`。
5. 恢复
   - 默认输入法已恢复为 `com.baidu.input_oppo/.ImeService`。
   - `com.android.adbkeyboard` 保留安装。

---

## 4. 已知限制

- 该预检只适用于当前 jianglab 真机。
- 如果设备重置、测试 IME 被卸载或系统策略变化，需要重新执行预检。
- 测试 IME 是设备测试工具，不是产品依赖。

---

## 5. 推荐下一步

1. 恢复 `task_v1_product_learning_ui_polish_real_chinese_smoke.md` 的真实中文 create / enrich smoke。
2. 日常 smoke 结束只恢复原输入法，不卸载 `com.android.adbkeyboard`。
