# Task：Android Chinese Input Device Preflight

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：Android Chinese Input Device Preflight
- 建议路径：`docs/delivery/tasks/task_android_chinese_input_device_preflight.md`
- 当前状态：`planned`
- 优先级：P1

本任务用于把 jianglab 当前真机准备成“中文 smoke ready”状态，避免每次 smoke 都重新安装测试 IME 并触发 OnePlus / OPlus 未知来源安全验证。

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：
  1. 恢复 `task_v1_product_learning_ui_polish_real_chinese_smoke.md` 的真实中文 smoke。
- 停止条件：
  - 设备安全策略禁止安装或保留测试 IME。
  - 需要绕过、破解或自动化厂商拼图验证码。

---

## 2. 任务目标

一次性完成当前设备上的 `ADBKeyBoard` 安装和可用性验证。完成后，日常 smoke 只切换 IME、输入中文、恢复原输入法，不再卸载测试 IME。

---

## 3. 当前背景

`task_v1_product_learning_ui_polish_real_chinese_smoke.md` 执行真实中文 smoke 时，重新安装 `ADBKeyBoard` 触发 OnePlus / OPlus 未知来源安全页与拼图验证，无法稳定自动化通过。

这属于设备安全策略，不是 OpenClaw Android UI 或 backend 逻辑问题。

---

## 4. 范围

本任务 In Scope：

- 人工一次性完成测试 IME 安装确认。
- 验证 `com.android.adbkeyboard` 已安装并出现在 IME 列表。
- 验证 `ADB_INPUT_B64` 能输入 `工厂设备巡检助手`。
- 恢复默认输入法。
- 更新 runbook / handoff。

本任务 Out of Scope：

- 不自动破解厂商拼图验证。
- 不修改 Android 产品代码。
- 不修改 backend。
- 不把测试 APK 提交到 Git。

---

## 5. 涉及文件

高概率涉及：

- `docs/how-to/debug/android-chinese-input-smoke.md`
- `docs/delivery/tasks/task_android_chinese_input_device_preflight.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/handoffs/handoff_2026_04_25_android_chinese_input_device_preflight.md`

---

## 6. 产出要求

至少应产出：

1. 设备预检结果。
2. 测试 IME 安装和切换验证。
3. 日常 smoke 不卸载测试 IME 的新规则。
4. handoff。

---

## 7. 验收标准

满足以下条件可认为完成：

1. `adb devices` 检测到真机。
2. `adb shell pm list packages com.android.adbkeyboard` 输出 `package:com.android.adbkeyboard`。
3. `adb shell ime list -s` 输出 `com.android.adbkeyboard/.AdbIME`。
4. 可切换到 `com.android.adbkeyboard/.AdbIME`。
5. `ADB_INPUT_B64` 可输入 `工厂设备巡检助手`。
6. smoke 结束后默认输入法恢复为 `com.baidu.input_oppo/.ImeService`。
7. 不卸载 `com.android.adbkeyboard`。

---

## 8. 推荐执行顺序

建议执行顺序：

1. 检查设备和当前默认输入法。
2. 如测试 IME 未安装，按 runbook 下载并推送 APK。
3. 在真机上人工完成 OPlus 安全确认和拼图验证。
4. 验证测试 IME 出现在包列表与 IME 列表。
5. 切换测试 IME，执行 `ADB_INPUT_B64` 输入中文。
6. 恢复原输入法，但不卸载测试 IME。
7. 更新 handoff。

---

## 9. 风险与注意事项

- 厂商拼图验证不能作为自动化步骤。
- 测试 IME 只允许保留在 jianglab 当前测试设备，不进入产品依赖。
- 如果设备策略不允许保留测试 IME，后续应改走 instrumentation / Compose UI test 方案。

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. 恢复 `task_v1_product_learning_ui_polish_real_chinese_smoke.md` 的真实中文 create / enrich smoke。

---

## 11. 实际产出

任务执行完成后补充。

---

## 12. 本次定稿边界

任务执行完成后补充。

---

## 13. 已做验证

任务执行完成后补充。

---

## 14. 实际结果说明

任务执行完成后补充。
